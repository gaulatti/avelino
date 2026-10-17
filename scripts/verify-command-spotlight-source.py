#!/usr/bin/env python3
"""Audit pinned native spotlight observations without accepting Linux parity."""
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path, PurePosixPath
import struct
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/command-spotlight-20261017'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
TREE = 'db61113381a51fc3c7b3d12786609cd9e76627c8'
CONTEXTS = set(itertools.product(['light', 'dark'], [1, 1.5], [1, 2]))
STEPS = ['initial', 'click-first', 'click-first-again', 'external-query', 'key-query',
    'flush-owner', 'blur-query', 'clear-query', 'flush-clear', 'identity-update',
    'reorder', 'labels', 'disable', 'disabled-click', 'disabled-key', 'enable',
    'scroll-bottom', 'scroll-top', 'appearance', 'text-scale', 'direction', 'empty',
    'restore', 'click-first-restored']
GATES = ['LinuxImplementation', 'systemSearchSymbolsFontsAndRaster', 'LinuxSizing',
    'nativeGenericIdentityAndBuilderTiming', 'nativeLazyRowRetentionAndMeasurement',
    'nativeInputTiming', 'nativeAccessibility', 'physicalDisplaysInput', 'readers',
    'independentMachineReplayAvailability']
STATE_KEYS = ['query', 'requests', 'pending', 'rowCounts', 'rowInstances', 'rowAppearances',
    'rowDisappearances', 'appearedKeys', 'controls', 'lifecycle', 'hostFlipped',
    'firstResponderClass', 'windowVisible', 'windowKey', 'applicationActive', 'backingDpr']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(name):
    path = PurePosixPath(name)
    assert str(path) == name and not path.is_absolute() and '..' not in path.parts
    return path


def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [clean(item) for item in value]
    return value


def context(row):
    return row['appearance'], row['textScale'], row['dpr']


def validate_report(report):
    assert report['reference'] == REFERENCE and report['tree'] == TREE
    assert report['accepted'] is False and report['expectedImagesChanged'] is False
    assert report['status'] == 'source-investigation; Linux implementation pending'
    assert report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    assert report['remainingAcceptance'] == GATES
    assert report['sourceOnlyArtifact']['containsPinnedSourceFiles'] == 89
    assert report['sourceOnlyArtifact']['downloadAvailability'] == 'pending independent-machine replay'
    assert report['sourceReplayStatus'] in ['passed', 'failed']
    for key, value in dict(fixtures=32, closedContexts=256, closedImages=768,
            closedPixelWitnessMatches=256, closedGeometryWitnessMatches=256,
            closedNativeControlWitnessMatches=256,
            historyDefinitions=8, histories=64, historySteps=1536, historyImages=4608,
            historyPixelWitnessMatches=1536, historyStateWitnessMatches=1536,
            historyGeometryWitnessMatches=1536, retainedRestores=64, retainedRestorePixelMatches=56,
            sizingContexts=256, sizingQueriesPerBranch=3840, sizingBranchQueries=11520,
            clearTargets=16, publicKeyAttempts=128, publicEditableKeyDeliveries=64,
            publicDisabledKeyEditorUnavailable=64, publicClearPointers=64).items():
        assert report['summary'][key] == value, key


def state(value):
    assert value['windowVisible'] is True and value['windowKey'] is False
    assert value['applicationActive'] is False and value['backingDpr'] == 2
    assert value['hostFlipped'] is True
    assert value['lifecycle'] == dict(appearances=1, disappearances=0, wrapperInstances=1)
    for frame in value['frames'].values():
        assert set(frame) == {'x', 'y', 'width', 'height'}
        assert all(type(n) in [int, float] and math.isfinite(n) for n in frame.values())
        assert frame['width'] >= 0 and frame['height'] >= 0


def frame_witness(states):
    first, last = states[1]['frames'], states[2]['frames']
    return set(first) <= set(last) and all(first[key] == last[key] for key in first)


