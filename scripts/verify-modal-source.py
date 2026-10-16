#!/usr/bin/env python3
"""Audit native Modal observations without approving a Linux implementation."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/modal-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
SOURCE_SHA256 = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
ARCHIVE_SHA256 = '0cea0f70a6e2f159f45f3ea32fefb25ca5334c520918fc8c33b4e8da75669416'
FIXTURES = set('''default title-empty title-long title-lines unicode bidi width-0 width-12
width-80 width-108 width-160 width-240 width-640 offer-0 offer-160 offer-800
content-empty content-zero content-hidden content-tall content-wide content-fills content-text
content-text-empty content-text-lines content-inherited content-multi content-vstack content-hstack
content-counter content-editor disabled rtl rtl-narrow parent-font32 parent-red'''.split())
TRACE_IDS = {'counter-lifecycle', 'editor-binding', 'ordinary', 'disabled', 'rtl',
             *('during-down-' + kind for kind in ['hold', 'disable', 'remove', 'width', 'title']),
             *('sheet-' + kind for kind in ['close', 'disabled-close', 'escape', 'outside'])}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['referenceRevision'] == REFERENCE and report['accepted'] is False
    assert report['approvedExceptions'] == [] and report['expectedImagesChanged'] is False
    assert report['linuxImplementation'] == 'pending'
    assert report['physicalInputAcceptance'] == report['screenReaderAcceptance'] == 'pending'
    assert report['remountPointerActivation'] == 'observed while containing window is visible'
    assert report['postDismissalInputEvidence'] == 'excluded: containing window is hidden'
    assert report['inactiveAccessibilityChildrenAvailable'] is False
    assert report['sheetCaptureScope'] == 'content view bounds; outer window chrome and shadow excluded'
    files = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert files == set(report['files']) | {'investigation.json'}, 'Missing or extra native evidence'
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name

    inputs, tooling, build = (read(name) for name in ['inputs.json', 'tooling-provenance.json', 'source-build-result.json'])
    assert inputs['reference'] == tooling['reference'] == build['reference'] == REFERENCE
    assert set(inputs['files']) == {'reference-source.tar', 'replay.py', 'tool/Common.swift', 'tool/CaptureMain.swift', 'tool/BehaviorMain.swift'}
    assert inputs['files']['reference-source.tar'] == tooling['sourceArchiveSha256'] == build['sourceArchiveSha256'] == SOURCE_SHA256
    assert tooling['sourceTree'] == 'db61113381a51fc3c7b3d12786609cd9e76627c8'
    assert tooling['sourceFiles'] == build['sourceFilesUnchanged'] == 89
    assert build['libraryBuiltFromSources'] is True and build['prebuiltLibraryInputs'] is False
    assert tooling['compiledInputs'] == [] and tooling['independentMachineAvailability'] == 'pending'
    assert tooling['sourceOnlyReplayArchiveSha256'] == ARCHIVE_SHA256
    assert tooling['sourceOnlyReplayMembers'] == sorted([*inputs['files'], 'inputs.json'])
    archive = Path(tooling['sourceOnlyReplayArchive'])
    if archive.exists():
        assert digest(archive) == ARCHIVE_SHA256
        with tarfile.open(archive) as source:
            assert sorted(m.name for m in source.getmembers()) == tooling['sourceOnlyReplayMembers']
            for name, expected in inputs['files'].items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected, name

    replay = read('clean-replay.json')
    outputs = {name for name in files if name.startswith(('captures/', 'behavior/'))}
    assert replay['files'] == replay['byteIdenticalFiles'] == report['sourceReplayIdenticalFiles'] == 977
    assert replay['mismatches'] == [] and len(replay['outputs']) == 977
    assert {row['file'] for row in replay['outputs']} == outputs
    for row in replay['outputs']:
        assert row['originalSha256'] == row['replaySha256'] == digest(directory / row['file']), row['file']
    continuity = read('capture-continuity.json')
    assert continuity['files'] == continuity['byteIdenticalFiles'] == len(continuity['outputs']) == 865
    assert continuity['mismatches'] == []
    assert {r['file'] for r in continuity['outputs']} == {n for n in outputs if n.startswith('captures/')}
    for row in continuity['outputs']:
        assert row['originalSha256'] == row['currentSha256'] == digest(directory / row['file'])

    used_pngs = set()

    def png(name, width=None, height=None):
        used_pngs.add(name)
        data = (directory / name).read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        dimensions = struct.unpack('>II', data[16:24])
        if width is not None:
            assert dimensions == (width, height), (name, dimensions)
        return data

    source = read('captures/captures.json')
    assert source['reference'] == REFERENCE and source['fixtures'] == len(FIXTURES) == 36
    rows = source['captures']
    identity = lambda r: (r['configuration']['fixture'], r['appearance'], r['textScale'], r['dpr'])
    lookup = {identity(row): row for row in rows}
    assert len(rows) == len(lookup) == report['publicCaptureCases'] == 288
    assert set(lookup) == set(itertools.product(FIXTURES, ['light', 'dark'], [1, 1.5], [1, 2]))
    for row in rows:
        f, dpr = row['configuration'], row['dpr']
        assert row['publicProbedIdentical'] and row['publicWitnessIdentical']
        images = [png('captures/' + path, f['width'] * dpr, f['height'] * dpr) for path in row['paths']]
        assert len(images) == 3 and images[0] == images[1] == images[2]
        for state in [row['probed'], row['witness']]:
            assert state['backingDpr'] == 2 and not state['key'] and not state['main'] and not state['applicationActive']
            assert state['calls'] == []
        parts, actual = row['witness']['parts'], row['probed']['parts']
        assert all(parts[k] == v for k, v in actual.items())
        root, header, line = (parts[k] for k in ['root', 'header', 'separator'])
        assert root['width'] == f['modalWidth']
        assert root['x'] + root['width'] / 2 == f['width'] / 2
        assert root['y'] + root['height'] / 2 == f['height'] / 2
        assert 0 <= root['y'] <= root['y'] + root['height'] <= f['height']
        assert header['width'] == max(92, f['modalWidth'])
        assert header['height'] == 40 + max(36, parts['title']['height'])
        assert parts['close']['width'] == 44 and parts['close']['height'] == 36
        assert line == dict(x=root['x'], y=root['y'] + header['height'], width=f['modalWidth'], height=1)
        assert parts['spacer']['width'] >= 8 and parts['spacer']['height'] == 0
        assert sum(parts[k]['width'] for k in ['title', 'spacer', 'close']) == parts['header-row']['width']
        content = sorted((v for k, v in parts.items() if k.startswith('content-')), key=lambda v: v['y'])
        position = line['y'] + 1
        for child in content:
            assert child['x'] + child['width'] / 2 == root['x'] + root['width'] / 2
            assert child['y'] == position + 20
            position += child['height'] + 40
        assert root['y'] + root['height'] == position, 'Flattened children each receive padding'
        for part in parts.values():
            assert all(math.isfinite(v) for v in part.values())
        base = lookup[('default', row['appearance'], row['textScale'], dpr)]
        if f['fixture'].startswith('offer-'):
            assert images[0] == (directory / 'captures' / base['paths'][0]).read_bytes()
        if f['fixture'] == 'parent-font32':
            assert all(parts['title'][k] == base['witness']['parts']['title'][k] for k in ['width', 'height'])
        other_scale = lookup[(f['fixture'], row['appearance'], 2.5 - row['textScale'], dpr)]
        assert parts['title']['width'] == other_scale['witness']['parts']['title']['width']
        assert parts['title']['height'] == other_scale['witness']['parts']['title']['height']

    heights = {'default': 197, 'content-empty': 77, 'content-zero': 117, 'content-hidden': 197,
               'content-tall': 437, 'content-multi': 217, 'content-vstack': 182, 'content-hstack': 161,
               'content-text-empty': 131, 'width-0': 414, 'width-12': 414, 'width-80': 414}
    for key, value in heights.items():
        assert lookup[(key, 'light', 1, 1)]['witness']['parts']['root']['height'] == value
    assert lookup[('content-wide', 'light', 1, 1)]['witness']['parts']['content-wide']['width'] == 800
    assert lookup[('content-fills', 'light', 1, 1)]['witness']['parts']['content-fills']['width'] == 440
    assert lookup[('content-editor', 'light', 1.5, 1)]['witness']['parts']['content-editor']['height'] == 60

    sheet_captures = read('behavior/sheet-captures.json')
    assert sheet_captures['reference'] == REFERENCE and len(sheet_captures['captures']) == 3
    assert {r['configuration']['fixture'] for r in sheet_captures['captures']} == {'sheet-capture-ordinary', 'sheet-capture-disabled', 'sheet-capture-rtl'}
    for row in sheet_captures['captures']:
        assert row['publicProbedIdentical'] and row['publicWitnessIdentical']
        images = [png('behavior/' + path, 960, 306) for path in row['paths']]
        assert images[0] == images[1] == images[2]
        assert all(state['presented'] and state['sheetCount'] == 1 for state in row['states'])

    behavior = read('behavior/behavior.json')
    assert behavior['reference'] == REFERENCE
    traces = {t['id']: t for t in behavior['traces']}
    assert len(behavior['traces']) == len(traces) == report['behaviorTraces'] == 14 and set(traces) == TRACE_IDS
    assert sum(len(t['events']) for t in traces.values()) == report['behaviorSnapshots'] == 60
    for trace in traces.values():
        assert len({e['action'] for e in trace['events']}) == len(trace['events'])
        for proof in trace.get('targetProofs', []):
            assert proof['identical']
            assert png('behavior/' + proof['publicPath'], 1920, 1800) == png('behavior/' + proof['witnessPath'], 1920, 1800)
        for event in trace['events']:
            state = event['state']
            assert not state['applicationActive']
            # The inactive host exposes only its group. This is no reader proof.
            assert len(state['accessibility']) in [0, 1]
            if trace['presentation'] == 'embedded':
                assert not state['key'] and not state['main']
                dismissed = event['action'] == 'embedded-close' and not trace['initialConfiguration']['disabled']
                assert state['windowVisible'] == (not dismissed), 'Close dismisses the hosting window; other inputs run before dismissal'
            if 'path' in event:
                png('behavior/' + event['path'], *( (1920, 1800) if trace['presentation'] == 'embedded' else (int(event['width'] * 2), int(event['height'] * 2)) ))

    lifecycle = traces['counter-lifecycle']['events']
    expected_calls = [[], ['counter:1'], ['counter:1'], ['counter:1', 'counter:2'], ['counter:1', 'counter:2']]
    third = ['counter:1', 'counter:2', 'counter:3']
    expected_calls += [third] * 3 + [third + ['counter:1']] * 3 + [third + ['counter:1', 'counter:1']] * 2
    assert [e['state']['calls'] for e in lifecycle] == expected_calls
    assert lifecycle[-1]['action'] == 'embedded-close'
    assert (directory / 'behavior' / lifecycle[-2]['path']).read_bytes() == (directory / 'behavior' / lifecycle[-1]['path']).read_bytes(), 'A cached hidden view can still render; window visibility is separate evidence'
    assert [(e['state']['appears'], e['state']['disappears']) for e in lifecycle] == [(1, 0)] * 6 + [(1, 1), (2, 1), (2, 1), (2, 2), (3, 2), (3, 2), (3, 2)]
    assert [e['state']['mountValues'] for e in lifecycle] == [[0]] * 7 + [[0, 0]] * 3 + [[0, 0, 0]] * 3
    editor = traces['editor-binding']['events']
    assert [e['state']['text'] for e in editor] == ['Draft edition'] + ['Producer renamed edition'] * 3
    for key in ['ordinary', 'disabled', 'rtl']:
        assert all(e['state']['calls'] == [] and e['state']['mounted'] for e in traces[key]['events'])
    for kind in ['hold', 'disable', 'remove', 'width', 'title']:
        events = traces['during-down-' + kind]['events']
        assert all(e['state']['calls'] == [] for e in events[:-1])
        assert events[-1]['state']['calls'] == ([] if kind in ['disable', 'remove'] else ['counter:1'])
    for kind in ['close', 'disabled-close', 'escape', 'outside']:
        events = traces['sheet-' + kind]['events']
        first, last = (e['state'] for e in events)
        assert first['presented'] and first['sheetCount'] == 1 and first['sheetDismissCount'] == 0
        assert last['parentVisible'] and last['calls'] == []
        assert (last['presented'], last['sheetCount'], last['sheetDismissCount']) == ((False, 0, 1) if kind == 'close' else (True, 1, 0))
        if kind in ['close', 'disabled-close']:
            event = events[-1]
            assert event['action'] == 'close-click' and event['targetPNGIdentical']
            assert png('behavior/' + event['targetPublicPath'], 960, 306) == png('behavior/' + event['targetWitnessPath'], 960, 306)
    assert sum(len(t.get('targetProofs', [])) for t in traces.values()) == report['embeddedTargetPairs'] == 19
    assert len([n for n in used_pngs if n.startswith('captures/')]) == 864
    assert len([n for n in used_pngs if n.startswith('behavior/')]) == 110
    assert used_pngs == {n for n in outputs if n.endswith('.png')}

    diagnostic = read('diagnostics/inactive-ax-attempt/behavior.json')
    for trace in diagnostic['traces']:
        if trace['id'] in ['sheet-close', 'sheet-disabled-close']:
            assert trace['events'][-1]['action'] == 'close-target-unavailable'
            assert trace['events'][-1]['state']['presented']
    assert read('diagnostics/inactive-ax-attempt/result.json')['suitableForCloseBehaviorAcceptance'] is False
    post_close = read('diagnostics/post-dismissal-input-attempt/behavior.json')
    trace = next(t for t in post_close['traces'] if t['id'] == 'counter-lifecycle')
    close_at = next(i for i, e in enumerate(trace['events']) if e['action'] == 'embedded-close')
    assert all(not e['state']['windowVisible'] for e in trace['events'][close_at:])
    assert trace['events'][-1]['state']['calls'] == ['counter:1', 'counter:2', 'counter:3']
    assert read('diagnostics/post-dismissal-input-attempt/result.json')['suitableForRemountPointerAcceptance'] is False
    return dict(captures=len(rows), behaviorTraces=len(traces), behaviorSnapshots=60,
                replayFiles=977, accepted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
