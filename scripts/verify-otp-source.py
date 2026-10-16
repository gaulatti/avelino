#!/usr/bin/env python3
"""Audit the native OTP source investigation without approving Linux parity."""
import hashlib
import itertools
import json
from pathlib import Path, PurePosixPath
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/otp-20261016'
FIXTURES = {'button-anchor', 'field-anchor', 'default-length', 'partial', 'full', 'overlong', 'unfiltered-initial', 'arabic-indic', 'eastern-arabic-indic', 'fullwidth', 'devanagari', 'mathematical', 'roman', 'fractions', 'han', 'keycap', 'combining', 'prepend', 'mixed-direction', 'empty-length-zero', 'nonempty-length-zero', 'length-one', 'length-two', 'length-four', 'length-eight', 'length-twelve', 'disabled-empty', 'disabled-value', 'rtl-empty', 'rtl-value', 'parent-font32', 'parent-red', 'locale-de', 'locale-ar', 'intrinsic-empty', 'intrinsic-value'} | {f'width-{n}' for n in [0, 12, 24, 60, 100, 160, 400]}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(name):
    p = PurePosixPath(name)
    assert name and str(p) == name and not p.is_absolute() and '..' not in p.parts, 'Unsafe evidence path'
    return p


def scalar_text(values):
    assert all(type(cp) is int and 0 <= cp <= 0x10ffff and not 0xd800 <= cp <= 0xdfff for cp in values), 'Invalid Unicode scalar'
    return ''.join(map(chr, values))


def ranges(path, wanted=None):
    result = set()
    for line in path.read_text().splitlines():
        text = line.split('#', 1)[0].strip()
        if not text:
            continue
        parts = list(map(str.strip, text.split(';')))
        if wanted is not None and parts[-1] not in wanted:
            continue
        span = parts[0].split('..')
        result.update(range(int(span[0], 16), int(span[-1], 16) + 1))
    return result