def observations(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    fixtures = read('fixtures.json')
    definitions = {row['id']: row for row in fixtures}
    assert len(fixtures) == len(definitions) == 32
    assert {row['valueKind'] for row in fixtures} == {'string', 'integer', 'boolean', 'record'}
    images = set()
    totals = dict(fixtures=32, closedContexts=0, closedImages=0, closedPixelWitnessMatches=0,
        closedGeometryWitnessMatches=0, closedNativeControlWitnessMatches=0,
        historyDefinitions=8, histories=0, historySteps=0, historyImages=0,
        historyPixelWitnessMatches=0, historyStateWitnessMatches=0,
        historyGeometryWitnessMatches=0, retainedRestores=0, retainedRestorePixelMatches=0,
        sizingContexts=0, sizingQueriesPerBranch=0, sizingBranchQueries=0,
        clearTargets=16, publicKeyAttempts=0, publicEditableKeyDeliveries=0,
        publicDisabledKeyEditorUnavailable=0, publicClearPointers=0)

    def pixels(prefix, row):
        encoded = []
        assert len(row['paths']) == len(row['states']) == 3
        for path in row['paths']:
            relative = prefix + '/' + path
            safe(relative)
            assert relative not in images
            images.add(relative)
            data = (directory / relative).read_bytes()
            assert data.startswith(b'\x89PNG\r\n\x1a\n')
            assert struct.unpack('!II', data[16:24]) == (720*row['dpr'], 520*row['dpr'])
            encoded.append(data)
        assert row['publicProbedIdentical'] is (encoded[0] == encoded[1])
        assert row['publicLiteralIdentical'] is (encoded[0] == encoded[2])
        for value in row['states']:
            state(value)
        return encoded, encoded[0] == encoded[1] == encoded[2]

    closed = read('output/captures.json')
    assert closed['reference'] == REFERENCE and closed['accepted'] is False
    seen = set()
    for row in closed['rows']:
        key = row['configuration']['id'], context(row)
        assert key not in seen and key[1] in CONTEXTS
        seen.add(key)
        assert row['configuration'] == clean(definitions[key[0]])
        encoded, identical = pixels('output', row)
        totals['closedContexts'] += 1
        totals['closedImages'] += 3
        totals['closedPixelWitnessMatches'] += identical
        totals['closedGeometryWitnessMatches'] += frame_witness(row['states'])
        totals['closedNativeControlWitnessMatches'] += all(row['states'][0]['controls'] == s['controls'] for s in row['states'][1:])
        frames = row['states'][2]['frames']
        assert frames['body'] == dict(x=100, y=70, width=520, height=380)
        height = 40*row['textScale']
        assert frames['search'] == dict(x=112, y=82, width=496, height=height)
        assert frames['header'] == dict(x=100, y=70, width=520, height=height+24)
        assert frames['scroll'] == dict(x=100, y=95+height, width=520, height=355-height)
        for current in row['states']:
            assert current['query'] == row['configuration']['query'] and current['requests'] == []
    assert seen == set(itertools.product(definitions, CONTEXTS))

    source_histories = read('histories.json') + read('supplementary-histories.json')
    hist_defs = {row['id']: row for row in source_histories}
    assert len(source_histories) == len(hist_defs) == 8
    seen = set()
    for prefix in ['history-output', 'supplementary-history-output']:
        data = read(prefix + '/histories.json')
        assert data['reference'] == REFERENCE and data['accepted'] is False
        for history in data['histories']:
            key = history['configuration']['id'], context(history)
            assert key not in seen and key[1] in CONTEXTS
            seen.add(key)
            assert history['configuration'] == clean(hist_defs[key[0]])
            assert [r['step'] for r in history['steps']] == STEPS
            initial = None
            for index, row in enumerate(history['steps']):
                encoded, identical = pixels(prefix, dict(row, dpr=history['dpr']))
                if initial is None:
                    initial = encoded
                assert row['matchesInitialPixels'] is (encoded == initial)
                totals['historySteps'] += 1
                totals['historyImages'] += 3
                totals['historyPixelWitnessMatches'] += identical
                totals['historyStateWitnessMatches'] += all(
                    all(row['states'][0][name] == other[name] for name in STATE_KEYS)
                    for other in row['states'][1:])
                totals['historyGeometryWitnessMatches'] += frame_witness(row['states'])
                public = row['states'][0]
                if row['step'] in ['key-query', 'disabled-key']:
                    totals['publicKeyAttempts'] += 1
                    action = row['actions'][0][0]
                    assert action['method'] == 'NSWindow.sendEvent keyDown/keyUp'
                    if row['step'] == 'key-query':
                        totals['publicEditableKeyDeliveries'] += action['available'] is True
                        assert action['fieldEnabled'] is True
                    else:
                        totals['publicDisabledKeyEditorUnavailable'] += action['available'] is False
                        assert action['fieldEnabled'] is False
                        previous = history['steps'][index-1]['states'][0]
                        assert public['query'] == previous['query'] and public['requests'] == previous['requests']
                if row['step'] == 'clear-query':
                    totals['publicClearPointers'] += 1
                    assert row['actions'][0][0]['kind'] == 'clearPointer'
                    assert '' in public['requests'][len(history['steps'][index-1]['states'][0]['requests']):]
                if row['step'] == 'restore':
                    totals['retainedRestores'] += 1
                    totals['retainedRestorePixelMatches'] += encoded[0] == initial[0]
            public = lambda name: history['steps'][STEPS.index(name)]['states'][0]
            fixture = history['configuration']
            assert public('external-query')['query'] == 'No matching commands'
            owner = fixture['owner']
            expected = 'q' if owner == 'echo' else 'Owner redirect' if owner == 'redirect' else 'No matching commands'
            assert public('key-query')['query'] == expected
            if owner == 'delayed':
                assert public('key-query')['pending'] == 'q'
                assert public('flush-owner')['query'] == 'q' and public('flush-owner')['pending'] is None
                assert public('flush-clear')['query'] == '' and public('flush-clear')['pending'] is None
            if owner == 'observe':
                assert public('clear-query')['query'] == 'No matching commands'
            if owner == 'redirect':
                assert public('clear-query')['query'] == 'Owner redirect'
            if len(fixture['entries']) == 3:
                first = fixture['entries'][0]['key']
                assert public('initial')['rowCounts'][first] == 0
                assert public('click-first')['rowCounts'][first] == 1
                assert public('click-first-again')['rowCounts'][first] == 2
                assert public('identity-update')['rowCounts'][first] == 2
                assert public('labels')['rowCounts'][first] == 2
                assert public('disabled-click')['rowCounts'] == public('disable')['rowCounts']
                assert public('restore')['rowCounts'][first] == 0
                assert public('click-first-restored')['rowCounts'][first] == 1
            if fixture['id'] == 'many-buttons':
                first = fixture['entries'][0]['key']
                assert public('click-first-again')['rowCounts'][first] == 2
                assert public('scroll-bottom')['rowCounts'][first] == 2
                assert public('restore')['rowCounts'][first] == 2
                assert public('click-first-restored')['rowCounts'][first] == 3
                assert history['steps'][STEPS.index('restore')]['matchesInitialPixels'] is False
            totals['histories'] += 1
    assert seen == set(itertools.product(hist_defs, CONTEXTS))

    sizing = read('sizing-output/sizing.json')
    assert sizing['reference'] == REFERENCE and sizing['accepted'] is False
    seen = set()
    for row in sizing['rows']:
        key = row['configuration']['id'], context(row)
        assert key not in seen and key[1] in CONTEXTS
        seen.add(key)
        assert row['configuration'] == clean(definitions[key[0]])
        assert [r['mode'] for r in row['modes']] == [0, 1, 2]
        queries = row['modes'][0]['proposals']
        assert len(queries) == 15
        assert all(m['proposals'] == queries for m in row['modes'])
        assert all(m['windowKey'] is False and m['applicationActive'] is False and m['backingDpr'] == 2 for m in row['modes'])
        assert all(value == dict(width=520, height=380) for value in queries.values())
        totals['sizingContexts'] += 1
        totals['sizingQueriesPerBranch'] += len(queries)
        totals['sizingBranchQueries'] += len(queries)*3
    assert seen == set(itertools.product(definitions, CONTEXTS))
    targets = read('clear-targets.json')
    assert targets['accepted'] is False and len(targets['targets']) == 16
    for target in targets['targets'].values():
        source = directory / 'output' / safe(target['source'])
        assert digest(source) == target['sha256']
        with Image.open(source) as image:
            x0, y0, x1, y1 = target['bounds']
            assert x0 < x1 and y0 < y1
            dpr = image.width / 720
            assert [target['x'], target['y']] == [(x0+x1)/(2*dpr), (y0+y1)/(2*dpr)]
            colors = image.convert('RGBA').crop((x0, y0, x1, y1)).getcolors((x1-x0)*(y1-y0))
            assert any(color == tuple(target['rgba']) for count, color in colors)
    assert len(images) == 5376
    return totals


def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = json.loads((directory / 'investigation.json').read_text())
    validate_report(report)
    files = {str(p.relative_to(directory)) for p in directory.rglob('*')
        if p.is_file() and p.name not in ['investigation.json', 'README.md']}
    assert files == set(report['files'])
    for name, checksum in report['files'].items():
        safe(name)
        assert digest(directory / name) == checksum, name
    assert observations(directory) == report['summary']
    read = lambda name: json.loads((directory / name).read_text())
    diagnostic = read('diagnostics/three-tall/history-output/histories.json')['histories']
    assert len(diagnostic) == 1 and context(diagnostic[0]) == ('light', 1, 1)
    assert [row['step'] for row in diagnostic[0]['steps']] == STEPS
    for row in diagnostic[0]['steps']:
        encoded = [(directory / 'diagnostics/three-tall/history-output' / safe(name)).read_bytes()
            for name in row['paths']]
        assert encoded[0] == encoded[1] == encoded[2]
        assert row['publicProbedIdentical'] is row['publicLiteralIdentical'] is True
    phases = {row['step']: row['states'][0] for row in diagnostic[0]['steps']}
    assert phases['direction']['appearedKeys'] == ['1', '2']
    assert phases['restore']['rowInstances'] == {'0': 1, '1': 2, '2': 1}
    assert read('diagnostics/three-tall/result.json')['exitCode'] == 0
    identity = read('source-identity.json')
    spec = importlib.util.spec_from_file_location('spotlight_source_tree', ROOT / 'scripts/verify-native-source-rebuild.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert len(identity['files']) == 89 and module.tree_hash(identity['files']) == TREE
    bypath = {r['path']: r for r in identity['files']}
    source = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    for row in source['files']:
        assert all(bypath[row['path']][key] == row[key] for key in ['mode', 'gitBlob', 'sha256'])
    fresh = read('provenance/fresh-inputs.json')
    first = read('provenance/first-inputs.json')
    assert first['prebuiltLibraryInputs'] is fresh['prebuiltLibraryInputs'] is False
    assert first['reference'] == fresh['reference'] == REFERENCE
    assert first['files']['reference-source.tar'] == fresh['files']['reference-source.tar'] == identity['fullArchiveSha256']
    for name in ['fixtures.json', 'histories.json', 'measure-clear.py'] + [
            'tool/' + name for name in ['SpotlightCommon.swift', 'Accessibility.swift', 'SpotlightMain.swift', 'SpotlightSizing.swift']]:
        assert first['files'][name] == fresh['files'][name]
    artifact = report['sourceOnlyArtifact']
    assert artifact['files'] == len(artifact['fileHashes']) == 11
    assert set(artifact['fileHashes']) == set(fresh['files']) | {'inputs.json'}
    assert all(artifact['fileHashes'][name] == checksum for name, checksum in fresh['files'].items())
    assert artifact['fileHashes']['inputs.json'] == digest(directory / 'provenance/fresh-inputs.json')
    assert read('provenance/first-result.json') == read('provenance/fresh-result.json') == dict(
        accepted=False, exitCode=0, sourceFilesUnchanged=89, prebuiltLibraryInputs=False)
    for name, count in [('first-commands.json', 6), ('fresh-commands.json', 7)]:
        commands = read('provenance/' + name)
        assert len(commands) == count and all(row['exitCode'] == 0 for row in commands)
        assert '--disable-automatic-resolution' in commands[0]['command']
        assert commands[0]['command'][commands[0]['command'].index('--target') + 1] == 'Sabella'
        assert 'arm64-apple-macosx26.0' in commands[0]['command']
    replay = json.loads((directory / 'replay.json').read_text())
    assert replay['prebuiltLibraryInputs'] is False and replay['sourceFilesUnchanged'] == 89
    assert replay['status'] == report['sourceReplayStatus']
    assert len(replay['files']) == 5381
    raw = {'clear-targets.json'} | {str(p.relative_to(directory))
        for name in ['output', 'history-output', 'supplementary-history-output', 'sizing-output']
        for p in (directory / name).rglob('*') if p.is_file()}
    assert set(replay['files']) == raw
    for name, record in replay['files'].items():
        safe(name)
        actual = digest(directory / name)
        assert actual == record['captureSha256']
        assert record['identical'] is (record['captureSha256'] == record['replaySha256'])
        if record['identical']:
            assert record['replayPath'] is None
        else:
            safe(record['replayPath'])
            assert digest(directory / record['replayPath']) == record['replaySha256']
    assert (replay['status'] == 'passed') is all(r['identical'] for r in replay['files'].values())
    print('Native spotlight: 256 closed contexts, 64 retained histories, 11520 sizing queries; Linux acceptance pending')
    return report


if __name__ == '__main__':
    verify()
