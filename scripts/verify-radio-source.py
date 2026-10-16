#!/usr/bin/env python3
"""Audit preserved native RadioGroup evidence; never approve Linux parity."""
import hashlib
import itertools
import json
import math
from pathlib import Path, PurePosixPath
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/radio-20261016'
FIXTURES = {
    'button-anchor', 'vertical', 'horizontal', 'intrinsic-vertical', 'intrinsic-horizontal',
    'empty-vertical', 'empty-horizontal', 'single', 'outside', 'selected-weekly',
    'selected-monthly', 'observe-only', 'disabled', 'one-disabled', 'selected-disabled',
    'all-disabled', 'rtl-vertical', 'rtl-horizontal', 'empty-title', 'all-empty-titles',
    'space-title', 'empty-value', 'multiline', 'unicode', 'canonical-value',
    'long-vertical', 'long-horizontal', 'system-font20', 'secondary-font20',
    'mono-font20', 'primary-bold20', 'system-bold20', 'red-foreground', 'environment-de',
} | {f'{orientation}-width-{width}' for orientation in ['vertical', 'horizontal']
     for width in [600, 240, 160, 120, 100, 80, 60, 12]} | {
    f'primary-font-{size}' for size in ['0.3', '13.0', '13.5', '20.0', '30.0']}
TRACES = {
    'vertical', 'horizontal', 'outside', 'observe-only', 'disabled', 'one-disabled',
    'selected-disabled', 'all-disabled', 'empty-value', 'empty-title', 'all-empty-titles',
    'space-title', 'canonical-value', 'unicode', 'multiline', 'vertical-width-12',
    'horizontal-width-12', 'primary-font-0.3', 'primary-font-13.5', 'primary-font-20.0',
    'primary-bold20', 'rtl-horizontal', 'empty-vertical', 'single',
}
WINDOW = {'applicationActive': False, 'backingDpr': 2, 'key': False, 'main': False,
          'origin': [-10000, -10000]}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    assert name and str(path) == name and not path.is_absolute() and '..' not in path.parts, 'Unsafe evidence path'
    return path


def png_size(path):
    data = path.read_bytes()
    assert data[:16] == b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR', 'Invalid PNG header'
    return struct.unpack('>II', data[16:24])


