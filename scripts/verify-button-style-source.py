#!/usr/bin/env python3
"""Audit pinned ButtonStyle pixels, per-view geometry and bounded input claims."""
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import tarfile

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/button-style-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
SOURCE_SHA = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
VARIANTS = ['primary', 'secondary', 'outline', 'subtle', 'ghost', 'link', 'destructive']
SIZES = ['xs', 'sm', 'md', 'lg']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(directory, name):
    return json.loads((directory / name).read_text())


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def geometry(row):
    f = row['configuration']
    state = row['states'][1]
    parts = state['partInstances']
    if f['content'] == 'empty':
        assert parts == {} and state['mountValues'] == []
        return
    assert state['mountValues'] == [0]
    multiple = f['content'] == 'multi'
    label_keys = ['first', 'second'] if multiple else ['label']
    expected = {'body', 'root', *label_keys}
    if f['parentLayout'] != 'zstack':
        expected.update(['leading', 'trailing', 'parent'])
    assert set(parts) == expected
    for key, values in parts.items():
        assert isinstance(values, list) and values
        assert values == sorted(values, key=lambda r: tuple(r[k] for k in ['x', 'y', 'width', 'height']))
        for rect in values:
            assert set(rect) == {'x', 'y', 'width', 'height'}
            assert all(finite(v) for v in rect.values())
            assert rect['width'] >= 0 and rect['height'] >= 0
        assert len(values) == (2 if multiple and key in ['body', 'root'] else 1)
    padding = dict(xs=10, sm=14, md=18, lg=24)[f['size']]
    minimum = 0 if f['variant'] == 'link' else dict(xs=28, sm=36, md=40, lg=48)[f['size']]
    labels = [parts[key][0] for key in label_keys]
    assert Counter((b['width'], b['height']) for b in parts['body']) == Counter(
        (r['width'] + 2 * padding, max(minimum, r['height'])) for r in labels)
    if f['offer'] is None:
        assert parts['root'] == parts['body']
    else:
        assert len(parts['root']) == 1
        assert parts['root'][0]['width'] == f['offer']
        assert parts['root'][0]['height'] == parts['body'][0]['height']
    if f['parentLayout'] == 'zstack':
        for box in parts['body'] + parts['root']:
            assert box['x'] == (640 - box['width']) / 2
            assert box['y'] == (400 - box['height']) / 2
    else:
        parent = parts['parent'][0]
        assert parent['x'] == (640 - parent['width']) / 2
        assert parent['y'] == (400 - parent['height']) / 2
        leading, trailing = parts['leading'][0], parts['trailing'][0]
        assert (leading['width'], leading['height']) == (40, 12)
        assert (trailing['width'], trailing['height']) == (30, 20)
        axis = 'x' if f['parentLayout'] == 'hstack' else 'y'
        extent = 'width' if axis == 'x' else 'height'
        cross = 'height' if axis == 'x' else 'width'
        bodies = sorted(parts['body'], key=lambda r: r[axis])
        sequence = [leading, *bodies, trailing]
        assert parent[extent] == sum(r[extent] for r in sequence) + 11 * (len(sequence) - 1)
        assert parent[cross] == max(r[cross] for r in sequence)
        cursor = parent[axis]
        for box in sequence:
            assert box[axis] == cursor
            cursor += box[extent] + 11


