#!/usr/bin/env python3
"""Project public native images, literal frame witnesses and owner traces."""
import argparse
import hashlib
import importlib.util
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/app-tabs-20261017'
TARGET = ROOT / 'tests/consumer/native-app-tabs-witnesses.json'
ICON_TARGET = ROOT / 'tests/consumer/native-app-tab-icon-metrics.json'
spec = importlib.util.spec_from_file_location('app_tabs_source', ROOT / 'scripts/verify-app-tabs-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


def project():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    source.verify()

    def observation(row, prefix, configuration):
        public, probed, literal = row['states']
        state = dict(literal, configuration=configuration)
        frames = source.active_frames(state)
        assert all(frames[k] == probed['frames'][k] for k in ['bar', 'caller'])
        return dict(configuration=configuration, selection=public['selection'],
            requests=public['requests'], pending=public['pending'], lifecycle=public['lifecycle'],
            frames=frames, reference=str((DIRECTORY / prefix / row['paths'][0]).relative_to(ROOT)))

    closed = []
    for row in read('output/captures.json')['rows']:
        closed.append(dict(observation(row, 'output', row['configuration']), appearance=row['appearance'],
            textScale=row['textScale'], dpr=row['dpr']))
    histories = []
    for row in read('history-output/histories.json')['histories']:
        steps = []
        for step in row['steps']:
            public = step['states'][0]
            steps.append(dict(observation(step, 'history-output', public['configuration']),
                step=step['step'], appearance=public['appearance'], textScale=public['textScale'],
                matchesInitialPixels=step['matchesInitialPixels'], actions=step['actions']))
        histories.append(dict(configuration=row['configuration'], appearance=row['appearance'],
            textScale=row['textScale'], dpr=row['dpr'], steps=steps))
    sizing = []
    for row in read('sizing-output/sizing.json')['rows']:
        sizing.append(dict(configuration=row['configuration'], appearance=row['appearance'],
            textScale=row['textScale'], dpr=row['dpr'], public=row['modes'][0]['proposals'],
            witnesses=[m['proposals'] for m in row['modes'][1:]]))
    return dict(reference=source.REFERENCE, accepted=False,
        sourceSha256=hashlib.sha256((DIRECTORY / 'investigation.json').read_bytes()).hexdigest(),
        nativeAccessibilityObserved=False, closed=closed, histories=histories, sizing=sizing)


def icon_metrics(projection):
    records = {}
    def collect(row, dpr):
        for index, tab in enumerate(row['configuration']['tabs']):
            frame = row['frames']['icon-' + str(index)]
            selected = unicodedata.normalize('NFD', tab['value']) == unicodedata.normalize('NFD', row['selection'])
            key = (tab['systemImage'], selected, dpr)
            value = dict(width=frame['width'], height=frame['height'])
            if key in records:
                assert records[key] == value, 'Native icon dimensions vary beyond this fixture adapter'
            records[key] = value
    for row in projection['closed']:
        collect(row, row['dpr'])
    for history in projection['histories']:
        for step in history['steps']:
            collect(step, history['dpr'])
    return dict(reference=projection['reference'], accepted=False,
        rows=[dict(symbol=symbol, selected=selected, dpr=dpr, **value)
            for (symbol, selected, dpr), value in sorted(records.items())])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    projection = project()
    value = json.dumps(projection, ensure_ascii=False, indent=2) + '\n'
    icons = json.dumps(icon_metrics(projection), indent=2) + '\n'
    if args.check:
        assert TARGET.read_text() == value, 'Native tab-bar projection drift'
        assert ICON_TARGET.read_text() == icons, 'Native tab-bar icon metric projection drift'
        print('App tab bar witnesses match the sealed public/native observations; acceptance pending')
    else:
        assert not TARGET.exists(), 'Preserve the existing projection; review changes explicitly'
        assert not ICON_TARGET.exists(), 'Preserve the existing icon metric projection'
        TARGET.write_text(value)
        ICON_TARGET.write_text(icons)


if __name__ == '__main__':
    main()
