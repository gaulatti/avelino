#!/usr/bin/env python3
"""Audit native Modal input facts and retain untrusted TextField pixels."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import tarfile
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/modal-input-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
SOURCE_SHA256 = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
ARCHIVE_SHA256 = '7ecf2f03510770e212135de0c6e33642a4d56785a2bd25049b031820f35c92c7'
QUARANTINE = {'outputs/sheet-editor-reopen.png', 'outputs/sheet-editor-reopen-again.png'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains(rect, x, y):
    return rect['x'] <= x < rect['x'] + rect['width'] and rect['y'] <= y < rect['y'] + rect['height']


def glyph_rect(frame, font_size, dpr):
    edge = math.ceil(font_size * 0.8 * dpr) / dpr
    inset = math.floor((16 - edge) / 2 * dpr + 0.5) / dpr
    snap = lambda value: math.floor(value * dpr + 0.5) / dpr
    return dict(x=snap(frame['x'] + (frame['width'] - 16) / 2 + inset),
                y=snap(frame['y'] + (frame['height'] - 16) / 2 + inset), width=edge, height=edge)


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['referenceRevision'] == REFERENCE and report['accepted'] is False
    assert report['approvedExceptions'] == [] and report['expectedImagesChanged'] is False
    assert report['fullReplayByteIdentity'] is False and report['sheetEditorWitnessTransparent'] is False
    assert set(report['pixelQuarantine']) == QUARANTINE
    assert report['sheetEditorTrustedGeometry'] == 'Close header only; first 154 physical rows are identical'
    assert all(report[key] == 'pending' for key in ['physicalInputAcceptance', 'focusedKeyboardAcceptance', 'screenReaderAcceptance'])
    files = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert files == set(report['files']) | {'investigation.json'}
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name
    inputs, tooling, build = (read(n) for n in ['inputs.json', 'tooling-provenance.json', 'source-build-result.json'])
    assert inputs['reference'] == tooling['reference'] == build['reference'] == REFERENCE
    assert set(inputs['files']) == {'reference-source.tar', 'replay.py', 'tool/Common.swift', 'tool/SheetSupport.swift', 'tool/InputMain.swift'}
    assert inputs['files']['reference-source.tar'] == tooling['sourceArchiveSha256'] == build['sourceArchiveSha256'] == SOURCE_SHA256
    assert tooling['sourceFiles'] == build['sourceFilesUnchanged'] == 89
    assert tooling['sourceTree'] == 'db61113381a51fc3c7b3d12786609cd9e76627c8'
    assert tooling['compiledInputs'] == [] and build['prebuiltLibraryInputs'] is False
    assert build['libraryBuiltFromSources'] is True and tooling['independentMachineAvailability'] == 'pending'
    assert tooling['sourceOnlyReplayArchiveSha256'] == ARCHIVE_SHA256
    assert tooling['sourceOnlyReplayMembers'] == sorted([*inputs['files'], 'inputs.json'])
    archive = Path(tooling['sourceOnlyReplayArchive'])
    if archive.exists():
        assert digest(archive) == ARCHIVE_SHA256
        with tarfile.open(archive) as source:
            assert sorted(source.getnames()) == tooling['sourceOnlyReplayMembers']
            for name, expected in inputs['files'].items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected

    replay = read('clean-replay.json')
    outputs = {n for n in files if n.startswith('outputs/')}
    assert len(outputs) == replay['files'] == report['sourceReplayFiles'] == 67
    assert replay['byteIdenticalFiles'] == report['sourceReplayIdenticalFiles'] == 65
    assert replay['fullByteIdentity'] is False and set(replay['mismatches']) == QUARANTINE
    assert len(replay['outputs']) == 67 and {r['file'] for r in replay['outputs']} == outputs
    for row in replay['outputs']:
        assert row['originalSha256'] == digest(directory / row['file'])
        if row['file'] not in QUARANTINE:
            assert row['identical'] and row['originalSha256'] == row['replaySha256']
        else:
            assert row['identical'] is False and row['originalSha256'] != row['replaySha256']
            assert row['replaySha256'] == digest(directory / row['replayPath'])
            assert row['fullPixelAcceptance'] == 'pending' and row['headerRowsPhysical'] == 154 and row['headerPixelIdentical']
            a, b = (Image.open(directory / name).convert('RGBA') for name in [row['file'], row['replayPath']])
            assert a.size == b.size == (960, 314)
            assert list(ImageChops.difference(a, b).convert('RGB').getbbox()) == row['differenceBounds'] == [34, 186, 926, 278]
            assert a.crop((0, 0, 960, 154)).tobytes() == b.crop((0, 0, 960, 154)).tobytes()

    used_pngs = set()

    def png(path, dimensions=None):
        used_pngs.add(path)
        data = (directory / path).read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        if dimensions is not None:
            assert struct.unpack('>II', data[16:24]) == dimensions
        return data

    data = read('outputs/input.json')
    assert data['reference'] == REFERENCE and data['complete'] is True
    groups = {g['configuration']['fixture']: g for g in data['groups']}
    names = {f'close-{w}-{direction}' for w, direction in itertools.product([0, 12, 80, 480], ['ltr', 'rtl'])}
    names |= {'disabled-12', 'disabled-480', 'wide', 'wide-disabled'}
    assert len(groups) == len(data['groups']) == report['groups'] == 12 and set(groups) == names
    for name, group in groups.items():
        config = group['configuration']
        pictures = [png('outputs/' + p, (config['width'] * 2, config['height'] * 2)) for p in group['paths']]
        assert group['publicProbedIdentical'] and group['publicWitnessIdentical']
        assert len(pictures) == 3 and pictures[0] == pictures[1] == pictures[2]
    queries = data['queries']
    assert len(queries) == report['clippingQueries'] == 170
    outside_activations = 0
    for name, group in groups.items():
        rows = [q for q in queries if q['fixture'] == name]
        config, parts = group['configuration'], group['parts']
        root = parts['root']
        wide = config['content'] == 'wide-button'
        target = parts['content-wide-button' if wide else 'close']
        xs = {-1, 0, 1, config['modalWidth'] / 2, config['modalWidth'] - 1, config['modalWidth'], config['modalWidth'] + 1}
        xs |= {target['x'] - root['x'] + target['width'] * fraction for fraction in [-0.01, 0, 0.1, 0.5, 0.9, 1, 1.01]}
        if wide:
            xs |= {-150, -20, 20, 460, 500, 630}
        assert len(rows) == len(xs) and len({r['xInModal'] for r in rows}) == len(rows)
        assert all(any(abs(x - row['xInModal']) < 1e-10 for x in xs) for row in rows)
        hit = target if wide else glyph_rect(target, 13, 2)
        for row in rows:
            x, y = row['point']['x'], row['point']['y']
            assert abs(x - root['x'] - row['xInModal']) < 1e-10 and y == target['y'] + target['height'] / 2
            assert row['insideModalRect'] == contains(root, x, y)
            assert row['insideTargetRect'] == contains(target, x, y)
            activated = contains(hit, x, y) and not config['disabled']
            assert row['calls'] == (['wide'] if wide and activated else [])
            assert row['windowVisible'] == (wide or not activated)
            assert not row['applicationActive']
            outside_activations += activated and not row['insideModalRect']
    assert outside_activations > 0, 'Visual clipping is not an input mask'
    # Four previous standalone public windows anchor the unchanged layout helper.
    original = ROOT / 'evidence/reference-investigations/modal-20261016/captures'
    for width, fixture in [(0, 'width-0'), (12, 'width-12'), (80, 'width-80'), (480, 'default')]:
        path = groups[f'close-{width}-ltr']['paths'][0]
        assert (directory / 'outputs' / path).read_bytes() == (original / f'{fixture}-light-text1.0-dpr2.0-mode0.png').read_bytes()

    profiles = read('outputs/hit-profiles.json')
    assert profiles['reference'] == REFERENCE and len(profiles['profiles']) == report['glyphProfiles'] == 4
    assert {(p['textScale'], p['dpr']) for p in profiles['profiles']} == set(itertools.product([1, 1.5], [1, 2]))
    assert sum(len(p['samples']) for p in profiles['profiles']) == report['glyphQueries'] == 568
    for profile in profiles['profiles']:
        scale, dpr = profile['textScale'], profile['dpr']
        pictures = [png('outputs/' + path, (960 * dpr, 900 * dpr)) for path in profile['paths']]
        assert profile['identical'] and pictures[0] == pictures[1]
        assert pictures[0] == (original / f'default-light-text{scale:.1f}-dpr{dpr:.1f}-mode0.png').read_bytes()
        frame, samples = profile['closeFrame'], profile['samples']
        hit = glyph_rect(frame, 13 if scale == 1 else 20, dpr)
        assert len(samples) == 142
        for sample in samples:
            assert sample['activated'] == contains(hit, frame['x'] + frame['width'] / 2 + sample['x'], frame['y'] + frame['height'] / 2 + sample['y'])
        assert [(s['x'], s['y']) for s in samples[-81:]] == list(itertools.product([-10, -8, -6, -4, 0, 4, 6, 8, 10], repeat=2))
        assert samples[0] == dict(x=0, y=0, activated=True)
        index = 1
        for name, x_sign, y_sign in [('left', -1, 0), ('right', 1, 0), ('top', 0, -1), ('bottom', 0, 1)]:
            inside, outside = 0, 24
            assert samples[index] == dict(x=24 * x_sign, y=24 * y_sign, activated=False)
            index += 1
            for _ in range(14):
                mid = (inside + outside) / 2
                sample = samples[index]
                assert sample['x'] == mid * x_sign and sample['y'] == mid * y_sign
                if sample['activated']:
                    inside = mid
                else:
                    outside = mid
                index += 1
            assert profile['bounds'][name] == dict(inside=inside, outside=outside)

    traces = {t['id']: t for t in data['traces']}
    assert set(traces) == {'retained-window', 'sheet-counter', 'sheet-editor'}
    assert len(data['traces']) == report['reopeningTraces'] == 3
    assert sum(len(t['events']) for t in traces.values()) == report['reopeningSnapshots'] == 20
    window = traces['retained-window']['events']
    assert [e['visible'] for e in window] == [True, True, False, True, True, False]
    assert [e['calls'] for e in window] == [[], ['counter:1'], ['counter:1'], ['counter:1'], ['counter:1', 'counter:2'], ['counter:1', 'counter:2']]
    assert all(e['appears'] == 1 and e['disappears'] == 0 and e['mountValues'] == [0] for e in window)
    for event in window:
        png('outputs/' + event['path'], (1920, 1800))
    for name in ['sheet-counter', 'sheet-editor']:
        trace = traces[name]
        a, b = (png('outputs/' + p, (960, 306 if name == 'sheet-counter' else 314)) for p in trace['proofPaths'])
        assert trace['proofIdentical'] == (name == 'sheet-counter') == (a == b)
        assert trace['headerPixelIdentical'] and trace['headerRowsPhysical'] == 154
        images = [Image.open(directory / 'outputs' / p).convert('RGBA') for p in trace['proofPaths']]
        assert images[0].crop((0, 0, 960, 154)).tobytes() == images[1].crop((0, 0, 960, 154)).tobytes()
        states = [e['state'] for e in trace['events']]
        assert [s['presented'] for s in states] == [True, True, False, True, True, False, True]
        assert [s['sheetCount'] for s in states] == [1, 1, 0, 1, 1, 0, 1]
        assert [s['sheetDismissCount'] for s in states] == [0, 0, 1, 1, 1, 2, 2]
        assert all(s['parentVisible'] and not s['applicationActive'] for s in states)
        for event in trace['events']:
            if 'path' in event:
                png('outputs/' + event['path'], (960, 306 if name == 'sheet-counter' else 314))
    counter = traces['sheet-counter']['events']
    assert [e['state']['calls'] for e in counter] == [[], ['counter:1'], ['counter:1'], ['counter:1'], ['counter:1', 'counter:1'], ['counter:1', 'counter:1'], ['counter:1', 'counter:1']]
    assert [e['state']['mountValues'] for e in counter] == [[0]] * 3 + [[0, 0]] * 3 + [[0, 0, 0]]
    assert all(e['state']['disappears'] == 0 for e in counter), 'Source callback is not QObject destruction evidence'
    assert [e['text'] for e in traces['sheet-editor']['events']] == ['Draft edition'] + ['Caller retains this edition'] * 3 + ['Caller changes the reopened edition'] * 3
    limit = read('outputs/witness-limit.json')
    assert limit['suitableForFullSheetPixelAcceptance'] is False and limit['headerPixelIdentical']
    assert used_pngs == {p for p in outputs if p.endswith('.png')}
    assert len(used_pngs) == 64
    return dict(clippingQueries=170, glyphQueries=568, reopeningSnapshots=20,
                replayFiles=67, byteIdenticalFiles=65, quarantinedImages=2, accepted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
