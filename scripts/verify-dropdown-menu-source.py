#!/usr/bin/env python3
"""Recompute native dropdown witnesses without accepting the Linux adapter."""
import hashlib
import itertools
import json
import math
from pathlib import Path, PurePosixPath
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/dropdown-menu-20261017'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
TREE = 'db61113381a51fc3c7b3d12786609cd9e76627c8'
CONTEXTS = set(itertools.product(['light', 'dark'], [1, 1.5], [1, 2]))
GATES = ['LinuxImplementation', 'nativeLabelConversionAndBuilderTiming',
    'nativeMenuPresentationSymbolsFontsRaster', 'LinuxSizing', 'nativeMenuInputTiming',
    'nativeAccessibility', 'physicalDisplaysInput', 'readers',
    'independentMachineReplayAvailability']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(name):
    path = PurePosixPath(name)
    assert str(path) == name and not path.is_absolute() and '..' not in path.parts


def clean(value):
    return {key: item for key, item in value.items() if item is not None}


def validate_report(report):
    assert report['reference'] == REFERENCE and report['tree'] == TREE
    assert report['accepted'] is False and report['expectedImagesChanged'] is False
    assert report['status'] == 'source-investigation; Linux implementation pending'
    assert report['tolerance'] == 'none' and report['approvedExceptions'] == []
    assert report['remainingAcceptance'] == GATES
    assert report['sourceOnlyArtifact']['containsPinnedSourceFiles'] == 89
    assert report['sourceOnlyArtifact']['prebuiltLibraryInputs'] is False
    assert report['sourceOnlyArtifact']['sha256'] == 'be8c686d2747851fdf84d5c35faefea3f626806d17d5bf080c006ebed9c908df'
    assert report['sourceOnlyArtifact']['downloadAvailability'] == 'pending independent-machine replay'
    assert report['sourceReplayStatus'] in ['passed', 'failed']
    assert report['normalPointerAcceptance'] == 'pending'
    assert report['menuShadowBackdropAcceptance'] == 'pending'
    assert report['summary'] == dict(fixtures=32, closedContexts=256, closedImages=768,
        pixelWitnessMatches=256, geometryWitnessMatches=256, nativeControlWitnessMatches=256,
        sizingContexts=256, sizingQueriesPerBranch=3840, sizingBranchQueries=11520,
        directDispatchBranches=3, ownerActionsPerBranch=3)


