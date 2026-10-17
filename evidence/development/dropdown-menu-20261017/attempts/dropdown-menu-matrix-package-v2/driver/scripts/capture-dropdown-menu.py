#!/usr/bin/env python3
"""Capture every native dropdown context and preserve complete caller observations."""
import argparse
import concurrent.futures
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
PROJECTION = ROOT / 'tests/consumer/native-dropdown-menu-witnesses.json'
CONTEXTS = list(itertools.product(['light', 'dark'], [1, 1.5], [1, 2]))


def prefix(appearance, scale, dpr):
    return f'{appearance}-text{scale:g}-dpr{dpr:g}'


def rows(projection=None):
    data = projection if projection is not None else json.loads(PROJECTION.read_text())
    assert data['reference'] == REFERENCE and data['accepted'] is False
    assert len(data['closed']) == len(data['sizing']) == 256
    result = []
    for row in data['closed']:
        context = prefix(row['appearance'], row['textScale'], row['dpr'])
        result.append(dict(row, context=context, path=context + '-' + row['configuration']['id'] + '.png'))
    assert len(result) == len({row['path'] for row in result}) == 256
    assert all(sum(row['context'] == prefix(*context) for row in result) == 32 for context in CONTEXTS)
    assert all((ROOT / row['reference']).is_file() for row in result)
    return result


def definitions(projection=None):
    data = projection if projection is not None else json.loads(PROJECTION.read_text())
    fixtures = {}
    for row in data['closed']:
        value = dict(api='BleeckerDropdownMenu', source=REFERENCE,
            fixture='dropdown-menu-' + row['configuration']['id'], width=600, height=300,
            configuration=row['configuration'])
        if value['fixture'] in fixtures:
            assert fixtures[value['fixture']] == value
        fixtures[value['fixture']] = value
    assert len(fixtures) == 32
    return dict(source=REFERENCE, accepted=False, fixtures=list(fixtures.values()))


def observations(expected, actual):
    errors = {}
    for key in ['configuration', 'appearance', 'textScale', 'dpr', 'title', 'enabled']:
        if expected.get(key) != actual.get(key):
            errors[key] = dict(reference=expected.get(key), candidate=actual.get(key))
    if actual.get('actions') != expected['calls']:
        errors['actions'] = dict(reference=expected['calls'], candidate=actual.get('actions'))
    if actual.get('labelActions') != 0:
        errors['labelActions'] = actual.get('labelActions')
    frames = actual.get('frames', {})
    return dict(nativeFrameStatus='passed' if frames == expected['frames'] else 'failed',
        bodyCallerFrameStatus='passed' if all(frames.get(key) == expected['frames'][key] for key in ['body', 'caller']) else 'failed',
        stateStatus='failed' if errors else 'passed', stateErrors=errors,
        referenceFrame=expected['frames'], candidateFrame=frames)


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
        command = [str(consumer), '--dropdown-menu', '--dropdown-menu-observe', '--text-scale', str(scale),
            '--dropdown-menu-report', str(output / name)]
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
        assert report['structuralChecks'] == 'passed' and report['images'] == 32 and report['accepted'] is False
        assert report['pointerDeliveries'] == 11 and report['keyDeliveries'] == 1 and len(report['actions']) == 6
        actual = {name + '-' + row['configuration']['id'] + '.png': dict(row, **row['state'], appearance=appearance, textScale=scale)
            for row in report['closed']}
        expected_rows = [row for row in corpus if row['context'] == name]
        assert set(actual) == {row['path'] for row in expected_rows}
        for expected in expected_rows:
            path = expected['path']
            actual[path].update(dpr=dpr, reference=expected['reference'], source=REFERENCE, accepted=False)
            assert actual[path]['configuration'] == expected['configuration']
            assert struct.unpack('>II', (output / path).read_bytes()[16:24]) == (600 * dpr, 300 * dpr)
            (output / (path + '.json')).write_text(json.dumps(actual[path], ensure_ascii=False, indent=2) + '\n')
        return dict(context=name, cases=32, exitCode=result.returncode)

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        receipts = list(pool.map(one, CONTEXTS))
    (output / 'capture.json').write_text(json.dumps(dict(reference=REFERENCE, accepted=False, rows=receipts, images=256), indent=2) + '\n')
    return receipts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('consumer', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--jobs', type=int, default=1)
    args = parser.parse_args()
    assert args.jobs >= 1
    print(json.dumps(capture(args.consumer, args.output, args.jobs), indent=2))
