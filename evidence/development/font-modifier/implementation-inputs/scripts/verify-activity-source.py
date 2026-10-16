#!/usr/bin/env python3
"""Audit pinned ActivityItem source measurements; never approve Linux parity."""
import hashlib
import itertools
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/activity-item-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
SOURCE_SHA256 = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
FIXTURES = set('''actions-button actions-counter actions-empty actions-empty-direct actions-hidden
actions-multi actions-multi-direct actions-nested actions-plain actions-rect actions-tall actions-zero
all-empty badge-anchor bidi button-anchor default-icon disabled disabled-empty disabled-multi
empty-detail empty-timestamp empty-title intrinsic intrinsic-empty intrinsic-multi locale-ar locale-de
long-detail long-timestamp long-title multiline-detail multiline-timestamp multiline-title narrow-empty
narrow-multi narrow-nested narrow-plain narrow-rect narrow-tall narrow-zero parent-font32
parent-font32-plain parent-font32-red parent-red parent-red-plain rtl rtl-empty rtl-multi rtl-narrow
spaces symbol-empty symbol-house symbol-wide unbreakable unicode width-0 width-100 width-108
width-109 width-12 width-120 width-160 width-180 width-240 width-320 width-36 width-60 width-720'''.split())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(directory, name):
    return json.loads((directory / name).read_text())