def diagnostic(directory, version, probe_matches):
    folder = directory / f'diagnostics/v{version}'
    index = load(folder, 'archive-files.json')
    assert index['fileCount'] == 2017 and index['compiledInputs'] == []
    assert digest(folder / 'capture-data.tar.gz') == index['sha256']
    with tarfile.open(folder / 'capture-data.tar.gz') as archive:
        members = archive.getmembers()
        assert len(members) == len({m.name for m in members}) == 2017
        assert all(m.isfile() and (m.name == 'captures.json' or m.name.endswith('.png')) and '/' not in m.name for m in members)
        data = {m.name: archive.extractfile(m).read() for m in members}
    assert set(data) == set(index['members'])
    assert all(hashlib.sha256(data[n]).hexdigest() == sha for n, sha in index['members'].items())
    rows = json.loads(data['captures.json'])['captures']
    assert len(rows) == 672
    assert sum(data[r['paths'][0]] == data[r['paths'][1]] for r in rows) == probe_matches
    assert all(data[r['paths'][0]] == data[r['paths'][2]] for r in rows)
    if version == 1:
        classification = load(folder, 'classification.json')
        assert classification['excluded'] and classification['accepted'] is False
    else:
        assert load(folder, 'geometry-classification.json')['lastWriterGeometryIsAggregate'] is False


def pointer_input(directory, name, active, deltas, corner_index):
    folder = directory / name
    state = load(folder, 'state.json')
    observations = load(folder, 'observations.json')
    pressed = load(folder, 'row-pressed-analysis.json')
    assert state['reference'] == REFERENCE and state['accepted'] is False
    assert observations['accepted'] is False and observations['visualClipIsInputClip'] is False
    assert observations['applicationActiveFlags'] == sorted({c['applicationActive'] for c in state['captures']})
    assert observations['keyWindowFlags'] == sorted({c['windowKey'] for c in state['captures']})
    captures = {c['path']: c for c in state['captures']}
    assert len(captures) == len(state['captures'])
    assert set(captures) == {p.name for p in folder.glob('*.png')}
    for capture in captures.values():
        assert capture['calls'] == list(range(1, capture['count'] + 1))
        assert capture['backingDpr'] == 2
    events = [e for e in state['events'] if e['fixture'] == 'multi-parent-hstack' and e['insideCanvas']]
    assert len(events) == 2 * len(deltas)
    phases = observations['rowPointerPhases']
    assert len(phases) == len(deltas)
    for index, phase in enumerate(phases):
        down, up = events[2 * index:2 * index + 2]
        assert down['type'] == 1 and up['type'] == 2
        after = events[2 * index + 2]['countBeforeDelivery'] if 2 * index + 2 < len(events) else state['count']
        assert phase == dict(downPoint=down['canvasPoint'], upPoint=up['canvasPoint'],
                             downTime=down['time'], upTime=up['time'], duration=up['time'] - down['time'],
                             before=down['countBeforeDelivery'], after=after, delta=after - down['countBeforeDelivery'])
        assert phase['delta'] == deltas[index]
    assert phases[0]['downPoint'] == dict(x=265.5, y=200)
    assert phases[1]['downPoint'] == dict(x=395, y=200)
    assert phases[2]['downPoint'] == phases[0]['downPoint'] and phases[2]['upPoint'] == phases[1]['downPoint']
    baseline = next(c for c in state['captures'] if c['fixture']['fixture'] == 'multi-parent-hstack')
    assert pressed['baseline'] == baseline['path'] and pressed['accepted'] is False
    base = Image.open(folder / pressed['baseline']).convert('RGB')
    assert len(pressed['phases']) == 2
    for index, observation in enumerate(pressed['phases']):
        phase = phases[index]
        sample = captures[observation['sample']]
        assert observation['downTime'] == phase['downTime'] and observation['upTime'] == phase['upTime']
        assert observation['duration'] == phase['duration'] >= 1.4
        assert observation['canvasPoint'] == phase['downPoint']
        assert phase['downTime'] + .19 < sample['time'] < phase['upTime']
        assert observation['sampleAfterDown'] == sample['time'] - phase['downTime']
        assert observation['countDuringHold'] == sample['count'] == phase['before']
        assert observation['applicationActive'] == sample['applicationActive'] == active
        assert observation['windowKey'] == sample['windowKey'] == active
        diff = ImageChops.difference(base, Image.open(folder / observation['sample']).convert('RGB'))
        assert observation['leftChanged'] == bool(diff.crop((403, 356, 660, 446)).getbbox()) is True
        assert observation['rightChanged'] == bool(diff.crop((682, 356, 898, 446)).getbbox()) is True
        assert observation['changedBounds'] == list(diff.getbbox())
    assert observations['changesBothBodiesForEitherTarget'] and observations['sharedPressedPixelsByteIdentical']
    assert observations['callerActionSharedAcrossTwoAXButtons']
    assert (folder / pressed['phases'][0]['sample']).read_bytes() == (folder / pressed['phases'][1]['sample']).read_bytes()
    corner = observations['transparentVisualCorner']
    assert corner['pixel'] == [403, 361] and corner['rgba'] == [255, 255, 255, 255]
    assert list(Image.open(folder / baseline['path']).convert('RGBA').getpixel(tuple(corner['pixel']))) == corner['rgba']
    assert corner['canvasPoint'] == phases[corner_index]['downPoint'] == dict(x=201.5, y=180.5)
    assert corner['heldDuration'] == phases[corner_index]['duration'] >= .95
    assert corner['activationDelta'] == phases[corner_index]['delta'] == 1
    counter_commands = [c for c in state['commands'] if c['fixture'] == 'content-counter' and 'count' in c]
    count = 1 if active else 2
    assert next(c for c in counter_commands if c['action'] == 'variant')['count'] == 1
    assert all(c['count'] == count for c in counter_commands if c['action'] == 'disabled')
    assert next(c for c in counter_commands if c['action'] == 'unmount')['count'] == count
    assert all(c['count'] == sum(deltas) and c['calls'] == list(range(1, sum(deltas) + 1))
               for c in state['commands'] if c['action'] in ['theme', 'quit'])
    if active:
        assert all(c['applicationActive'] and c['windowKey'] for c in captures.values()
                   if c['fixture']['fixture'] == 'multi-parent-hstack')
        runtime = load(folder, 'runtime-inputs.json')
        assert runtime['sourceBuildResultSha256'] == digest(directory / 'input-clean-build/source-build-result.json')
        assert runtime['nativeAppActiveAndKeyAfterCUATab']
    assert load(folder, 'termination.json')['terminated']


