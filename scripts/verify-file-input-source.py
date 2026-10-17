#!/usr/bin/env python3
"""Recompute FileInput native evidence without claiming Linux acceptance."""
import hashlib
import itertools
import json
import math
from pathlib import Path, PurePosixPath
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/file-input-20261017'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
TREE = 'db61113381a51fc3c7b3d12786609cd9e76627c8'
SOURCE = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
CONTEXTS = set(itertools.product(['light', 'dark'], [1, 1.5], [1, 2]))
GATES = ['LinuxImplementation', 'LinuxSizing', 'nativeChooserPresentationFontsRaster',
    'typeConformanceAndOwnerUpdates', 'nativeInputAndCallbackTiming',
    'freshSourceBehaviorReplay', 'nativeAccessibility', 'physicalDisplaysInput',
    'readers', 'independentMachineReplayAvailability']
SUMMARY = dict(fixtures=32, closedContexts=256, closedImages=768,
    pixelWitnessMatches=256, geometryWitnessMatches=256, sizingContexts=256,
    sizingQueriesPerBranch=3840, sizingBranchQueries=11520,
    nativeUISuccessCallbacks=7, controlledAXObservations=26)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(name):
    path = PurePosixPath(name)
    assert str(path) == name and not path.is_absolute() and '..' not in path.parts


def validate_report(report):
    assert report['reference'] == REFERENCE and report['tree'] == TREE
    assert report['accepted'] is False and report['expectedImagesChanged'] is False
    assert report['status'] == 'source-investigation; Linux implementation pending'
    assert report['tolerance'] == 'none' and report['approvedExceptions'] == []
    assert report['remainingAcceptance'] == GATES
    assert report['summary'] == SUMMARY
    artifact = report['sourceOnlyArtifact']
    assert artifact['containsPinnedSourceFiles'] == 89
    assert artifact['prebuiltLibraryInputs'] is False
    assert artifact['sha256'] == 'ab7ff095cdcd10ff6816b09997ccdce5bed57e689d5077b079b9cc961e166bea'
    assert artifact['downloadAvailability'] == 'pending independent-machine replay'
    assert report['sourceReplayStatus'] in ['passed', 'failed']
    assert report['behaviorSourceReplayStatus'] == 'pending'
    assert report['physicalInputAcceptance'] == report['openPanelRasterAcceptance'] == 'pending'


def closed_observations(directory, fixtures, data):
    assert data['reference'] == REFERENCE and data['accepted'] is False
    totals = dict(closedContexts=0, closedImages=0, pixelWitnessMatches=0,
        geometryWitnessMatches=0)
    seen, images = set(), set()
    for row in data['rows']:
        key = row['configuration']['id'], (row['appearance'], row['textScale'], row['dpr'])
        assert key not in seen and key[1] in CONTEXTS
        seen.add(key)
        assert row['configuration'] == {k: v for k, v in fixtures[key[0]].items() if v is not None}
        modes = row['modes']
        assert [m['mode'] for m in modes] == [0, 1, 2]
        encoded = []
        for mode in modes:
            name = 'output/' + mode['path']
            safe(name)
            assert name not in images
            images.add(name)
            png = (directory / name).read_bytes()
            assert png.startswith(b'\x89PNG\r\n\x1a\n')
            assert struct.unpack('!II', png[16:24]) == (600 * row['dpr'], 300 * row['dpr'])
            encoded.append(png)
            state = mode['state']
            assert state['applicationActive'] is False and state['windowKey'] is False
            assert state['backingDpr'] == 2 and state['mounted'] is True
            assert state['results'] == []
            assert set(state['frames']) == (set() if mode['mode'] == 0 else {'body', 'caller'})
            for frame in state['frames'].values():
                assert set(frame) == {'x', 'y', 'width', 'height'}
                assert all(isinstance(v, (int, float)) and math.isfinite(v) for v in frame.values())
                assert frame['width'] >= 0 and frame['height'] >= 0
        assert row['publicProbedIdentical'] is (encoded[0] == encoded[1])
        assert row['publicLiteralIdentical'] is (encoded[0] == encoded[2])
        totals['closedContexts'] += 1
        totals['closedImages'] += 3
        totals['pixelWitnessMatches'] += encoded[0] == encoded[1] == encoded[2]
        totals['geometryWitnessMatches'] += modes[1]['state']['frames'] == modes[2]['state']['frames']
    assert seen == set(itertools.product(fixtures, CONTEXTS))
    assert {str(p.relative_to(directory)) for p in (directory / 'output').glob('*.png')} == images
    return totals


def sizing_observations(fixtures, data):
    assert data['reference'] == REFERENCE and data['accepted'] is False
    seen, proposals = set(), None
    for row in data['rows']:
        key = row['configuration']['id'], (row['appearance'], row['textScale'], row['dpr'])
        assert key not in seen and key[1] in CONTEXTS
        seen.add(key)
        assert row['configuration'] == {k: v for k, v in fixtures[key[0]].items() if v is not None}
        modes = row['modes']
        assert [m['mode'] for m in modes] == [0, 1, 2]
        assert modes[0]['proposals'] == modes[1]['proposals'] == modes[2]['proposals']
        if proposals is None:
            proposals = set(modes[0]['proposals'])
        assert len(proposals) == 15 and set(modes[0]['proposals']) == proposals
        for mode in modes:
            assert mode['applicationActive'] is False and mode['windowKey'] is False
            assert mode['backingDpr'] == 2
            for size in mode['proposals'].values():
                assert set(size) == {'width', 'height'}
                assert all(isinstance(v, (int, float)) and math.isfinite(v) and v >= 0 for v in size.values())
    assert seen == set(itertools.product(fixtures, CONTEXTS))
    return dict(sizingContexts=len(seen), sizingQueriesPerBranch=len(seen) * 15,
        sizingBranchQueries=len(seen) * 45)


