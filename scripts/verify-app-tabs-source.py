#!/usr/bin/env python3
"""Audit native tab-bar observations without accepting a Linux implementation."""
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path, PurePosixPath
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/app-tabs-20261017'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
TREE = 'db61113381a51fc3c7b3d12786609cd9e76627c8'
CONTEXTS = set(itertools.product(['light', 'dark'], [1, 1.5], [1, 2]))
STEPS = ['initial', 'click-second', 'reselect-second', 'external-selection', 'disable-second',
    'disabled-click', 'enable-second', 'ax-press-second', 'flush-owner', 'reorder',
    'labels-and-badges', 'narrow', 'direction', 'appearance', 'text-scale', 'empty', 'restore', 'click-first']
GATES = ['LinuxImplementation', 'nativeSymbolsFontsAndRaster', 'nativeLabelFitting',
    'nativeGenericIdentityAndDuplicateIDs', 'nativeKeyboardAndInputTiming',
    'nativeAccessibility', 'physicalDisplaysInput', 'readers', 'independentMachineReplayAvailability']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(name):
    p = PurePosixPath(name)
    assert name and str(p) == name and not p.is_absolute() and '..' not in p.parts, 'Unsafe evidence path'
    return p


def context(row):
    return row['appearance'], row['textScale'], row['dpr']


def config(value):
    return {k: v for k, v in value.items() if v is not None} | {
        'tabs': [{k: v for k, v in t.items() if v is not None} for t in value['tabs']]}


def active_frames(state):
    """Probes retain their last value; removed views are excluded by current data."""
    tabs = state['configuration']['tabs']
    result = {}
    for name, frame in state['frames'].items():
        if name in ['bar', 'caller']:
            result[name] = frame
            continue
        kind, index = name.rsplit('-', 1)
        index = int(index)
        if index < len(tabs) and (kind != 'badge' or int(tabs[index].get('badge') or 0) > 0):
            result[name] = frame
    return result


def validate_report(report):
    assert report['reference'] == REFERENCE and report['tree'] == TREE
    assert report['status'] == 'source-investigation; Linux implementation pending'
    assert report['accepted'] is False and report['expectedImagesChanged'] is False
    assert report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    assert report['remainingAcceptance'] == GATES
    assert report['sourceOnlyArtifact']['containsPinnedSourceFiles'] == 89
    assert report['sourceOnlyArtifact']['downloadAvailability'] == 'pending independent-machine replay'
    assert report['sourceReplayStatus'] in ['passed', 'failed']
    for key, value in dict(fixtures=43, closedContexts=344, closedImages=1032,
            sizingContexts=344, sizingQueriesPerBranch=5160, sizingBranchQueries=15480,
            histories=48, historySteps=864, historyImages=2592, rawOutputFiles=3627,
            nativeAccessibilityButtons=0, availableAccessibilityPresses=0,
            publicPointerDeliveries=192, hiddenBadgePairs=24, cappedBadgePairs=8,
            inheritedPresentationPairs=16, unchangedTextScalePairs=172).items():
        assert report['summary'][key] == value, key


def wrapper(state):
    assert state['windowVisible'] is True and state['windowKey'] is False and state['applicationActive'] is False
    assert state['backingDpr'] == 2 and state['accessibility']['truncated'] is False
    assert state['lifecycle'] == dict(appearances=1, disappearances=0, wrapperInstances=1)
    for frame in state['frames'].values():
        assert set(frame) == {'x', 'y', 'width', 'height'}
        assert all(type(v) in [int, float] and math.isfinite(v) for v in frame.values())
        assert frame['width'] >= 0 and frame['height'] >= 0