def projection(values, numbers, joining, prepend, limit=None):
    """Group retained numeric starts and their attached scalars, then prefix."""
    scalar_text(values)
    groups, current, previous = [], None, None
    for cp in values:
        if cp in numbers and previous not in prepend:
            current = [cp]
            groups.append(current)
        elif cp in joining and current is not None:
            current.append(cp)
        else:
            current = None
        previous = cp
    return [cp for group in (groups if limit is None else groups[:limit]) for cp in group]


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    reference = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['referenceRevision'] == reference['revision'] and report['referenceTree'] == reference['tree']
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False and report['approvedExceptions'] == [], 'Source investigation cannot approve parity'
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual == set(report['files']) | {'investigation.json'}, 'Missing or extra OTP evidence'
    for name, sha in report['files'].items():
        relative(name)
        assert digest(directory / name) == sha, name
    provenance, inputs, build = (read(n) for n in ['tooling-provenance.json', 'inputs.json', 'source-build-result.json'])
    identity = json.loads((ROOT / provenance['sourceIdentity']).read_text())
    assert provenance['referenceRevision'] == inputs['reference'] == build['reference'] == reference['revision']
    assert provenance['referenceTree'] == reference['tree'] and provenance['compiledInputs'] == []
    assert provenance['target'] == 'arm64-apple-macosx26.0' and provenance['buildTarget'] == 'Sabella' and provenance['automaticResolution'] is False
    assert build['sourceFilesUnchanged'] == len(identity['files']) == 89 and build['preparedInputsRecomputed'] == 2
    assert build['sourceArchiveSha256'] == inputs['files']['reference-source.tar'] == identity['fullArchiveSha256']
    assert len(inputs['files']) == 18 and set(inputs['files']) == {
        'reference-source.tar', 'replay.py', 'grapheme-inputs.json', 'numeric-cluster-properties.json',
        *('tool/' + name for name in ['Common.swift', 'CaptureMain.swift', 'RenderedBehaviorMain.swift', 'StateBindingMain.swift', 'EdgeMain.swift', 'semantics.swift', 'graphemes.swift', 'cluster-proof.swift']),
        *('unicode17/' + name for name in ['DerivedNumericType.txt', 'GraphemeBreakProperty.txt', 'GraphemeBreakTest.txt', 'emoji-data.txt', 'DerivedCoreProperties.txt', 'inputs.json'])}
    assert provenance['toolArtifact']['files'] == {**inputs['files'], 'inputs.json': digest(directory / 'inputs.json')}
    for name, sha in inputs['files'].items():
        if (directory / name).is_file():
            assert digest(directory / name) == sha, 'Frozen replay input differs from preserved data'
    official_inputs = read('unicode17/inputs.json')
    assert set(official_inputs) == {'DerivedNumericType.txt', 'GraphemeBreakProperty.txt', 'GraphemeBreakTest.txt', 'emoji-data.txt', 'DerivedCoreProperties.txt'}
    for name, record in official_inputs.items():
        assert record['url'].startswith('https://www.unicode.org/Public/17.0.0/ucd/') and digest(directory / 'unicode17' / name) == record['sha256']
    assert digest(directory / 'unicode17/LICENSE.txt') == digest(ROOT / 'assets/unicode/LICENSE.txt')

    semantics, graphemes, props, proof = (read(n) for n in ['native-otp-semantics.json', 'native-otp-graphemes.json', 'numeric-cluster-properties.json', 'native-otp-cluster-proof.json'])
    assert semantics['reference'] == graphemes['reference'] == proof['reference'] == reference['revision']
    numbers = set(semantics['singleScalarNumbers'])
    assert semantics['scannedValidScalars'] == 1112064 and len(numbers) == len(semantics['singleScalarNumbers']) == 2023
    assert numbers == ranges(directory / 'unicode17/DerivedNumericType.txt'), 'Native numeric profile differs from official data'
    assert semantics['singleScalarNumbers'] == sorted(numbers)
    assert len(semantics['markScalars']) == len(set(semantics['markScalars'])) == 2543
    joining = ranges(directory / 'unicode17/GraphemeBreakProperty.txt', {'Extend', 'SpacingMark', 'ZWJ'})
    prepend = ranges(directory / 'unicode17/GraphemeBreakProperty.txt', {'Prepend'})
    assert props['joiningScalars'] == sorted(joining) and len(joining) == 2619 and props['prependScalars'] == sorted(prepend) and len(prepend) == 27
    assert props['numericScalars'] == 2023 and props['numericGCBClasses'] == {'Other': 2023}
    for line in (directory / 'unicode17/GraphemeBreakProperty.txt').read_text().splitlines():
        text = line.split('#', 1)[0].strip()
        if text:
            span, kind = map(str.strip, text.split(';'))
            ends = span.split('..')
            assert not numbers.intersection(range(int(ends[0], 16), int(ends[-1], 16) + 1)), 'Numeric start has a non-Other grapheme class'
    pictographic = ranges(directory / 'unicode17/emoji-data.txt', {'Extended_Pictographic'})
    consonants = ranges(directory / 'unicode17/DerivedCoreProperties.txt', {'Consonant'})
    for key, overlap in [('numericExtendedPictographicOverlap', numbers & pictographic), ('numericIndicConsonantOverlap', numbers & consonants), ('joiningExtendedPictographicOverlap', joining & pictographic), ('joiningIndicConsonantOverlap', joining & consonants)]:
        assert props[key] == sorted(overlap) == [], 'Numeric cluster independence invariant failed'
    examples = semantics['examples']
    assert len(examples) == 204 and {(r['case'], r['length']) for r in examples} == set(itertools.product(range(34), [0, 1, 2, 4, 6, 10]))
    for row in examples:
        assert projection(row['input']['scalars'], numbers, joining, prepend) == row['filtered']['scalars']
        assert projection(row['input']['scalars'], numbers, joining, prepend, row['length']) == row['result']['scalars'], 'Native scalar spelling or character prefix changed'
    tests = graphemes['officialTests']
    expected_tests = read('grapheme-inputs.json')['cases']
    assert len(tests) == len(expected_tests) == 766 and [r['index'] for r in tests] == list(range(766))
    assert graphemes['officialInputSha256'] == digest(directory / 'unicode17/GraphemeBreakTest.txt')
    assert [r['index'] for r in tests if not r['matchesOfficial']] == list(range(758, 766)), 'Measured native boundary differences must remain visible'
    for row, expected in zip(tests, expected_tests):
        assert row['scalars'] == expected['scalars'] and row['matchesOfficial'] == (row['boundaries'] == expected['boundaries'])
        assert row['boundaries'][0] == 0 and row['boundaries'][-1] == len(row['scalars']) and row['boundaries'] == sorted(set(row['boundaries']))
        assert projection(row['scalars'], numbers, joining, prepend) == row['filteredScalars']
    contexts = graphemes['markContexts']
    bases = {0x31, 0x661, 0x2163, 0x4e00, 0x1d7d9, 0x1f100, 0xf33}
    assert len(contexts) == 17801 and {(r['base'], r['mark']) for r in contexts} == set(itertools.product(bases, semantics['markScalars']))
    for row in contexts:
        values = [row['base'], row['mark'], 0x32]
        assert row['firstScalarRuleMatches'] is True
        assert projection(values, numbers, joining, prepend) == row['filteredScalars'], 'Native joining marks cannot be discarded'
        assert projection(values, numbers, joining, prepend, 1) == row['prefixOneScalars']
    assert proof['cases'] == 13137306 and proof['joiningCases'] == 2023 * 2619 and proof['prependCases'] == 2023 * 27 and proof['allScalarCases'] == 7 * 1112064
    assert proof['mismatches'] == 0 and proof['mismatchExamples'] == [] and proof['resultFNV1a64'] == '3d551fb50bf22f59'

    qt, candidate = read('qt-probe/qt-otp-semantics.json'), read('qt-rule-probe/qt-otp-filter.json')
    assert qt['qt'] == candidate['qt'] == '6.8.3' and qt['qcharUnicodeVersion'] == 27
    assert qt['summary'] == {'boundaryVectors': 766, 'examples': 204, 'markContexts': 17801, 'nativeBoundaryVectorMatches': 636, 'nativeExampleMatches': 204, 'nativeMarkBoundaryMatches': 13780, 'nativeMarkFilterMatches': 13782, 'nativeNumbers': 2023, 'numericScalarDifferences': 112, 'plainQtExampleMatches': 194}, 'Original Qt diagnostic must not be replaced with passing adapter output'
    assert len(qt['singleScalarNumericDifferences']) == 112 and all(r['native'] is True and r['qt'] is False and r['scalar'] in numbers for r in qt['singleScalarNumericDifferences'])
    assert len({r['scalar'] for r in qt['singleScalarNumericDifferences']}) == 112
    assert len(qt['officialTests']) == 766 and len(qt['markContexts']) == 17801 and len(qt['examples']) == 204
    for expected, row in zip(tests, qt['officialTests']):
        assert row['index'] == expected['index'] and row['matchesNative'] == (row['boundaries'] == expected['boundaries'])
    assert sum(r['matchesNative'] for r in qt['officialTests']) == 636
    for expected, row in zip(contexts, qt['markContexts']):
        assert (row['base'], row['mark']) == (expected['base'], expected['mark'])
        assert row['matchesNative'] == (row['boundaries'] == expected['boundaries'])
        assert row['filterMatchesNative'] == (row['filteredScalars'] == expected['filteredScalars'] and row['prefixOneScalars'] == expected['prefixOneScalars'])
    assert sum(r['matchesNative'] for r in qt['markContexts']) == 13780 and sum(r['filterMatchesNative'] for r in qt['markContexts']) == 13782
    assert candidate['summary'] == {'examples': 204, 'graphemeVectors': 766, 'markContexts': 17801, 'matchingExamples': 204, 'matchingGraphemeVectorFilters': 766, 'matchingMarkContexts': 17801}
    for expected, row in zip(examples, candidate['examples']):
        assert row['matchesNative'] is True and row['scalars'] == expected['result']['scalars'] and (row['case'], row['length']) == (expected['case'], expected['length'])
    assert len(candidate['examples']) == 204 and len(candidate['markContexts']) == 17801 and len(candidate['graphemeVectorFilters']) == 766
    for expected, row in zip(contexts, candidate['markContexts']):
        assert row['matchesNative'] is True and row['scalars'] == expected['filteredScalars'] and row['prefixOneScalars'] == expected['prefixOneScalars']
    for expected, row in zip(tests, candidate['graphemeVectorFilters']):
        assert row['index'] == expected['index'] and row['matchesNative'] is True and row['scalars'] == expected['filteredScalars']

    captures = read('captures/captures.json')
    assert captures['reference'] == reference['revision'] and captures['fixtures'] == 43 and len(captures['captures']) == 344
    rows = captures['captures']
    assert {(r['fixture'], r['appearance'], r['textScale'], r['dpr']) for r in rows} == set(itertools.product(FIXTURES, ['light', 'dark'], [1, 1.5], [1, 2])), 'OTP fixture coverage changed'
    for row in rows:
        image = directory / 'captures' / relative(row['path'])
        witness = directory / 'captures' / relative(row['witnessPath'])
        assert row['source'] == reference['revision'] and row['accepted'] is False and row['witnessIdentity'] is True and image.read_bytes() == witness.read_bytes(), 'Public source/witness identity failed'
        assert image.read_bytes()[:16] == b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR' and struct.unpack('>II', image.read_bytes()[16:24]) == (row['width'] * row['dpr'], row['height'] * row['dpr'])
        n = row['native']
        assert n['backingDpr'] == 2 and not n['key'] and not n['main'] and not n['applicationActive'], 'Hosted window context changed'
        assert n['code'] == row['code'] and n['codeScalars'] == list(map(ord, row['code'])) and n['requests'] == [] and n['modelWrites'] == [], 'Initial getter must stay unfiltered'
        if row['api'] == 'BleeckerOTPInput':
            assert n['fieldFound'] and not n['editorFound'] and n['fontPointSize'] == 20 and n['centerAligned'] and n['enabled'] == (not row['disabled'])
            assert n['placeholder'] == '•' * row['length'] and n['componentRect']['width'] >= 28 and n['componentRect']['height'] == 40 * row['textScale']
            if row['fixture'].startswith('width-') and row['proposalWidth'] < 28:
                assert n['componentRect']['width'] == 28
            if row['intrinsic']:
                assert n['componentRect']['width'] == 600
        if row['fixture'] == 'button-anchor':
            assert image.read_bytes() == (ROOT / 'evidence/reference-investigations/radio-20261016/captures' / row['path']).read_bytes(), 'Hosted anchor context changed'

    behavior, bindings, edges = read('behavior-final/behavior.json'), read('state-bindings/state-bindings.json'), read('edges/edges.json')
    assert behavior['reference'] == bindings['reference'] == edges['reference'] == reference['revision']
    assert len(behavior['traces']) == 8 and len(bindings['traces']) == 9 and len(edges['traces']) == 2
    canonical = next(r for r in bindings['traces'] if r['bindingMode'] == 'projected-state' and r['fixture'] == 'empty')
    events = {r['action']: r['state'] for r in canonical['events']}
    assert events['insert-settled']['code'] == '1٢Ⅳ1\u03012' and events['insert-settled']['fieldValue'] == 'a1b٢Ⅳ1\u03012', 'Raw editing text and filtered model must remain distinct'
    assert events['return-command']['fieldValue'] == events['return-command']['code'] == '1️⃣٢'
    assert events['length-two']['code'] == 'X987654321', 'Length changes cannot truncate the getter'
    large = {r['action']: r['state'] for r in next(r for r in edges['traces'] if r['fixture'] == 'large-insert')['steps']}
    assert len(large['insert-40001']['fieldValue']) == 40001 and large['insert-40001']['fieldValue'] == 'a' * 40000 + '1' and large['insert-40001']['code'] == '1', 'Native insertion is not capped at Qt default length'
    marked = {r['action']: r['state'] for r in next(r for r in edges['traces'] if r['fixture'] == 'marked-text')['steps']}
    assert marked['mark-one']['hasMarkedText'] and marked['mark-two']['hasMarkedText'] and marked['mark-two']['code'] == '12'
    assert marked['unmark']['code'] == '一二' and marked['unmark']['hasMarkedText'] is False
    for folder, data, key in [('behavior-final', behavior, 'events'), ('state-bindings', bindings, 'events'), ('edges', edges, 'steps')]:
        for trace in data['traces']:
            for event in trace[key]:
                assert (directory / folder / relative(event['path'])).is_file()

    replay = read('clean-replay-comparison.json')
    assert replay['comparedFiles'] == replay['identicalFiles'] == 897 and replay['missingOriginal'] == replay['different'] == []
    assert len(replay['files']) == 897 and len({r['path'] for r in replay['files']}) == 897
    for row in replay['files']:
        relative(row['path'])
        assert row['identical'] is True and row['originalSha256'] == row['replaySha256'] == digest(directory / row['path']), 'Clean source replay drifted'
    expected_summary = {'publicCaptures': 344, 'otpCaptures': 328, 'anchorCaptures': 16, 'witnessByteIdentity': 344, 'crossComponentButtonAnchors': 8, 'bindingTraces': 8, 'stateBindingTraces': 9, 'edgeTraces': 2, 'nativeScalarCount': 1112064, 'nativeNumbers': 2023, 'officialGraphemeVectors': 766, 'nativeOfficialGraphemeMatches': 758, 'nativeMarkContexts': 17801, 'nativeClusterRuleCases': 13137306, 'nativeClusterRuleMismatches': 0, 'cleanReplayIdenticalFiles': 897}
    assert all(report[k] == v for k, v in expected_summary.items())
    return expected_summary


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
