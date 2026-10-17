#!/usr/bin/env python3
"""Capture every native desktop app-tab context and retained binding step."""
import argparse
import concurrent.futures
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
import time
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
PROJECTION = ROOT / 'tests/consumer/native-app-tabs-witnesses.json'
CONTEXTS = list(itertools.product(['light', 'dark'], [1, 1.5], [1, 2]))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prefix(appearance, scale, dpr):
    return f'{appearance}-text{scale:g}-dpr{dpr:g}'


def selected_values(row):
    selection = unicodedata.normalize('NFD', row['selection'])
    return [tab['value'] for tab in row['configuration']['tabs']
        if unicodedata.normalize('NFD', tab['value']) == selection]


def rows(projection=None):
    data = projection if projection is not None else json.loads(PROJECTION.read_text())
    assert data['reference'] == REFERENCE and data['accepted'] is False
    assert [len(data[k]) for k in ['closed', 'histories', 'sizing']] == [344, 48, 344]
    result = []
    for row in data['closed']:
        context = prefix(row['appearance'], row['textScale'], row['dpr'])
        result.append(dict(row, selectedValues=selected_values(row), kind='closed', context=context,
            path=context + '-' + row['configuration']['id'] + '.png'))
    for history in data['histories']:
        assert len(history['steps']) == 18
        context = prefix(history['appearance'], history['textScale'], history['dpr'])
        for index, step in enumerate(history['steps']):
            result.append(dict(step, selectedValues=selected_values(step), kind='history', context=context, dpr=history['dpr'],
                path=f'{context}-{history["configuration"]["id"]}-history-step{index}.png'))
    assert len(result) == len({r['path'] for r in result}) == 1208
    assert all(sum(r['context'] == prefix(*c) for r in result) == 151 for c in CONTEXTS)
    assert all((ROOT / r['reference']).is_file() for r in result)
    return result


def definitions(projection=None):
    data = projection if projection is not None else json.loads(PROJECTION.read_text())
    fixtures = {}
    for row in data['closed']:
        source = row['configuration']
        value = {k: v for k, v in source.items() if k not in ['width', 'height']}
        value.update(api='BleeckerAppTabBar', source=REFERENCE, fixture='app-tabs-' + source['id'],
            width=640, height=400, tabWidth=source['width'], tabHeight=source.get('height'))
        if source['id'] in fixtures:
            assert fixtures[source['id']] == value
        fixtures[source['id']] = value
    assert len(fixtures) == 43
    return dict(source=REFERENCE, accepted=False, fixtures=list(fixtures.values()))


def observations(expected, actual):
    errors = {}
    for key in ['configuration', 'appearance', 'textScale', 'dpr', 'kind', 'selection', 'selectedValues', 'requests', 'pending', 'lifecycle']:
        if actual.get(key) != expected.get(key):
            errors[key] = dict(reference=expected.get(key), candidate=actual.get(key))
    if expected['kind'] == 'history' and actual.get('step') != expected['step']:
        errors['step'] = actual.get('step')
    return dict(nativeFrameStatus='passed' if actual.get('frames') == expected['frames'] else 'failed',
        stateStatus='failed' if errors else 'passed', stateErrors=errors,
        retainedRasterStatus='failed' if expected['kind'] == 'history' and expected['step'] == 'restore'
            and actual.get('matchesInitialPixels') is not True else 'passed',
        referenceFrame=expected['frames'], candidateFrame=actual.get('frames'))


def capture(consumer, output, jobs=1):
    consumer, output = Path(consumer).resolve(), Path(output).resolve()
    assert consumer.is_file() and not output.exists(), 'Use a fresh directory; preserve earlier attempts'
    corpus = rows()
    output.mkdir(parents=True)

    def one(context):
        appearance, scale, dpr = context
        name = prefix(*context)
        environment = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
            QT_SCALE_FACTOR=str(dpr), LANG='C.UTF-8')
        for key in ['QML_IMPORT_PATH', 'QML2_IMPORT_PATH']:
            environment.pop(key, None)
        command = [str(consumer), '--app-tabs', '--app-tabs-observe', '--text-scale', str(scale),
            '--app-tabs-report', str(output / name)]
        if appearance == 'dark':
            command.append('--dark')
        started = time.monotonic()
        with (output / (name + '.log')).open('w') as log:
            result = subprocess.run(command, cwd=consumer.parent, env=environment, stdout=log, stderr=subprocess.STDOUT)
        receipt = dict(command=command, exitCode=result.returncode, seconds=time.monotonic() - started, log=name + '.log')
        (output / (name + '-process.json')).write_text(json.dumps(receipt, indent=2) + '\n')
        assert result.returncode == 0, (name, receipt)
        log = (output / receipt['log']).read_text()
        assert not any(word in log for word in ['TypeError', 'ReferenceError', 'Binding loop', 'Invalid state', 'unavailable'])
        report = json.loads((output / (name + '.json')).read_text())
        assert report['structuralChecks'] == 'passed' and report['images'] == 151
        assert report['pointerDeliveries'] == 24 and report['accepted'] is False
        actual = {}
        for row in report['closed']:
            path = name + '-' + row['configuration']['id'] + '.png'
            actual[path] = dict(row, appearance=appearance, textScale=scale, kind='closed')
        for history in report['histories']:
            for index, step in enumerate(history['steps']):
                path = f'{name}-{history["configuration"]["id"]}-history-step{index}.png'
                actual[path] = dict(step, kind='history')
        expected_rows = [r for r in corpus if r['context'] == name]
        assert set(actual) == {r['path'] for r in expected_rows}
        for expected in expected_rows:
            path = expected['path']
            actual[path].update(dpr=dpr, reference=expected['reference'], source=REFERENCE, accepted=False)
            assert actual[path]['configuration'] == expected['configuration']
            assert struct.unpack('>II', (output / path).read_bytes()[16:24]) == (640 * dpr, 400 * dpr)
            (output / (path + '.json')).write_text(json.dumps(actual[path], ensure_ascii=False, indent=2) + '\n')
        return dict(context=name, cases=151, exitCode=result.returncode)

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        receipts = list(pool.map(one, CONTEXTS))
    (output / 'capture.json').write_text(json.dumps(dict(reference=REFERENCE, accepted=False,
        rows=receipts, images=1208), indent=2) + '\n')
    return receipts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('consumer', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--jobs', type=int, default=1)
    args = parser.parse_args()
    assert args.jobs >= 1
    print(json.dumps(capture(args.consumer, args.output, args.jobs), indent=2))


if __name__ == '__main__':
    main()