def observations(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    fixtures = read('fixtures.json')
    definitions = {f['id']: f for f in fixtures}
    assert len(definitions) == len(fixtures) == 43
    assert {f['valueKind'] for f in fixtures} == {'string', 'integer', 'boolean', 'record'}
    assert {f['owner'] for f in fixtures} == {'echo', 'observe', 'delayed', 'redirect'}
    images = set()
    totals = dict(closedPixelWitnessMatches=0, closedGeometryWitnessMatches=0,
        closedStateWitnessMatches=0, sizingWitnessMatches=0, historyPixelWitnessMatches=0,
        historyStateWitnessMatches=0, retainedRestores=0, nativeAccessibilityButtons=0,
        availableAccessibilityPresses=0, publicPointerDeliveries=0)

    def picture(name, dpr):
        safe(name)
        assert name not in images
        images.add(name)
        data = (directory / name).read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', data[16:24]) == (640 * dpr, 400 * dpr)
        return data

    def triple(row, prefix, configuration):
        assert len(row['paths']) == len(row['states']) == 3
        values = [picture(prefix + '/' + p, row['dpr']) for p in row['paths']]
        assert row['publicProbedIdentical'] is (values[0] == values[1])
        assert row['publicLiteralIdentical'] is (values[0] == values[2])
        states = row['states']
        for state in states:
            wrapper(state)
            totals['nativeAccessibilityButtons'] += sum(n.get('role') == 'AXButton' for n in state['accessibility']['nodes'])
        assert states[0]['frames'] == {}
        assert all(states[1]['frames'].get(k) == states[2]['frames'].get(k) for k in ['bar', 'caller'])
        stable = ['lifecycle', 'selection', 'requests', 'pending']
        state_same = all(states[0][k] == states[1][k] == states[2][k] for k in stable)
        return values, state_same

    closed = read('output/captures.json')
    assert closed['reference'] == REFERENCE and closed['accepted'] is False
    assert len(closed['rows']) == 344
    assert {(r['configuration']['id'], *context(r)) for r in closed['rows']} == {
        (key, *c) for key in definitions for c in CONTEXTS}
    for row in closed['rows']:
        assert row['configuration'] == config(definitions[row['configuration']['id']])
        values, same = triple(row, 'output', row['configuration'])
        totals['closedPixelWitnessMatches'] += values[0] == values[1] == values[2]
        totals['closedGeometryWitnessMatches'] += all(row['states'][1]['frames'][k] == row['states'][2]['frames'][k] for k in ['bar', 'caller'])
        totals['closedStateWitnessMatches'] += same
        for state in row['states']:
            assert state['selection'] == row['configuration']['selection'] and state['requests'] == []
        if row['configuration']['id'] == 'empty':
            assert row['states'][2]['frames']['bar']['height'] == 5
            assert row['states'][2]['frames']['bar']['width'] == 0
        if row['configuration']['id'] == 'width-30':
            assert row['states'][2]['frames']['bar']['width'] > row['states'][2]['frames']['caller']['width']

    by_context = {(r['configuration']['id'], *context(r)): r for r in closed['rows']}
    def pixels(key):
        return (directory / 'output' / by_context[key]['paths'][0]).read_bytes()
    hidden = capped = inherited = unchanged_scale = 0
    for appearance, scale, dpr in CONTEXTS:
        suffix = (appearance, scale, dpr)
        baseline = pixels(('width-300', *suffix))
        hidden += sum(pixels((name, *suffix)) == baseline for name in ['badge-0', 'badge--1', 'badge--9223372036854775808'])
        capped += pixels(('badge-100', *suffix)) == pixels(('badge-9223372036854775807', *suffix))
        inherited += sum(pixels((name, *suffix)) == baseline for name in ['parent-font', 'parent-red'])
    for name, appearance, dpr in itertools.product(definitions, ['light', 'dark'], [1, 2]):
        unchanged_scale += pixels((name, appearance, 1, dpr)) == pixels((name, appearance, 1.5, dpr))
    totals.update(hiddenBadgePairs=hidden, cappedBadgePairs=capped,
        inheritedPresentationPairs=inherited, unchangedTextScalePairs=unchanged_scale)

    sizing = read('sizing-output/sizing.json')
    assert sizing['reference'] == REFERENCE and sizing['accepted'] is False and len(sizing['rows']) == 344
    assert {(r['configuration']['id'], *context(r)) for r in sizing['rows']} == {(key, *c) for key in definitions for c in CONTEXTS}
    sizing_differences = []
    for row in sizing['rows']:
        assert row['configuration'] == config(definitions[row['configuration']['id']])
        assert [m['mode'] for m in row['modes']] == [0, 1, 2]
        for mode in row['modes']:
            assert len(mode['proposals']) == 15 and mode['windowKey'] is False and mode['applicationActive'] is False and mode['backingDpr'] == 2
        a, b, c = [m['proposals'] for m in row['modes']]
        differences = {k: [a[k], b[k], c[k]] for k in a if not a[k] == b[k] == c[k]}
        totals['sizingWitnessMatches'] += not differences
        if differences:
            sizing_differences.append(dict(fixture=row['configuration']['id'], appearance=row['appearance'], textScale=row['textScale'], dpr=row['dpr'], proposals=differences))
    assert read('sizing-witness-differences.json') == sizing_differences

    history = read('history-output/histories.json')
    histories = read('histories.json')
    names = {r['id'] for r in histories}
    assert names == {'width-300', 'canonical', 'integer', 'owner-observe', 'owner-delayed', 'owner-redirect'}
    assert history['reference'] == REFERENCE and history['accepted'] is False and len(history['histories']) == 48
    assert {(r['configuration']['id'], *context(r)) for r in history['histories']} == {(key, *c) for key in names for c in CONTEXTS}
    for row in history['histories']:
        f = row['configuration']
        assert f == config(definitions[f['id']]) and [s['step'] for s in row['steps']] == STEPS
        named = {s['step']: s for s in row['steps']}
        initial = None
        for step in row['steps']:
            composite = dict(step, dpr=row['dpr'])
            values, same = triple(composite, 'history-output', f)
            if initial is None:
                initial = values
            assert step['matchesInitialPixels'] is (values == initial)
            totals['historyPixelWitnessMatches'] += values[0] == values[1] == values[2]
            totals['historyStateWitnessMatches'] += same
            for action in step['actions']:
                if action['kind'] == 'accessibilityPress':
                    totals['availableAccessibilityPresses'] += action['available']
                    if not action['available']:
                        assert action['returned'] is None
            if step['actions'] and step['actions'][0]['kind'] == 'pointer':
                totals['publicPointerDeliveries'] += 1
            if step['step'] == 'restore':
                totals['retainedRestores'] += values == initial
            if step['step'] == 'empty':
                assert all(active_frames(s) == {k: v for k, v in s['frames'].items() if k in ['bar', 'caller']} for s in step['states'])
        for mode in range(3):
            state = lambda name: named[name]['states'][mode]
            second = f['tabs'][1]['value']
            assert state('click-second')['requests'] == [second]
            assert state('reselect-second')['requests'] == [second, second]
            assert state('disabled-click')['requests'] == state('disable-second')['requests']
            assert state('external-selection')['selection'] == f['tabs'][-1]['value']
            if f['owner'] == 'echo':
                assert state('click-second')['selection'] == second
            else:
                assert state('click-second')['selection'] == f['selection']
            if f['owner'] == 'delayed':
                assert state('click-second')['pending'] == second
                assert state('flush-owner')['selection'] == second and state('flush-owner')['pending'] is None
            if f['owner'] == 'observe':
                assert state('flush-owner')['selection'] == f['tabs'][-1]['value']
            assert state('click-first')['requests'] == [second, second, f['tabs'][0]['value']]
    assert len(images) == 3624
    return totals


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    validate_report(report)
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name not in ['investigation.json', 'README.md']}
    assert set(report['files']) == actual, 'Missing or extra evidence'
    for name, checksum in report['files'].items():
        safe(name)
        assert digest(directory / name) == checksum, name
    totals = observations(directory)
    for name, count in totals.items():
        assert report['summary'][name] == count, name
    identity = read('source-identity.json')
    spec = importlib.util.spec_from_file_location('source_identity', ROOT / 'scripts/verify-native-source-rebuild.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert len(identity['files']) == 89 and module.tree_hash(identity['files']) == TREE
    assert read('provenance/initial-inputs.json')['sourceFiles'] == {r['path']: r['sha256'] for r in identity['files']}
    initial = read('provenance/initial-inputs.json')
    assert initial['reference'] == REFERENCE and initial['sourceFilesUnchanged'] == 89
    assert initial['prebuiltLibraryInputs'] is True and initial['helperBuildExitCode'] == 0 and initial['failedHelperBuildExitCode'] == 1
    assert 'Sabella.o' in initial['compiledLibraryInputs']
    assert len(initial['helpers']) == 3
    source = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    bypath = {r['path']: r for r in identity['files']}
    for row in source['files']:
        assert all(bypath[row['path']][k] == row[k] for k in ['mode', 'gitBlob', 'sha256'])
    assert bypath['Sources/Sabella/Mobile.swift']['sha256'] == '1feea91528f96a09679d67e381a9d0a79a58fa9ce8a6e0bc29d36c5edb4f24fa'
    fresh = read('provenance/fresh-inputs.json')
    assert fresh['prebuiltLibraryInputs'] is False and fresh['reference'] == REFERENCE
    assert fresh['files']['reference-source.tar'] == identity['fullArchiveSha256']
    assert all(fresh['files'][n] == checksum for n, checksum in initial['helpers'].items())
    artifact = report['sourceOnlyArtifact']
    assert artifact['files'] == len(artifact['fileHashes']) == 8
    assert set(artifact['fileHashes']) == set(fresh['files']) | {'inputs.json'}
    assert all(artifact['fileHashes'][n] == checksum for n, checksum in fresh['files'].items())
    assert artifact['fileHashes']['inputs.json'] == digest(directory / 'provenance/fresh-inputs.json')
    assert read('provenance/fresh-result.json') == dict(exitCode=0, sourceFilesUnchanged=89, prebuiltLibraryInputs=False, accepted=False)
    commands = read('provenance/fresh-commands.json')
    assert len(commands) == 5 and all(r['exitCode'] == 0 for r in commands)
    assert '--disable-automatic-resolution' in commands[0]['command'] and '--target' in commands[0]['command']
    assert commands[0]['command'][commands[0]['command'].index('--target') + 1] == 'Sabella'
    assert 'arm64-apple-macosx26.0' in commands[0]['command']
    assert all('avelino-app-tabs-source-replay-20261017-v1' in c for c in commands[1]['command'] if c.endswith(('Sabella.o', '.swift')))
    replay = read('replay.json')
    raw = {str(p.relative_to(directory)) for name in ['output', 'sizing-output', 'history-output'] for p in (directory / name).rglob('*') if p.is_file()}
    assert len(raw) == 3627 and len(replay['results']) == 3627 and {r['path'] for r in replay['results']} == raw
    exact = 0
    for row in replay['results']:
        safe(row['path'])
        assert row['firstSha256'] == digest(directory / row['path'])
        same = row['firstSha256'] == row['replaySha256']
        assert row['status'] == ('passed' if same else 'failed')
        if same:
            assert row['replayPath'] is None
        else:
            safe(row['replayPath'])
            assert row['replaySha256'] == digest(directory / row['replayPath'])
        exact += same
    assert replay['extraFiles'] == []
    assert report['summary']['sourceReplayExactFiles'] == exact
    assert report['sourceReplayStatus'] == ('passed' if exact == len(raw) else 'failed')
    return dict(totals, sourceReplayExactFiles=exact, accepted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