def observations(directory=DIRECTORY):
    read = lambda name: json.loads((directory / name).read_text())
    definitions = read('fixtures.json')
    fixtures = {row['id']: row for row in definitions}
    assert len(definitions) == len(fixtures) == 32
    data = read('output/captures.json')
    assert data['reference'] == REFERENCE and data['accepted'] is False
    totals = dict(fixtures=32, closedContexts=0, closedImages=0, pixelWitnessMatches=0,
        geometryWitnessMatches=0, nativeControlWitnessMatches=0, sizingContexts=0,
        sizingQueriesPerBranch=0, sizingBranchQueries=0, directDispatchBranches=0,
        ownerActionsPerBranch=3)
    seen = set()
    images = set()
    for row in data['results']:
        context = row['appearance'], row['textScale'], row['dpr']
        key = row['fixture'], context
        assert key not in seen and context in CONTEXTS
        seen.add(key)
        assert row['configuration'] == clean(fixtures[key[0]])
        modes = row['modes']
        assert [mode['mode'] for mode in modes] == [0, 1, 2]
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
            assert mode['windowKey'] is False and mode['applicationActive'] is False
            assert mode['backingDpr'] == 2 and mode['calls'] == []
            popups = [v for v in mode['views'] if v['type'] == 'SwiftUIPopupButton']
            assert len(popups) == 1
            assert popups[0]['pullsDown'] is True
            assert popups[0]['enabled'] is not fixtures[key[0]]['disabled']
            assert popups[0]['menu']['items'] == [], 'Closed menu content was unexpectedly built'
            for frame in mode['frames'].values():
                assert set(frame) == {'x', 'y', 'width', 'height'}
                assert all(isinstance(n, (int, float)) and math.isfinite(n) for n in frame.values())
                assert frame['width'] >= 0 and frame['height'] >= 0
        assert row['publicProbedIdentical'] is (encoded[0] == encoded[1])
        assert row['publicLiteralIdentical'] is (encoded[0] == encoded[2])
        totals['closedContexts'] += 1
        totals['closedImages'] += 3
        totals['pixelWitnessMatches'] += encoded[0] == encoded[1] == encoded[2]
        totals['geometryWitnessMatches'] += modes[1]['frames'] == modes[2]['frames']
        totals['nativeControlWitnessMatches'] += modes[0]['views'] == modes[1]['views'] == modes[2]['views']
    assert seen == set(itertools.product(fixtures, CONTEXTS))
    assert {str(path.relative_to(directory)) for path in (directory / 'output').glob('*.png')} == images
    sizing = read('sizing-output/sizing.json')
    assert sizing['reference'] == REFERENCE and sizing['accepted'] is False
    seen = set()
    proposals = None
    for row in sizing['rows']:
        key = row['configuration']['id'], (row['appearance'], row['textScale'], row['dpr'])
        assert key not in seen and key[1] in CONTEXTS
        seen.add(key)
        assert row['configuration'] == clean(fixtures[key[0]])
        modes = row['modes']
        assert [mode['mode'] for mode in modes] == [0, 1, 2]
        assert modes[0]['proposals'] == modes[1]['proposals'] == modes[2]['proposals']
        assert len(modes[0]['proposals']) == 15
        if proposals is None:
            proposals = set(modes[0]['proposals'])
        assert set(modes[0]['proposals']) == proposals
        for mode in modes:
            assert mode['windowKey'] is False and mode['applicationActive'] is False
            assert mode['backingDpr'] == 2
        totals['sizingContexts'] += 1
        totals['sizingQueriesPerBranch'] += 15
        totals['sizingBranchQueries'] += 45
    assert seen == set(itertools.product(fixtures, CONTEXTS))
    for branch in range(3):
        trace = read(f'behavior-output/mode{branch}.json')
        assert trace['accepted'] is False
        steps = {step['phase']: step for step in trace['steps']}
        assert steps['initial']['menu']['items'] == steps['update']['menu']['items'] == []
        assert steps['initial']['popupEnabled'] is True
        assert steps['initial']['windowKey'] is False and steps['initial']['applicationActive'] is False
        items = steps['tracking']['menu']['items']
        assert len(items) == 4 and items[0]['hidden'] is True
        assert [item['title'] for item in items[1:]] == ['Open', 'Duplicate', 'Remove']
        assert steps['after-cancel']['calls'] == []
        for index in range(4):
            step = steps[f'dispatch-{index}']
            assert 'direct-dispatch diagnostic, not pointer acceptance' in step['method']
            assert step['calls'] == ['open', 'duplicate', 'remove'][:index]
        totals['directDispatchBranches'] += 1
    return totals


def verify(directory=DIRECTORY):
    report = json.loads((directory / 'investigation.json').read_text())
    validate_report(report)
    files = json.loads((directory / 'files.json').read_text())
    assert set(files) == {str(path.relative_to(directory)) for path in directory.rglob('*')
        if path.is_file() and path.name != 'files.json'}
    for name, row in files.items():
        safe(name)
        path = directory / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    assert observations(directory) == report['summary']
    inputs = []
    for prefix in ['source-build', 'source-replay-build']:
        result = json.loads((directory / prefix / 'result.json').read_text())
        assert result == dict(accepted=False, exitCode=0, sourceFilesUnchanged=89, prebuiltLibraryInputs=False)
        commands = json.loads((directory / prefix / 'commands.json').read_text())
        assert [row['name'] for row in commands] == ['library-build', 'capture-build',
            'sizing-build', 'behavior-build', 'capture', 'sizing', 'behavior']
        assert all(row['exitCode'] == 0 for row in commands)
        assert commands[0]['command'][0:2] == ['swift', 'build']
        assert '--disable-automatic-resolution' in commands[0]['command']
        record = json.loads((directory / prefix / 'inputs.json').read_text())
        assert record['prebuiltLibraryInputs'] is False
        assert record['reference'] == REFERENCE and record['tree'] == TREE
        assert set(record['files']) == {'fixtures.json', 'reference-source.tar', 'replay.py',
            'tool/DropdownCommon.swift', 'tool/CaptureMain.swift', 'tool/SizingMain.swift', 'tool/BehaviorMain.swift'}
        inputs.append(record)
    assert inputs[0] == inputs[1]
    replay = json.loads((directory / 'source-replay.json').read_text())
    assert replay['status'] == report['sourceReplayStatus']
    assert len(replay['files']) == 773
    assert all(row['identical'] is (row['originalSha256'] == row['replaySha256']) for row in replay['files'])
    assert replay['status'] == ('passed' if all(row['identical'] for row in replay['files']) else 'failed')
    for row in replay['files']:
        safe(row['path'])
        assert digest(directory / row['path']) == row['originalSha256']
    print('Dropdown: 256 native closed witnesses and 3840 sizing proposals per branch; Linux implementation pending')


if __name__ == '__main__':
    verify()
