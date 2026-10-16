#!/usr/bin/env python3
"""Audit native proposal/history measurements without approving Linux parity."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/activity-layout-mechanics-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
SOURCE_SHA256 = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['referenceRevision'] == REFERENCE and report['accepted'] is False
    assert report['approvedExceptions'] == [] and report['expectedImagesChanged'] is False
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert actual == set(report['files']) | {'investigation.json'}
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name
    inputs, provenance, build = (read(name) for name in ['inputs.json', 'tooling-provenance.json', 'source-build-result.json'])
    assert inputs['reference'] == provenance['reference'] == build['reference'] == REFERENCE
    assert set(inputs['files']) == {'reference-source.tar', 'replay.py', 'tool/MechanicsFixed.swift',
                                   'tool/PushOutMetrics.swift', 'tool/ActionMain.swift', 'tool/BucketMain.swift'}
    assert inputs['files']['reference-source.tar'] == provenance['sourceArchiveSha256'] == build['sourceArchiveSha256'] == SOURCE_SHA256
    assert provenance['sourceFiles'] == build['sourceFilesUnchanged'] == 89
    assert provenance['compiledInputs'] == [] and provenance['independentMachineAvailability'] == 'pending'
    assert provenance['sourceTree'] == 'db61113381a51fc3c7b3d12786609cd9e76627c8'
    assert provenance['sourceOnlyReplayMembers'] == sorted([*inputs['files'], 'inputs.json'])
    assert provenance['sourceOnlyReplayArchiveSha256'] == 'c50f37c948e96d6164c3bd8674c71993d91d50a9b8edd0b0627b8bc6310a0909'
    assert build['libraryBuiltFromSources'] is True and build['prebuiltLibraryInputs'] is False
    replay = read('clean-replay.json')
    assert replay['files'] == replay['byteIdenticalFiles'] == report['sourceReplayIdenticalFiles'] == 156 and replay['mismatches'] == []
    outputs = replay['outputs']
    expected = {name for name in actual if name.startswith(('text/', 'actions/', 'buckets/'))}
    assert len(outputs) == 156 and {row['file'] for row in outputs} == expected
    for row in outputs:
        assert row['originalSha256'] == row['replaySha256'] == digest(directory / row['file'])

    original = json.loads((ROOT / 'evidence/reference-investigations/activity-text-20261016/queries.json').read_text())
    lookup = {(r['key'], r['textScale'], r['proposalWidth'], r['dpr']): r for r in original['queries']}
    text = read('text/fixed-queries.json')
    assert text['reference'] == REFERENCE and len(text['rows']) == report['publicTextQueries'] == 3374
    keys = set()
    height_matches = width_matches = 0
    for row in text['rows']:
        key = 'title' if row['style'] == 'primary14' else 'detail' if row['style'] == 'secondary12' else 'timestamp' if row['style'] == 'secondary10' else row['text'].lower()
        scale = 1.5 if row['style'] == 'primary20' else 1
        identity = (key, scale, row['proposalWidth'], row['dpr'])
        keys.add(identity)
        source = lookup[identity]
        assert row['text'] == source['text'] and row['native'] == {key: source['rect'][key] for key in ['width', 'height']}
        assert row['nsPushOut'] == row['nsStandard']
        assert ''.join(line['text'] for line in row['nsPushOut']) == row['text']
        height = sum(line['height'] for line in row['nsPushOut'])
        width = math.ceil(max(line['width'] for line in row['nsPushOut']) * row['dpr']) / row['dpr']
        height_matches += height == row['native']['height']
        width_matches += width == row['native']['width']
    assert keys == set(lookup), 'Public Text coverage changed'
    assert height_matches == 3370 and width_matches == 3360, 'AppKit proxy cannot claim complete SwiftUI equivalence'

    paragraphs = read('text/pushout-metrics.json')['rows']
    assert len(paragraphs) == report['appKitParagraphQueries'] == 5400
    grouped = {}
    for row in paragraphs:
        key = (row['font'], row['size'], row['prefix'], row['tail'])
        grouped.setdefault(key, []).append(row['proposalWidth'])
        text = 'a' * row['prefix'] + ' b ' + 'c' * row['tail']
        assert ''.join(line['text'] for line in row['none']) == ''.join(line['text'] for line in row['push']) == text
        assert row['changed'] == ([line['text'] for line in row['none']] != [line['text'] for line in row['push']])
    assert set(grouped) == set(itertools.product(['LibreFranklin-Regular', 'EncodeSans-Md'], [10, 12, 13], range(1, 21), range(1, 16)))
    for widths in grouped.values():
        values = sorted(widths)
        assert len(values) == 3 and values == [values[0], values[0] + .5, values[0] + 1]

    actions = read('actions/proposals.json')
    assert actions['reference'] == REFERENCE and len(actions['rows']) == report['publicActionProfiles'] == 16
    assert {(r['dpr'], r['textScale'], r['proposalWidth']) for r in actions['rows']} == set(itertools.product([1, 2], [1, 1.5], [0, 180, 240, 400]))
    for row in actions['rows']:
        prefix = f"width-{float(row['proposalWidth'])}-scale-{float(row['textScale'])}-dpr-{float(row['dpr'])}"
        bare, probed = [directory / 'actions' / f'{prefix}-wrapped-{flag}.png' for flag in ['false', 'true']]
        assert row['identical'] is True and bare.read_bytes() == probed.read_bytes()
        assert struct.unpack('>II', bare.read_bytes()[16:24]) == (720 * row['dpr'], 800 * row['dpr'])
        assert {entry['key'] for entry in row['queries']} == {'review', 'archive'}
        if row['proposalWidth'] == 400:
            anchor = ROOT / 'evidence/reference-investigations/activity-item-20261016/captures' / f"actions-multi-light-text{float(row['textScale'])}-hosted-dpr{float(row['dpr'])}.png"
            assert bare.read_bytes() == anchor.read_bytes(), 'Original public action anchor changed'
    narrow = next(row for row in actions['rows'] if row['dpr'] == 1 and row['textScale'] == 1.5 and row['proposalWidth'] == 240)
    review = [r for r in narrow['queries'] if r['key'] == 'review']
    archive = [r for r in narrow['queries'] if r['key'] == 'archive']
    assert [(r['width'], r['fittedWidth'], r['fittedHeight']) for r in review] == [('infinity', 95, 36), (0, 28, 150), (148 / 3, 46, 125)]
    assert [(r['width'], r['fittedWidth'], r['fittedHeight']) for r in archive] == [('infinity', 97, 36), (0, 28, 175), (51, 50, 100)]

    buckets = read('buckets/buckets.json')
    assert buckets['reference'] == REFERENCE and len(buckets['traces']) == report['textHistoryTraces'] == 48
    assert sum(len(t['events']) for t in buckets['traces']) == report['textHistorySnapshots'] == 120
    lookup = {(t['key'], t['dpr'], t['sequence']): t for t in buckets['traces']}
    assert set(lookup) == set(itertools.product(['review', 'archive', 'title12', 'title26'], [1, 2], range(6)))
    for (key, dpr, sequence), trace in lookup.items():
        target = {'review': 10, 'archive': 11, 'title12': 12, 'title26': 26}[key]
        sequences = [[target], [target - .5, target], [target, target - .5, target], [target, target + 1, target],
                     [target - .49, target - .1, target], [target - .5, target, target + .01]]
        assert [e['proposalWidth'] for e in trace['events']] == sequences[sequence]
        for event in trace['events']:
            data = (directory / 'buckets' / event['path']).read_bytes()
            assert struct.unpack('>II', data[16:24]) == (720 * dpr, 1000 * dpr)
    fresh = lookup['review', 1, 0]['events'][0]
    growing = lookup['review', 1, 1]['events']
    revisited = lookup['review', 1, 2]['events']
    assert fresh['rect'] == {'width': 10, 'height': 80}
    assert [e['rect']['height'] for e in growing] == [96, 96]
    assert (directory / 'buckets' / growing[0]['path']).read_bytes() == (directory / 'buckets' / growing[1]['path']).read_bytes()
    assert [e['rect']['height'] for e in revisited] == [80, 96, 80]
    assert (directory / 'buckets' / fresh['path']).read_bytes() == (directory / 'buckets' / revisited[-1]['path']).read_bytes()
    assert [e['rect']['height'] for e in lookup['review', 2, 1]['events']] == [96, 80]
    assert [e['rect']['height'] for e in lookup['review', 2, 4]['events']] == [96, 96, 96]
    return dict(publicTextQueries=3374, paragraphProxyQueries=5400, publicActionProfiles=16,
                identicalActionPngPairs=16, originalActionAnchors=4, historyTraces=48, historySnapshots=120,
                cleanReplayIdenticalFiles=156)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
