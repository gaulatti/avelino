#!/usr/bin/env python3
"""Audit public text alignment measurements and preserve the failed Qt diagnostic."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/activity-text-alignment-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
SOURCE_SHA256 = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
ARCHIVE_SHA256 = 'fd17c1569ba4dce5dbf29a49bca0f4de8e887511f4dd73a37808498755ee15a4'
QT_COMMIT = 'bf30fa143d49bc9debab55b149d162a7fbebb0c3'
PROFILES = {('primary14', 'Edition updated'), ('secondary12', 'Ready for review'),
            ('secondary10', '2 min ago'), ('primary13', 'Review'), ('primary13', 'Archive'),
            ('primary20', 'Review'), ('primary20', 'Archive')}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(row):
    return row['style'], row['text'], row['dpr'], row['rtl'], row['proposalWidth']


def size(row):
    return {key: row[key] for key in ['width', 'height']}


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['referenceRevision'] == REFERENCE and report['accepted'] is False
    assert report['approvedExceptions'] == [] and report['expectedImagesChanged'] is False
    files = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert files == set(report['files']) | {'investigation.json'}
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name

    inputs, tooling, build = (read(name) for name in ['inputs.json', 'tooling-provenance.json', 'source-build-result.json'])
    assert inputs['reference'] == tooling['reference'] == build['reference'] == REFERENCE
    assert set(inputs['files']) == {'reference-source.tar', 'replay.py', 'tool/Common.swift', 'tool/RtlTextMain.swift', 'tool/LineMain.swift'}
    assert inputs['files']['reference-source.tar'] == tooling['sourceArchiveSha256'] == build['sourceArchiveSha256'] == SOURCE_SHA256
    assert tooling['sourceTree'] == 'db61113381a51fc3c7b3d12786609cd9e76627c8'
    assert tooling['sourceFiles'] == build['sourceFilesUnchanged'] == 89
    assert build['libraryBuiltFromSources'] is True and build['prebuiltLibraryInputs'] is False
    assert tooling['compiledInputs'] == [] and tooling['independentMachineAvailability'] == 'pending'
    assert tooling['sourceOnlyReplayMembers'] == sorted([*inputs['files'], 'inputs.json'])
    assert tooling['sourceOnlyReplayArchiveSha256'] == ARCHIVE_SHA256
    common = json.loads((ROOT / 'evidence/reference-investigations/activity-item-20261016/replay-inputs.json').read_text())
    assert inputs['files']['tool/Common.swift'] == tooling['sharedCaptureHelperSha256'] == common['files']['tool/Common.swift']
    archive = Path(tooling['sourceOnlyReplayArchive'])
    if archive.exists():
        assert digest(archive) == ARCHIVE_SHA256
        with tarfile.open(archive) as source:
            assert sorted(m.name for m in source.getmembers()) == tooling['sourceOnlyReplayMembers']
            for name, expected in inputs['files'].items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected, name

    replay = read('clean-replay.json')
    outputs = {name for name in files if name.startswith(('directions/', 'lines/'))}
    assert replay['files'] == replay['byteIdenticalFiles'] == report['sourceReplayIdenticalFiles'] == 1599
    assert replay['mismatches'] == [] and len(replay['outputs']) == 1599
    assert {row['file'] for row in replay['outputs']} == outputs
    for row in replay['outputs']:
        assert row['originalSha256'] == row['replaySha256'] == digest(directory / row['file'])

    directions = read('directions/text-directions.json')
    assert directions['reference'] == REFERENCE
    queries, fresh = directions['queries'], directions['fresh']
    assert len(queries) == report['publicDirectionQueries'] == 6748
    assert len(fresh) == report['freshDirectionQueries'] == 252
    expected = {(style, text, dpr, rtl, width / 2) for (style, text), dpr, rtl, width
                in itertools.product(PROFILES, [1, 2], [False, True], range(241))}
    assert len({identity(row) for row in queries}) == len(queries) and {identity(row) for row in queries} == expected
    assert {identity(row) for row in fresh} == {(style, text, dpr, rtl, width) for (style, text), dpr, rtl, width
        in itertools.product(PROFILES, [1, 2], [False, True], [12, 26, 38, 39, 39.5, 40, 40.5, 54, 160])}
    lookup = {identity(row): row for row in queries}
    original = json.loads((ROOT / 'evidence/reference-investigations/activity-layout-mechanics-20261016/text/fixed-queries.json').read_text())
    assert len(original['rows']) == report['originalLTRQueriesReproduced'] == 3374
    for row in original['rows']:
        assert size(lookup[(row['style'], row['text'], row['dpr'], False, row['proposalWidth'])]['rect']) == row['native']
    changes = [(lookup[(row['style'], row['text'], row['dpr'], False, row['proposalWidth'])], row)
               for row in queries if row['rtl']]
    assert sum(size(a['rect']) != size(b['rect']) for a, b in changes) == report['nativeDirectionDifferences'] == 593
    assert sum(a['rect']['height'] != b['rect']['height'] for a, b in changes) == report['nativeDirectionHeightDifferences'] == 5

    def png(name, dpr, height):
        data = (directory / name).read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II', data[16:24]) == (720 * dpr, height * dpr), name
        return data

    source = ROOT / 'evidence/reference-investigations/activity-item-20261016/captures'
    captures = json.loads((source / 'captures.json').read_text())['captures']
    rows = read('directions/row-directions.json')
    assert rows['reference'] == REFERENCE and len(rows['fixtures']) == report['publicActivityPairs'] == report['originalActivityPNGsReproduced'] == 16
    assert {(r['width'], r['rtl'], r['dpr'], r['textScale']) for r in rows['fixtures']} == set(itertools.product([160, 400], [False, True], [1, 2], [1, 1.5]))
    for row in rows['fixtures']:
        assert row['publicWitnessIdentical'] is True and len(row['paths']) == 2
        a, b = [png('directions/rows/' + name, row['dpr'], 800) for name in row['paths']]
        old = next(r for r in captures if r['fixture'] == row['fixture'] and r['appearance'] == 'light' and r['dpr'] == row['dpr'] and r['textScale'] == row['textScale'])
        assert a == b == (source / old['path']).read_bytes()
        assert row['witness']['parts'] == old['witness']['parts']

    alignments = read('lines/lines.json')
    assert alignments['reference'] == REFERENCE
    samples = alignments['rows']
    texts = {'title': 'Edition updated', 'detail': 'Ready for review', 'timestamp': '2 min ago',
             'single-word': 'Review', 'one-space': 'abc def', 'double-space': 'abc  def',
             'trailing-space': 'abc def ', 'explicit-line': 'abc\ndef'}
    assert len(samples) == report['publicAlignmentSamples'] == 768
    assert {(r['key'], r['dpr'], r['rtl'], r['alignment'], r['proposalWidth']) for r in samples} == set(itertools.product(texts, [1, 2], [False, True], ['leading', 'center', 'trailing'], [14, 16, 17, 22, 29, 40, 60, 80]))
    frame_matches = 0
    for row in samples:
        assert row['text'] == texts[row['key']]
        a, b = [png('lines/' + name, row['dpr'], 1000) for name in row['paths']]
        assert row['imagesIdentical'] is False and a != b, 'Custom renderer is not a transparent observation'
        frame_matches += row['bareRect'] == row['probedRect']
        for frame in [row['bareRect'], row['probedRect']]:
            assert set(frame) == {'x', 'y', 'width', 'height'} and all(math.isfinite(v) for v in frame.values())
        for line in row['lines']:
            for run in line['runs']:
                assert all(0 <= i < len(row['text']) for i in run['indices'])
                assert run['characters'] == ''.join(row['text'][i] for i in run['indices'])
    assert report['publicAlignmentRendererPNGIdentities'] == 0
    assert frame_matches == report['publicAlignmentRendererFrameMatches'] == 626
    assert len(samples) - frame_matches == report['publicAlignmentRendererFrameDifferences'] == 142
    bykey = {(r['key'], r['dpr'], r['proposalWidth'], r['rtl'], r['alignment']): r for r in samples}
    identities = 0
    for row in samples:
        if not row['rtl']:
            other = bykey[(row['key'], row['dpr'], row['proposalWidth'], True, {'leading': 'trailing', 'center': 'center', 'trailing': 'leading'}[row['alignment']])]
            assert row['bareRect'] == other['bareRect']
            assert (directory / 'lines' / row['paths'][0]).read_bytes() == (directory / 'lines' / other['paths'][0]).read_bytes()
            identities += 1
    assert identities == report['bareAlignmentDirectionPNGIdentities'] == 384
    overlaps = {'title': ('primary14', 'Edition updated'), 'detail': ('secondary12', 'Ready for review'),
                'timestamp': ('secondary10', '2 min ago'), 'single-word': ('primary13', 'Review')}
    identities = 0
    for row in samples:
        if row['key'] in overlaps and row['alignment'] == 'leading' and row['proposalWidth'] == 40:
            style, text = overlaps[row['key']]
            old = next(r for r in fresh if r['style'] == style and r['text'] == text and r['dpr'] == row['dpr'] and r['rtl'] == row['rtl'] and r['proposalWidth'] == 40)
            assert row['bareRect'] == old['rect']
            assert (directory / 'lines' / row['paths'][0]).read_bytes() == png('directions/text/' + old['path'], row['dpr'], 1000)
            identities += 1
    assert identities == report['bareAlignmentToDirectionPNGIdentities'] == 16

    qt, provenance = read('qt/comparison.json'), read('qt/provenance.json')
    assert qt['accepted'] is False and qt['candidate'] == provenance['candidateCommit'] == QT_COMMIT
    assert provenance['qt'] == '6.8.3' and provenance['architecture'] == 'arm64'
    assert provenance['sourceBuildTreesAbsent'] is True and provenance['network'] == 'none'
    assert provenance['inputQmlSha256'] == digest(directory / 'qt/tst_directions.qml')
    candidate = json.loads((ROOT / 'evidence/development/activity/candidate.json').read_text())
    assert provenance['installedLibrarySha256'] == candidate['installedFiles']['lib/qml/Avelino/libAvelino.so']
    assert provenance['packageImage'] == candidate['toolchainImages']['packageNoICUHeaders']
    for name, expected in provenance['sourceFileHashes'].items():
        assert hashlib.sha256(subprocess.check_output(['git', 'show', QT_COMMIT + ':' + name], cwd=ROOT)).hexdigest() == expected, name
    expected = {('ascending', *identity(r)): r for r in queries} | {('fresh', *identity(r)): r for r in fresh}
    seen, mismatches = set(), {'ascending': 0, 'fresh': 0}
    for row in qt['results']:
        actual = row['input']; key = (actual['kind'], *identity(actual)); assert key not in seen; seen.add(key)
        native = expected[key]['rect']; assert row['native'] == native
        difference = {k: {'native': native[k], 'qt': actual[k]} for k in ['width', 'height'] if native[k] != actual[k]}
        assert row['differences'] == difference
        if difference:
            assert actual['rtl'] is True
            mismatches[actual['kind']] += 1
    assert seen == set(expected) and len(seen) == qt['queries'] == report['historicalQtQueries'] == 7000
    assert mismatches == {'ascending': 593, 'fresh': 21}
    assert qt['mismatches'] == report['historicalQtMismatches'] == 614
    assert qt['matches'] == report['historicalQtMatches'] == 6386
    assert report['historicalQtAscendingRTLMismatches'] == 593 and report['historicalQtFreshRTLMismatches'] == 21
    captured = []
    for dpr in [1, 2]:
        capped = (directory / f'qt/activity-rtl-qt-dpr{dpr}-v1.log').read_text()
        complete = (directory / f'qt/activity-rtl-qt-dpr{dpr}-v2.log').read_text()
        assert capped.count('RTL_MEASUREMENT ') == 2001 and 'Maximum amount of warnings exceeded' in capped
        assert complete.count('RTL_MEASUREMENT ') == 3500 and 'Totals: 30 passed, 0 failed' in complete
        captured.extend(json.loads(line.split('RTL_MEASUREMENT ', 1)[1]) for line in complete.splitlines() if 'RTL_MEASUREMENT ' in line)
    assert captured == [row['input'] for row in qt['results']], 'Historical Qt outcomes must retain the actual captured records'
    return report


if __name__ == '__main__':
    verify()
    print('Text alignment source: 7000 direction/fresh measurements, 768 bare samples, 1599 identical replay outputs; historical Qt614 failures and renderer proxy limits preserved')