def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = load(directory, 'investigation.json')
    assert report['referenceRevision'] == REFERENCE and report['sourceArchiveSha256'] == SOURCE_SHA
    assert report['accepted'] is False and report['approvedExceptions'] == []
    for key in ['activeWindowKeyboardAcceptance', 'readerAcceptance', 'linuxAcceptance']:
        assert report[key] == 'pending'
    assert report['fixtures'] == 88 and report['closedGroups'] == 704 and report['sourceOnlyReplayFiles'] == 2113
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name != 'investigation.json'}
    assert actual == set(report['files'])
    assert all(digest(directory / n) == sha for n, sha in report['files'].items())
    source = load(directory, 'captures/captures.json')
    assert source['reference'] == REFERENCE and source['fixtures'] == 88 and source['peakWindows'] == 1
    rows = source['captures']
    contexts = {(r['configuration']['fixture'], r['appearance'], r['textScale'], r['dpr']) for r in rows}
    fixtures = {r['configuration']['fixture'] for r in rows}
    assert len(rows) == len(contexts) == 704 and len(fixtures) == 88
    assert contexts == set(itertools.product(fixtures, ['light', 'dark'], [1, 1.5], [1, 2]))
    definitions = {}
    for row in rows:
        f = row['configuration']
        assert f['variant'] in VARIANTS and f['size'] in SIZES
        assert f['parentLayout'] in ['zstack', 'hstack', 'vstack']
        assert f['offer'] is None or finite(f['offer']) and f['offer'] >= 0
        assert f['width'] == 640 and f['height'] == 400 and isinstance(f['text'], str)
        if f['fixture'] in definitions:
            assert definitions[f['fixture']] == f
        definitions[f['fixture']] = f
        assert row['publicProbedIdentical'] and row['publicWitnessIdentical']
        paths = row['paths']
        assert len(paths) == 3 and len(set(paths)) == 3
        images = [(directory / 'captures' / name).read_bytes() for name in paths]
        assert images[0] == images[1] == images[2]
        assert struct.unpack('>II', images[0][16:24]) == (640 * row['dpr'], 400 * row['dpr'])
        a, b, c = row['states']
        assert a['partInstances'] == {} and b == c
        assert {k: v for k, v in a.items() if k != 'partInstances'} == {k: v for k, v in b.items() if k != 'partInstances'}
        for state in [a, b, c]:
            assert state['calls'] == [] and state['count'] == state['disappears'] == 0
            assert state['applicationActive'] is False and state['windowKey'] is False
            assert state['windowVisible'] and state['backingDpr'] == 2
        geometry(row)
    for variant, size, disabled in itertools.product(VARIANTS, SIZES, [False, True]):
        name = 'default' if (variant, size, disabled) == ('primary', 'md', False) else f'{variant}-{size}-{"disabled" if disabled else "enabled"}'
        f = definitions[name]
        assert (f['variant'], f['size'], f['disabled'], f['content'], f['text']) == (variant, size, disabled, 'text', 'Review')
    assert definitions['content-empty']['content'] == 'empty'
    assert definitions['content-zero']['content'] == 'zero'
    assert definitions['content-hidden']['content'] == 'hidden'
    assert definitions['offer-0']['offer'] == 0
    for row in rows:
        parts = row['states'][1]['partInstances']
        name = row['configuration']['fixture']
        if name in ['content-zero', 'content-hidden']:
            width, height = (0, 0) if name == 'content-zero' else (200, 80)
            assert (parts['label'][0]['width'], parts['label'][0]['height']) == (width, height)
        if name == 'offer-0' and row['textScale'] == 1:
            assert (parts['body'][0]['width'], parts['body'][0]['height']) == (36, 102)
            assert (parts['root'][0]['width'], parts['root'][0]['height']) == (0, 102)
    replay = load(directory, 'clean-replay.json')
    assert replay['accepted'] is False and replay['compiledInputs'] == []
    expected_outputs = {str(p.relative_to(directory / 'captures')) for p in (directory / 'captures').iterdir() if p.is_file()}
    assert replay['identicalFiles'] == len(replay['outputs']) == 2113
    assert {r['file'] for r in replay['outputs']} == expected_outputs
    for record in replay['outputs']:
        assert record['originalSha256'] == record['replaySha256'] == digest(directory / 'captures' / record['file'])
    provenance = load(directory, 'tooling-provenance.json')
    assert provenance['compiledInputs'] == [] and provenance['automaticLivePixelReplay'] is False
    assert provenance['sourceArchiveSha256'] == SOURCE_SHA
    for name in ['source-build-result.json', 'clean-build/source-build-result.json', 'input-clean-build/source-build-result.json']:
        build = load(directory, name)
        assert build['sourceFilesUnchanged'] == 89 and build['libraryBuiltFromSources'] and build['prebuiltLibraryInputs'] is False
    assert load(directory, 'input-clean-build/source-build-result.json')['automaticLivePixelReplay'] is False
    continuity = load(directory, 'public-continuity.json')
    assert continuity['publicBodyContinuityFromV2'] == 672 and continuity['matchingProbeWitnessStateMaps'] == 704
    assert all(digest(directory / 'captures' / n) == sha for n, sha in continuity['files'].items())
    pointer_input(directory, 'input', False, [1, 1, 0, 1, 1, 0, 0], 4)
    pointer_input(directory, 'input-key-window', True, [1, 1, 0, 1, 0, 0], 3)
    diagnostic(directory, 1, 134)
    diagnostic(directory, 2, 672)
    return dict(closedGroups=704, sourceReplayFiles=2113, repeatedPartContexts=24, pointerPhases=13, accepted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