def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = read(directory, 'investigation.json')
    assert report['referenceRevision'] == REFERENCE
    assert report['accepted'] is False and report['approvedExceptions'] == []
    assert report['expectedImagesChanged'] is False
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert actual == set(report['files']) | {'investigation.json'}, 'Missing or extra source evidence'
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name
    provenance = read(directory, 'tooling-provenance.json')
    assert provenance['reference'] == REFERENCE and provenance['sourceFiles'] == 89
    assert provenance['sourceArchiveSha256'] == SOURCE_SHA256
    assert provenance['sourceTree'] == 'db61113381a51fc3c7b3d12786609cd9e76627c8'
    assert provenance['compiledInputs'] == [], 'Compiled inputs cannot replace a source-only replay'
    assert provenance['independentMachineAvailability'] == 'pending'
    inputs = read(directory, 'replay-inputs.json')
    assert inputs['reference'] == REFERENCE
    assert set(inputs['files']) == {'reference-source.tar', 'replay.py', 'tool/Common.swift', 'tool/Fixtures.swift',
                                   'tool/CaptureMain.swift', 'tool/BehaviorMain.swift', 'tool/LayoutMain.swift'}
    assert inputs['files']['reference-source.tar'] == SOURCE_SHA256
    rebuilt = read(directory, 'source-build-result.json')
    assert rebuilt['reference'] == REFERENCE and rebuilt['sourceFilesUnchanged'] == 89
    assert rebuilt['sourceArchiveSha256'] == SOURCE_SHA256
    assert rebuilt['libraryBuiltFromSources'] is True and rebuilt['prebuiltLibraryInputs'] is False
    replay = read(directory, 'clean-replay-comparison.json')
    assert replay['files'] == replay['byteIdenticalFiles'] == 1753 and replay['mismatches'] == []
    assert len(replay['outputs']) == 1753
    expected_outputs = {name for name in actual if name.startswith(('captures/', 'behavior/'))} | {'layout-queries.json'}
    assert {row['file'] for row in replay['outputs']} == expected_outputs, 'Replay output coverage changed'
    for row in replay['outputs']:
        assert row['originalSha256'] == row['replaySha256'] == digest(directory / row['file']), row['file']

    source = read(directory, 'captures/captures.json')
    assert source['reference'] == REFERENCE and source['fixtures'] == 69
    rows = source['captures']
    names = {row['fixture'] for row in rows}
    assert names == FIXTURES and len(rows) == 552
    assert {(r['fixture'], r['appearance'], r['textScale'], r['dpr']) for r in rows} == set(
        itertools.product(names, ['light', 'dark'], [1, 1.5], [1, 2])), 'Activity capture coverage changed'
    assert len({row['path'] for row in rows}) == 552
    activity = [row for row in rows if row['api'] == 'BleeckerActivityItem']
    assert len(activity) == 536
    lookup = {(r['fixture'], r['appearance'], r['textScale'], r['dpr']): r for r in rows}
    anchors = read(ROOT / 'evidence/reference-investigations/radio-20261016', 'captures/captures.json')['captures']
    anchor_lookup = {(r['appearance'], r['textScale'], r['dpr']): r for r in anchors if r['fixture'] == 'button-anchor'}
    for row in rows:
        assert row['source'] == REFERENCE and row['accepted'] is False
        assert row['captureMethod'] == 'NSHostingView.cacheDisplay in isolated NSWindow; explicit bitmap dimensions, no image resizing'
        actual = directory / 'captures' / row['path']
        assert actual.read_bytes() == (directory / 'captures' / row['instrumentedPath']).read_bytes()
        assert actual.read_bytes() == (directory / 'captures' / row['witnessPath']).read_bytes()
        assert row['instrumentedIdentity'] and row['witnessIdentity']
        assert struct.unpack('>II', actual.read_bytes()[16:24]) == (row['width'] * row['dpr'], row['height'] * row['dpr'])
        for state in ['native', 'instrumented', 'witness']:
            assert row[state]['backingDpr'] == 2 and not row[state]['key'] and not row[state]['main']
            assert not row[state]['applicationActive']
        root = row['componentRect']
        assert root == row['instrumented']['parts']['root'] == row['witnessRootRect'] == row['witness']['parts']['root']
        assert abs(root['x'] + root['width'] / 2 - row['width'] / 2) < 1e-6
        assert abs(root['y'] + root['height'] / 2 - row['height'] / 2) < 1e-6
        assert root['y'] >= 0 and root['y'] + root['height'] <= row['height'], 'Clipped source body'
        if row['fixture'] == 'button-anchor':
            anchor = anchor_lookup[(row['appearance'], row['textScale'], row['dpr'])]
            preserved = ROOT / 'evidence/reference-investigations/radio-20261016/captures' / anchor['path']
            assert actual.read_bytes() == preserved.read_bytes(), 'Preserved Button anchor changed'
        if row['api'] != 'BleeckerActivityItem':
            continue
        parts, fonts = row['witness']['parts'], row['witness']['fonts']
        assert parts['badge']['width'] == parts['badge']['height'] == 36
        assert parts['row']['height'] + 16 == root['height']
        assert parts['badge']['y'] == parts['text-column']['y'] == root['y'] + 8
        assert parts['spacer']['height'] == 0 and parts['spacer']['width'] >= 8
        for key, family, size in [('title', 'EncodeSans-SmBold', 14), ('detail', 'LibreFranklin-Regular', 12),
                                  ('timestamp', 'LibreFranklin-Regular', 10)]:
            assert fonts[key]['postScriptName'] == family and fonts[key]['pointSize'] == size
            assert fonts[key]['enabled'] == (not row['disabled'])
        if row['fixture'] == 'all-empty':
            assert all(parts[key]['height'] == 14 and parts[key]['width'] == 0 for key in ['title', 'detail', 'timestamp'])
            assert parts['text-column']['height'] == 48 and root['height'] == 64
        if row['fixture'] == 'parent-font32-plain':
            assert fonts['action-plain']['pointSize'] == 32
    for aliases in [('actions-multi', 'actions-multi-direct'), ('actions-empty', 'actions-empty-direct'),
                    ('default-icon', 'actions-button')]:
        for appearance, scale, dpr in itertools.product(['light', 'dark'], [1, 1.5], [1, 2]):
            left, right = [lookup[(name, appearance, scale, dpr)] for name in aliases]
            assert (directory / 'captures' / left['path']).read_bytes() == (directory / 'captures' / right['path']).read_bytes()

    layout = read(directory, 'layout-queries.json')
    widths = list(range(161)) + list(range(164, 401, 4))
    assert layout['reference'] == REFERENCE and layout['widths'] == widths
    assert layout['summary'] == dict(queries=7072, matchingRoots=7072, nativeActionRectPairs=8840, matchingActionRects=8840)
    actions = ['empty', 'button', 'multi', 'nested', 'plain', 'rect', 'tall', 'zero']
    queries = layout['queries']
    assert len(queries) == 7072 and {(r['actions'], r['proposalWidth'], r['dpr'], r['textScale']) for r in queries} == set(
        itertools.product(actions, widths, [1, 2], [1, 1.5]))
    minima = {'empty': 68, 'button': 108, 'multi': 148, 'nested': 141, 'plain': 80, 'rect': 112, 'tall': 112, 'zero': 80}
    action_pairs = 0
    nested_overflows = 0
    for row in queries:
        assert row['componentRect'] == row['witnessRoot'] == row['witnessRects']['root']
        assert row['rootMatches'] and row['actionRectsMatch']
        for name, bounds in row['nativeActionRects'].items():
            assert bounds == row['witnessRects'][name]
            action_pairs += 1
        if row['proposalWidth'] == 0:
            assert row['componentRect']['width'] == minima[row['actions']]
        if row['componentRect']['width'] > max(minima[row['actions']], row['proposalWidth']) + 1e-6:
            assert row['actions'] == 'nested' and row['textScale'] == 1.5
            nested_overflows += 1
    assert action_pairs == 8840 and nested_overflows == 178, 'Nested action elasticity cannot be replaced by a minimum-width clamp'

    behavior = read(directory, 'behavior/behavior.json')
    assert behavior['reference'] == REFERENCE
    traces = {trace['fixture']: trace for trace in behavior['traces']}
    assert set(traces) == {'ordinary', 'multi', 'multi-direct', 'empty', 'disabled', 'hidden', 'rtl', 'counter',
                           'during-down-hold', 'during-down-disable', 'during-down-remove', 'during-down-width', 'during-down-title'}
    assert len(traces) == 13 and sum(len(trace['events']) for trace in traces.values()) == 94
    for name, trace in traces.items():
        events = {event['action']: event['state'] for event in trace['events']}
        for event in trace['events']:
            assert (directory / 'behavior' / event['path']).is_file()
            assert event['state']['configuration']['fixture'] == name
            if event['action'].startswith('click-'):
                assert event['state']['calls'] == [], 'Activity body must not acquire an action'
        if name in ['disabled', 'hidden', 'empty', 'during-down-disable', 'during-down-remove', 'during-down-width']:
            assert all(event['state']['calls'] == [] for event in trace['events']), name
        if name in ['ordinary', 'rtl']:
            assert events['review']['calls'] == events['review-cancel']['calls'] == ['review']
        if name in ['multi', 'multi-direct']:
            assert events['archive']['calls'] == ['review', 'archive']
        if name in ['during-down-hold', 'during-down-title']:
            assert events['down']['calls'] == events['hold-or-update']['calls'] == []
            assert events['up']['calls'] == ['review']
    counter = {e['action']: e['state'] for e in traces['counter']['events']}
    assert counter['initial']['actionValues'] == {'counter': 0}
    assert counter['increment']['actionValues'] == counter['producer-update']['actionValues'] == {'counter': 1}
    assert counter['increment-after-update']['actionValues'] == {'counter': 2}
    assert counter['remove-actions']['actionValues'] == {}
    for name in ['restore-actions', 'restore-after-replacement', 'disabled-counter']:
        assert counter[name]['actionValues'] == {'counter': 0}
    assert counter['enabled-counter']['calls'] == ['counter'] * 4
    assert counter['enabled-counter']['appears'] == 3 and counter['enabled-counter']['disappears'] == 2
    return {'fixtures': 69, 'publicImages': 552, 'activityImages': 536, 'anchors': 16,
            'layoutQueries': 7072, 'nativeActionRectPairs': 8840, 'traces': 13, 'snapshots': 94,
            'cleanReplayIdenticalFiles': 1753}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