def normalizer(profile):
    """Independent recursive NFD and stable canonical ordering over measured facts."""
    mappings = {int(k, 16): v for k, v in profile['decompositions'].items()}
    classes = {int(k, 16): v for k, v in profile['combiningClasses'].items()}
    def expand(scalar, active=frozenset()):
        assert scalar not in active, 'Cyclic canonical decomposition'
        return [v for child in mappings[scalar] for v in expand(child, active | {scalar})] if scalar in mappings else [scalar]
    def normalize(scalars):
        result = []
        for scalar in scalars:
            for value in expand(scalar):
                result.append(value)
                index, rank = len(result) - 1, classes.get(value, 0)
                while index and rank and classes.get(result[index - 1], 0) > rank:
                    result[index], result[index - 1] = result[index - 1], result[index]
                    index -= 1
        return result
    return normalize


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    reference = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['referenceRevision'] == reference['revision'] and report['referenceTree'] == reference['tree']
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False, 'Source investigation cannot approve parity'
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual == set(report['files']) | {'investigation.json'}, 'Missing or extra RadioGroup evidence'
    for name, expected in report['files'].items():
        relative(name)
        assert digest(directory / name) == expected, name
    provenance, inputs, build = (read(name) for name in ['tooling-provenance.json', 'inputs.json', 'source-build-result.json'])
    source = json.loads((ROOT / provenance['sourceIdentity']).read_text())
    assert inputs['reference'] == build['reference'] == provenance['referenceRevision'] == reference['revision']
    assert inputs['tree'] == provenance['referenceTree'] == reference['tree']
    assert inputs['compiledInputs'] == build['compiledInputs'] == provenance['compiledInputs'] == [], 'Compiled inputs cannot prove fresh source replay'
    assert provenance['target'] == 'arm64-apple-macosx26.0' and provenance['buildTarget'] == 'Sabella' and provenance['automaticResolution'] is False
    assert build['sourceFilesUnchanged'] == len(source['files']) == 89
    assert build['sourceArchiveSha256'] == inputs['files']['reference-source.tar'] == source['fullArchiveSha256']
    expected_inputs = {'reference-source.tar', 'replay.py', 'tool/main.swift', 'tool/behavior.swift', 'tool/accessibility.swift', 'tool/read-normalization.py', 'tool/string-identity.swift'}
    assert set(inputs['files']) == expected_inputs
    assert provenance['toolArtifact']['files'] == {**inputs['files'], 'inputs.json': digest(directory / 'inputs.json')}

    profile, native, qt = (read(name) for name in ['native-normalization-data.json', 'native-string-identity.json', 'qt-string-identity.json'])
    assert profile['reference'] == native['reference'] == reference['revision']
    assert profile['icuVersion'] == [78, 1, 0, 0] and profile['unicodeVersion'] == [17, 0, 0, 0]
    assert len(profile['decompositions']) == 13253 and len(profile['combiningClasses']) == 968
    for key, values in profile['decompositions'].items():
        assert f'{int(key, 16):06x}' == key and values
        assert all(isinstance(v, int) and 0 <= v <= 0x10ffff and not 0xd800 <= v <= 0xdfff for v in [int(key, 16), *values])
    assert all(isinstance(v, int) and 1 <= v <= 255 for v in profile['combiningClasses'].values())
    normalize = normalizer(profile)
    rows = native['results']
    assert native['inputIcuVersion'] == profile['icuVersion'] and native['inputUnicodeVersion'] == profile['unicodeVersion']
    assert native['cases'] == len(rows) == report['nativeStringPairs'] == 13762, 'Native String pair coverage changed'
    assert native['randomSeed'] == '510e527fade682d1' and native['randomMarkPairs'] == 500
    mapping_pairs = [r for r in rows if r['kind'] == 'canonical-mapping']
    assert len(mapping_pairs) == 13253 and {r['left'][0]: r['right'] for r in mapping_pairs} == {int(k, 16): v for k, v in profile['decompositions'].items()}, 'Canonical mapping coverage changed'
    for row in rows:
        assert row['equal'] == (normalize(row['left']) == normalize(row['right'])), 'Native canonical identity changed'
        assert not row['equal'] or row['hashEqual'] is True, 'Equal native String hashes differ'
    assert len([r for r in rows if r['kind'] == 'mark-order']) == 500
    assert len([r for r in rows if r['kind'] == 'explicit-string']) == 9
    expected_types = {'int-double-one': True, 'bool-int-one': False, 'bool-string': False, 'int-string': False, 'signed-zero': True, 'nan': False, 'positive-infinity': True, 'opposite-infinity': False, 'unsafe-integer-rounded-double': False, 'maximum-integer-rounded-double': False, 'float-double-fraction': False, 'optional-nil-different-types': False, 'optional-some-versus-bare': False, 'canonical-string': True}
    assert len(native['anyHashable']) == len(expected_types) and {r['case']: r['equal'] for r in native['anyHashable']} == expected_types, 'Native AnyHashable type identity changed'
    assert qt['qtVersion'] == '6.8.3' and qt['qcharUnicodeVersion'] == 27
    assert len(qt['results']) == len(rows)
    for a, b in zip(rows, qt['results']):
        assert {k: v for k, v in b.items() if k != 'qtCanonicalEqual'} == a, 'Qt/native identity pair alignment changed'
    mismatches = [r for r in qt['results'] if r['qtCanonicalEqual'] != r['equal']]
    assert qt['mismatches'] == report['qtNormalizationMismatches'] == len(mismatches) == 17, 'Qt normalization mismatch must remain explicit'
    assert all(r['kind'] == 'mark-order' and r['equal'] is True for r in mismatches)
    eq = lambda a, b: normalize(list(map(ord, a))) == normalize(list(map(ord, b)))

    captures = read('captures/captures.json')
    rows = captures['captures']
    assert captures['reference'] == reference['revision']
    assert captures['fixtures'] == report['fixtures'] == len(FIXTURES) == 55
    keys = {(r['fixture'], r['appearance'], r['textScale'], r['dpr']) for r in rows}
    assert len(rows) == report['hostedCaptures'] == 440 and keys == set(itertools.product(FIXTURES, ['light', 'dark'], [1, 1.5], [1, 2])), 'Hosted capture coverage changed'
    assert len(keys) == len(rows), 'Duplicate hosted capture'
    bykey = {(r['fixture'], r['appearance'], r['textScale'], r['dpr']): r for r in rows}
    paths = set()
    for row in rows:
        assert row['source'] == reference['revision'] and row['accepted'] is False
        assert row['processLocale'] == 'en_US' and row['environmentDisplayScale'] == row['dpr']
        assert row['nativeWindowState'] == WINDOW, 'Physical/focus state cannot be inferred from requested bitmap scale'
        assert row['captureMethod'] == 'NSHostingView.cacheDisplay in isolated NSWindow; explicit bitmap dimensions, no image resizing'
        assert row['componentMeasured'] is True and row['componentRect'] is not None
        assert row['selectionScalars'] == list(map(ord, row['selection'])), 'Original scalar payload changed'
        assert row['path'] not in paths
        paths.add(row['path'])
        for key in ['path', 'witnessPath', 'detailPath']:
            relative(row[key])
            assert png_size(directory / 'captures' / row[key]) == (row['width'] * row['dpr'], row['height'] * row['dpr'])
            assert digest(directory / 'captures' / row[key]) == digest(directory / 'captures' / row['path']), 'Native instrumentation changed artwork'
        assert row['witnessIdentity'] is True and row['detailIdentity'] is True
        assert all(math.isfinite(v) for r in [row['componentRect'], *row['detailRects'].values()] for v in r.values())
        assert all(r['width'] >= 0 and r['height'] >= 0 for r in [row['componentRect'], *row['detailRects'].values()])
        if row['api'] == 'BleeckerButton':
            assert row['fixture'] == 'button-anchor'
            continue
        assert row['api'] == 'BleeckerRadioGroup'
        assert len(row['detailRects']) == len(row['options']) * 4 and len(row['detailFonts']) == len(row['options']) * 2
        for i, option in enumerate(row['options']):
            assert option['selected'] == eq(option['value'], row['selection']), 'Selection must use canonical String identity'
            for part in ['title', 'icon']:
                font = row['detailFonts'][f'option-{i}-{part}']
                assert font['enabled'] == (not row['disabled'] and not option['disabled'])
    assert report['radioCaptures'] == sum(r['api'] == 'BleeckerRadioGroup' for r in rows) == 432 and report['buttonAnchors'] == 8
    for fixture, appearance, dpr in itertools.product(FIXTURES - {'button-anchor'}, ['light', 'dark'], [1, 2]):
        a, b = (bykey[(fixture, appearance, scale, dpr)] for scale in [1, 1.5])
        assert digest(directory / 'captures' / a['path']) == digest(directory / 'captures' / b['path']), 'Custom text scale changed plain native Label'
    row = lambda fixture: bykey[(fixture, 'light', 1, 2)]
    for fixture, width, height in [('vertical', 72, 68), ('horizontal', 224, 16), ('horizontal-width-100', 101, 112), ('empty-vertical', 0, 0), ('empty-horizontal', 0, 0)]:
        assert (row(fixture)['componentRect']['width'], row(fixture)['componentRect']['height']) == (width, height), 'Native layout boundary changed'
    assert row('primary-font-0.3')['detailRects']['option-0-icon']['width'] == 0
    assert row('primary-font-0.3')['detailFonts']['option-0-title']['pointSize'] == 12
    assert row('primary-bold20')['detailRects']['option-0-icon']['width'] == 24
    assert row('primary-font-20.0')['detailRects']['option-0-icon']['width'] == 23
    assert row('horizontal-width-100')['detailRects']['option-0-title']['width'] == 0
    assert row('horizontal-width-100')['detailRects']['option-0-title']['height'] == 80

    behavior = read('behavior/behavior.json')
    assert behavior['reference'] == reference['revision'] and behavior['nativeWindowState'] == WINDOW
    assert behavior['accepted'] is False and behavior['screenReaderVerified'] is False and behavior['physicalPointerVerified'] is False
    traces = behavior['traces']
    assert len(traces) == report['nativeBehaviorTraces'] == len(TRACES) == 24 and {t['fixture'] for t in traces} == TRACES
    for trace in traces:
        f = trace['configuration'];value = trace['initialValue']
        assert value == f['selection'] and len(trace['actions']) == 6
        for action in trace['actions']:
            assert action['before'] == value
            index = action['index']
            valid = index < len(f['options']) and not action.get('skipped')
            enabled = valid and not f['disabled'] and not f['options'][index]['disabled']
            expected = [f['options'][index]['value']] if enabled and action['target'] != 'gap' and not action['cancel'] else []
            assert action['requests'] == expected, 'Native release/target/disabled request changed'
            assert action['modelWrites'] == ([] if f['observeOnly'] else expected), 'Binding ownership changed'
            if action['modelWrites']:
                value = action['modelWrites'][-1]
            assert action['after'] == value
        update = trace['externalUpdate']
        assert update['requests'] == update['modelWrites'] == [] and update['allWrites'] == ['external-missing'], 'External producer update emitted a request'
        assert update['value'] == 'external-missing'
        value = update['value'];parent = trace['externalConfiguration']
        assert len(trace['afterExternalActions']) == 4 and [a['index'] for a in trace['afterExternalActions']] == [0, 1, 2, 2]
        for action in trace['afterExternalActions']:
            assert action['before'] == value
            option = parent['options'][action['index']]
            expected = [] if option['disabled'] else [option['value']]
            assert action['requests'] == expected, 'Updated option identity changed'
            assert action['modelWrites'] == ([] if f['observeOnly'] else expected), 'Binding ownership changed'
            if action['modelWrites']:
                value = action['modelWrites'][-1]
            assert action['after'] == value
        assert trace['finalValue'] == value
    canonical = next(t for t in traces if t['fixture'] == 'canonical-value')
    assert list(map(ord, canonical['initialValue'])) == [101, 769] and list(map(ord, canonical['actions'][0]['requests'][0])) == [233], 'Original requested scalar spelling must be preserved'

    grids = behavior['hitGrids']
    counts = {
        'vertical': [(115, 86), (41, 32), (39, 26)],
        'primary-font-20.0': [(160, 129), (59, 49), (55, 40)],
        'primary-bold20': [(171, 140), (59, 50), (57, 42)],
        'rtl-horizontal': [(115, 86), (41, 32), (39, 26)],
        'empty-title': [(55, 26), (0, 0), (39, 26)],
        'space-title': [(63, 34), (41, 32), (39, 26)],
        'primary-font-0.3': [(78, 53), (39, 30), (0, 0)],
        'horizontal-width-100': [(55, 0), (0, 0), (39, 26)],
    }
    assert len(grids) == report['finiteHitGrids'] == len(counts) == 8 and {g['fixture'] for g in grids} == set(counts)
    for grid in grids:
        assert [a['axis'] for a in grid['axes']] == ['button-horizontal', 'title-vertical', 'icon-vertical']
        observed = [(len(a['points']), sum(bool(p['requests']) for p in a['points'])) for a in grid['axes']]
        assert observed == counts[grid['fixture']], 'Finite native hit grid changed'
        assert all(p['requests'] in [[], ['daily']] for a in grid['axes'] for p in a['points'])
    phases = behavior['pointerPhases']
    names = {'selected', 'unselected', 'disabled', 'cancel', 'hold', 'selection-during-down', 'disable-during-down', 'option-disable-during-down', 'remove-during-down', 'reorder-during-down', 'orientation-during-down'}
    assert len(phases) == report['pointerPhaseTraces'] == len(names) == 11 and {p['fixture'] for p in phases} == names
    for phase in phases:
        name = phase['fixture']
        for key in ['afterDown', 'afterHold']:
            assert phase[key]['requests'] == phase[key]['modelWrites'] == [], 'Pointer-down/hold emitted a native request'
        expected = ['daily'] if name in {'selected', 'unselected', 'hold', 'selection-during-down'} else []
        assert phase['afterUp']['requests'] == phase['afterUp']['modelWrites'] == expected, 'Native release cancellation changed'
        for suffix in ['before', 'down', 'up']:
            assert png_size(directory / 'behavior/states' / (phase['pathStem'] + '-' + suffix + '.png')) == (1440, 1040)
    assert next(p for p in phases if p['fixture'] == 'hold')['holdSeconds'] == 1.2
    accessibility = read('native-accessibility.json')
    assert accessibility['accepted'] is False and accessibility['screenReaderVerified'] is False
    assert len(accessibility['results']) == 6
    for context in accessibility['results']:
        assert context['host']['role'] == 'AXGroup' and context['host']['childCount'] == 0, 'Hosting-only AX diagnostic cannot establish control semantics'

    anchors = read('cross-method-anchors.json')['results']
    assert len(anchors) == 8 and {a['path'] for a in anchors} == {r['path'] for r in rows if r['api'] == 'BleeckerButton'}
    for anchor in anchors:
        old = ROOT / relative(anchor['previousPath'])
        assert anchor['pngByteIdentical'] is True and anchor['geometryIdentical'] is True
        assert digest(old) == anchor['previousSha256'] == anchor['currentSha256'] == digest(directory / 'captures' / relative(anchor['path'])), 'Hosted button anchor changed'
        assert anchor['currentRect'] == anchor['previousRect']
    replay = read('clean-replay.json')
    expected_outputs = {name for name in report['files'] if name.startswith(('captures/', 'behavior/')) or name in {'native-accessibility.json', 'native-normalization-data.json', 'native-string-identity.json'}}
    assert replay['compiledInputs'] == [] and replay['sourceFilesUnchanged'] == 89
    assert replay['filesCompared'] == replay['byteIdenticalFiles'] == report['sourceReplayIdenticalFiles'] == len(expected_outputs) == 1358
    assert replay['differentFiles'] == []
    assert len(replay['results']) == len(expected_outputs) and {r['path'] for r in replay['results']} == expected_outputs, 'Replay output coverage changed'
    for result in replay['results']:
        assert result['identical'] is True and result['originalSha256'] == result['replayedSha256'] == digest(directory / relative(result['path']))
    return {k: report[k] for k in ['hostedCaptures', 'radioCaptures', 'nativeBehaviorTraces', 'finiteHitGrids', 'pointerPhaseTraces', 'nativeStringPairs', 'qtNormalizationMismatches', 'sourceReplayIdenticalFiles']}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
