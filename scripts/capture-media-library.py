#!/usr/bin/env python3
"""Capture the complete MediaLibrary corpus, retained histories and fatal inputs."""
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

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
PROJECTION = ROOT / 'tests/consumer/native-media-library-witnesses.json'
CONTEXTS = list(itertools.product(['light', 'dark'], [1, 1.5], [1, 2]))
STEPS = ['initial', 'value-update', 'reorder', 'insert', 'remove', 'minimum-width', 'size',
    'appearance', 'text-scale', 'direction', 'disabled', 'disabled-click', 'empty', 'restore',
    'zero-width', 'width-restored', 'scroll-bottom', 'scroll-top', 'wait-0.2', 'wait-1.0', 'click-first']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def prefix(appearance, scale, dpr):
    return f'{appearance}-text{scale:g}-dpr{dpr:g}'

def rows(projection=None):
    data = projection if projection is not None else json.loads(PROJECTION.read_text())
    assert data['reference'] == REFERENCE and data['accepted'] is False
    assert [len(data[k]) for k in ['closed', 'edges', 'histories', 'sizing']] == [496, 112, 48, 496]
    result = []
    for kind in ['closed', 'edges']:
        for row in data[kind]:
            if row.get('nativeExitCode', 0):
                continue
            context = prefix(row['appearance'], row['textScale'], row['dpr'])
            result.append(dict(row, kind='edge' if kind == 'edges' else 'closed', context=context,
                path=context + '-' + ('edge-' if kind == 'edges' else '') + row['configuration']['id'] + '.png'))
    for row in data['histories']:
        context = prefix(row['appearance'], row['textScale'], row['dpr'])
        assert [s['step'] for s in row['steps']] == STEPS
        for index, step in enumerate(row['steps']):
            result.append(dict(step, kind='history', context=context, dpr=row['dpr'],
                path=f'{context}-{row["configuration"]["id"]}-history-step{index}.png'))
    assert len(result) == len({r['path'] for r in result}) == 1608
    assert all(sum(r['context'] == prefix(*c) for r in result) == 201 for c in CONTEXTS)
    assert all((ROOT / r['reference']).is_file() for r in result)
    return result

def observations(expected, actual):
    errors = {}
    for key in ['configuration', 'appearance', 'textScale', 'dpr', 'kind']:
        if actual.get(key) != expected[key]:
            errors[key] = dict(reference=expected[key], candidate=actual.get(key))
    state = actual.get('lifecycle', {})
    if any(state.get(k) != v for k, v in dict(appearances=1, disappearances=0, wrapperInstances=1).items()):
        errors['wrapperState'] = state
    if expected['kind'] == 'history':
        if actual.get('step') != expected['step']:
            errors['step'] = actual.get('step')
    return dict(retainedRasterStatus='failed' if expected['kind']=='history' and expected['step']=='restore' and actual.get('matchesInitialPixels') is not True else 'passed', nativeFrameStatus='passed' if actual.get('frame') == expected['frame'] else 'failed',
        nativeLifecycleStatus='passed' if state == expected['lifecycle'] else 'failed',
        stateStatus='failed' if errors else 'passed', stateErrors=errors,
        referenceFrame=expected['frame'], candidateFrame=actual.get('frame'),
        referenceLifecycle=expected['lifecycle'], candidateLifecycle=state)