def behavior_observations(directory):
    read = lambda name: json.loads((directory / name).read_text())
    trace = read('native-ui/output/ui-trace.json')
    assert trace['accepted'] is False and trace['reference'] == REFERENCE
    steps = trace['steps']
    assert steps[-1]['phase'] == 'finished'
    results = steps[-1]['results']
    assert len(results) == 7
    root = 'file:///Users/gaulatti/.codex/tmp/avelino-file-input-fixtures-20261017-v1/'
    expected = [['one.txt'], ['one.txt', 'two.txt'], ['one.txt'],
        ['one.txt', 'two.txt'], ['one.txt'], ['fake.png'], ['folder/']]
    for index, (row, names) in enumerate(zip(results, expected)):
        assert row == dict(kind='success', ordinal=index, panelVisibleAtCallback=True,
            urls=[root + name for name in names])
    removed = [s for s in steps if s['phase'] == 'owner-result' and s['mounted'] is False]
    assert len(removed) == 1 and len(removed[0]['results']) == 3
    panels = {tuple(s['allowedContentTypes']): s for s in steps if s['phase'] == 'panel-ready'}
    assert set(panels) == {('public.plain-text',), ('public.image',), ('public.folder',), (), ('public.item',)}
    for types, panel in panels.items():
        assert panel['allowsMultipleSelection'] is True
        assert panel['canChooseDirectories'] is (types == ('public.folder',))
        assert panel['canChooseFiles'] is (types in [('public.plain-text',), ('public.image',), ('public.item',)])
        assert panel['resolvesAliases'] is True
    ax = read('native-ui/output/cua-observations.json')
    assert ax['fileInputCuaEvidenceVersion'] == 1
    phases = {row['phase']: row['state'] for row in ax['observations']}
    assert len(phases) == len(ax['observations']) == 26
    assert 'Choose file' not in phases['removed-in-result']
    assert 'Choose file' in phases['reverse-order-accepted']
    assert '(disabled) Open' in phases['image-no-extension-click']
    assert '(selected, settable)' in phases['image-fake-extension-click']
    assert '(disabled) Open' not in phases['image-fake-extension-click']
    assert '(disabled) Open' in phases['empty-filter-file-click']
    assert '(selected, settable)' in phases['item-filter-file-click']
    assert '(disabled) Open' in phases['item-filter-file-click']
    assert read('diagnostics/v2/result.json')['exitCode'] == -6
    assert 'not implemented' in (directory / 'diagnostics/v2/behavior.log').read_text()
    for mode in range(3):
        data = read(f'diagnostics/v3/output/mode{mode}.json')
        assert data['accepted'] is False and data['mode'] == mode
        states = {step['phase']: step for step in data['steps']}
        assert states['after-cancel']['results'] == [] and states['after-cancel']['visible'] is False
        assert all(step['results'] == [] for step in data['steps'])
    assert read('native-ui/result.json') == dict(exitCode=0, accepted=False)
    return dict(nativeUISuccessCallbacks=len(results), controlledAXObservations=len(phases))


def verify(directory=DIRECTORY):
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    validate_report(report)
    files = read('files.json')
    assert set(files) == {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        safe(name)
        path = directory / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    definitions = read('fixtures.json')
    fixtures = {row['id']: row for row in definitions}
    assert len(definitions) == len(fixtures) == 32
    totals = dict(fixtures=len(fixtures))
    totals.update(closed_observations(directory, fixtures, read('output/captures.json')))
    totals.update(sizing_observations(fixtures, read('sizing-output/sizing.json')))
    totals.update(behavior_observations(directory))
    assert totals == report['summary'] == read('observations.json')
    inputs = []
    for prefix in ['source-build', 'source-replay-build']:
        result = read(prefix + '/result.json')
        assert result == dict(accepted=False, exitCode=0, sourceFilesUnchanged=89,
            prebuiltLibraryInputs=False, sourceArchiveSha256=report['sourceOnlyArtifact']['sha256'])
        commands = read(prefix + '/commands.json')
        assert [c['name'] for c in commands] == ['library-build', 'capture-build', 'capture', 'sizing-build', 'sizing']
        assert all(c['exitCode'] == 0 for c in commands)
        assert commands[0]['command'][:2] == ['swift', 'build']
        assert '--disable-automatic-resolution' in commands[0]['command']
        record = read(prefix + '/inputs.json')
        assert record['prebuiltLibraryInputs'] is False and record['accepted'] is False
        assert record['files']['reference-source.tar'] == SOURCE
        inputs.append(record)
    assert inputs[0] == inputs[1]
    replay = read('source-replay.json')
    expected = {'output/' + m['path'] for row in read('output/captures.json')['rows'] for m in row['modes']}
    expected.update(['output/captures.json', 'sizing-output/sizing.json'])
    assert len(replay['files']) == 770 and {row['path'] for row in replay['files']} == expected
    for row in replay['files']:
        safe(row['path'])
        assert row['identical'] is (row['originalSha256'] == row['replaySha256'])
        assert digest(directory / row['path']) == row['originalSha256']
    assert replay['status'] == report['sourceReplayStatus']
    assert replay['status'] == ('passed' if all(row['identical'] for row in replay['files']) else 'failed')
    print('FileInput: 256 native closed witnesses, 11520 sizing responses and 7 UI callbacks; Linux pending')


if __name__ == '__main__':
    verify()