def capture(consumer, output, jobs=1):
    consumer, output = Path(consumer).resolve(), Path(output).resolve()
    assert consumer.is_file() and not output.exists(), 'Use a fresh directory; preserve earlier attempts'
    corpus = rows()
    output.mkdir(parents=True)
    def one(context):
        appearance, scale, dpr = context
        name = prefix(*context)
        target = output / name
        environment = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
            QT_SCALE_FACTOR=str(dpr), LANG='C.UTF-8')
        for key in ['QML_IMPORT_PATH', 'QML2_IMPORT_PATH']:
            environment.pop(key, None)
        command = [str(consumer), '--media-library', '--media-library-observe', '--text-scale', str(scale),
            '--media-library-report', str(target)]
        if appearance == 'dark':
            command.append('--dark')
        def process(arguments, suffix):
            start = time.monotonic()
            log = name + suffix + '.log'
            with (output / log).open('w') as stream:
                result = subprocess.run(arguments, cwd=consumer.parent, env=environment, stdout=stream, stderr=subprocess.STDOUT)
            receipt = dict(command=arguments, exitCode=result.returncode, seconds=time.monotonic()-start, log=log)
            (output / (name + suffix + '-process.json')).write_text(json.dumps(receipt, indent=2) + '\n')
            return receipt
        receipt = process(command, '')
        assert receipt['exitCode'] == 0, (name, receipt)
        log = (output / receipt['log']).read_text()
        assert not any(word in log for word in ['Unable to assign', 'ReferenceError', 'TypeError', 'Error:',
            'QFont::', 'Binding loop', 'Could not find any constructor']), log[-4000:]
        report = json.loads(Path(str(target) + '.json').read_text())
        assert report['qt'] == '6.8.3' and report['platform'] == 'offscreen' and report['dpr'] == dpr
        assert report['width'] == 640 and report['height'] == 400 and report['structuralChecks'] == 'passed'
        assert report['accepted'] is False and report['images'] == report['geometryObservations'] == 201
        assert report['pointerDeliveries'] == 12 and len(report['sizing']) == 62
        assert all(r['actual'] is None and r['status'].startswith('unobserved') for r in report['sizing'])
        actual = {}
        for kind, key in [('closed', 'closed'), ('edge', 'edges')]:
            for row in report[key]:
                if row.get('nativeExitCode', 0):
                    continue
                path = name + '-' + ('edge-' if kind == 'edge' else '') + row['configuration']['id'] + '.png'
                assert path not in actual
                actual[path] = dict(row, appearance=appearance, textScale=scale, kind=kind)
        for history in report['histories']:
            assert [s['step'] for s in history['steps']] == STEPS
            for index, step in enumerate(history['steps']):
                path = f'{name}-{history["configuration"]["id"]}-history-step{index}.png'
                assert path not in actual
                actual[path] = dict(step, kind='history')
        expected = {r['path']: r for r in corpus if r['context'] == name}
        assert actual.keys() == expected.keys() and len(actual) == 201
        records = []
        for path, value in actual.items():
            value.update(qt=report['qt'], platform=report['platform'], width=640, height=400, dpr=dpr,
                api='BleeckerMediaLibrary', fixture=path, source=REFERENCE, accepted=False)
            observation = observations(expected[path], value)
            assert observation['stateStatus'] == 'passed', (path, observation['stateErrors'])
            image = output / path
            assert struct.unpack('>II', image.read_bytes()[16:24]) == (640*dpr, 400*dpr)
            metadata = output / (path + '.json')
            metadata.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
            records.append(dict(path=path, sha256=digest(image), metadataSha256=digest(metadata)))
        fatal_command = [str(consumer), '--media-library', '--media-library-fatal', '--text-scale', str(scale)]
        if appearance == 'dark':
            fatal_command.append('--dark')
        fatal = process(fatal_command, '-fatal')
        assert fatal['exitCode'] in [-6, 134] and 'minimumTileWidth -16' in (output / fatal['log']).read_text(), fatal
        print(f'MediaLibrary {name}: 201 displayed observations and one isolated fatal input', flush=True)
        return dict(context=name, process=receipt, fatalProcess=fatal, records=records)
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        contexts = list(pool.map(one, CONTEXTS))
    assert sum(len(r['records']) for r in contexts) == 1608
    report = dict(reference=REFERENCE, accepted=False, cases=1608, closedContexts=496,
        successfulEdgeContexts=104, fatalEdgeContexts=8, histories=48, historySteps=1008, contexts=contexts,
        consumerSha256=digest(consumer), projectionSha256=digest(PROJECTION),
        scope='Every native closed/edge input and all 21 retained-history steps. Direct sizing remains unobserved and native acceptance pending.')
    (output / 'capture-results.json').write_text(json.dumps(report, indent=2) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('consumer', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--jobs', type=int, choices=range(1, 9), default=1)
    args = parser.parse_args()
    capture(args.consumer, args.output, args.jobs)
