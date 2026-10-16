#!/usr/bin/env python3
"""Audit hosted native Stepper evidence without accepting Linux parity."""
import hashlib
import itertools
import json
from pathlib import Path, PurePosixPath
import struct

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/stepper-20261016'
LOCALES = {'en_US', 'de_DE', 'es_CL', 'fr_FR', 'ja_JP', 'ar_EG', 'hi_IN'}
FIXTURES = {
    'above-range', 'below-range', 'beyond-js-safe', 'button-anchor', 'disabled',
    'empty', 'environment-de', 'equal-above', 'equal-below', 'equal-range',
    'integer-max', 'integer-min', 'intrinsic', 'js-safe', 'labeled-initializer',
    'long', 'lower', 'multiline', 'negative-offset', 'normal', 'observe-only',
    'offset', 'offset-min', 'parent-font20', 'parent-font30', 'rtl', 'space',
    'state-active', 'state-inactive', 'state-key', 'step-four', 'step-negative',
    'step-zero', 'unicode', 'upper', 'value-1234', 'width-100', 'width-12',
    'width-120', 'width-160', 'width-240', 'width-60', 'width-80',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    assert name and str(path) == name and not path.is_absolute() and '..' not in path.parts, 'Unsafe evidence path'
    return path


def integer(value):
    assert isinstance(value, str) and str(int(value)) == value and -(2 ** 63) <= int(value) < 2 ** 63, 'Lossless Int64 string required'
    return int(value)


def png_size(path):
    data = path.read_bytes()
    assert data[:16] == b'\x89PNG\r\n\x1a\n\0\0\0\rIHDR', 'Invalid PNG header'
    return struct.unpack('>II', data[16:24])


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    reference = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['referenceRevision'] == reference['revision'] and report['referenceTree'] == reference['tree']
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False, 'Source investigation cannot approve parity'
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual == set(report['files']) | {'investigation.json'}, 'Missing or extra Stepper evidence'
    for name, expected in report['files'].items():
        relative(name)
        assert digest(directory / name) == expected, name

    provenance = read('tooling-provenance.json')
    inputs = read('inputs.json')
    build = read('source-build-result.json')
    source = json.loads((ROOT / provenance['sourceIdentity']).read_text())
    assert inputs['reference'] == build['reference'] == provenance['referenceRevision'] == reference['revision']
    assert inputs['tree'] == provenance['referenceTree'] == reference['tree']
    assert inputs['compiledInputs'] == build['compiledInputs'] == provenance['compiledInputs'] == [], 'Compiled inputs cannot prove fresh source replay'
    assert provenance['target'] == 'arm64-apple-macosx26.0' and provenance['buildTarget'] == 'Sabella' and provenance['automaticResolution'] is False
    assert build['sourceFilesUnchanged'] == len(source['files']) == 89
    assert build['sourceArchiveSha256'] == inputs['files']['reference-source.tar'] == source['fullArchiveSha256']
    expected_inputs = {'reference-source.tar', 'replay.py', 'tool/main.swift', 'tool/behavior.swift', 'tool/states.swift', 'tool/run-traps.py', 'tool/image-renderer-discovery.swift'}
    assert set(inputs['files']) == expected_inputs and provenance['toolArtifact']['files'] == {**inputs['files'], 'inputs.json': digest(directory / 'inputs.json')}

    data = read('captures/captures.json')
    rows = data['captures']
    assert data['reference'] == reference['revision'] and data['processLocale'] == 'en_US'
    assert data['fixtures'] == report['fixtures'] == len(FIXTURES) == 43
    keys = {(r['fixture'], r['appearance'], r['textScale'], r['dpr']) for r in rows}
    assert len(rows) == report['hostedCaptures'] == 344 and keys == set(itertools.product(FIXTURES, ['light', 'dark'], [1, 1.5], [1, 2])), 'Hosted capture coverage changed'
    assert len(keys) == len(rows), 'Duplicate hosted capture'
    bykey = {(r['fixture'], r['appearance'], r['textScale'], r['dpr']): r for r in rows}
    paths = set()
    for row in rows:
        assert row['source'] == reference['revision'] and row['processLocale'] == 'en_US'
        assert row['captureMethod'] == 'NSHostingView.cacheDisplay in isolated NSWindow; explicit bitmap dimensions, no image resizing', 'Capture method changed'
        assert row['environmentDisplayScale'] == row['dpr']
        assert row['nativeWindowState'] == {'applicationActive': False, 'backingDpr': 2, 'key': False, 'main': False, 'origin': [-10000, -10000]}, 'Physical/focus state cannot be inferred from requested bitmap scale'
        for key in ['value', 'lowerBound', 'upperBound', 'step', 'displayOffset']:
            integer(row[key])
        assert integer(row['lowerBound']) <= integer(row['upperBound'])
        expected = row['path']
        assert expected not in paths
        paths.add(expected)
        for key in ['path', 'instrumentedPath', 'layoutWitnessPath']:
            relative(row[key])
            assert png_size(directory / 'captures' / row[key]) == (row['width'] * row['dpr'], row['height'] * row['dpr'])
            assert digest(directory / 'captures' / row[key]) == digest(directory / 'captures' / expected), 'Native instrumentation changed artwork'
        assert row['instrumentedPngByteIdentical'] is True and row['layoutWitnessPngByteIdentical'] is True
        if row['api'] == 'BleeckerButton':
            assert row['fixture'] == 'button-anchor'
            continue
        assert row['api'] == 'BleeckerStepper' and row['componentRect']['height'] == 36
        assert row['decrementEnabled'] == (not row['disabled'] and integer(row['value']) > integer(row['lowerBound']))
        assert row['incrementEnabled'] == (not row['disabled'] and integer(row['value']) < integer(row['upperBound']))
        fonts = row['layoutWitnessFonts']
        assert fonts['label']['pointSize'] == 13 and fonts['label']['postScriptName'] == 'EncodeSans-Regular', 'Fixed label font changed'
        assert fonts['value']['pointSize'] == 12 and fonts['value']['postScriptName'] == '.AppleSystemUIFontMonospaced-Bold', 'Fixed value font changed'
        for part in ['minus', 'plus']:
            assert fonts[part]['pointSize'] == (row['parentFont'] or 13)
        rects = row['layoutWitnessRects']
        assert rects['divider']['height'] == 24 and rects['divider']['width'] == 1
        assert rects['value']['width'] >= 34
        assert rects['label']['width'] == rects['label-text']['width'] + 20
    assert report['stepperCaptures'] == sum(r['api'] == 'BleeckerStepper' for r in rows) == 336
    assert report['buttonAnchors'] == 8
    for appearance, scale, dpr in itertools.product(['light', 'dark'], [1, 1.5], [1, 2]):
        def row(fixture):
            return bykey[(fixture, appearance, scale, dpr)]
        for left, right in [('normal', 'labeled-initializer'), ('normal', 'observe-only'), ('value-1234', 'environment-de')]:
            assert digest(directory / 'captures' / row(left)['path']) == digest(directory / 'captures' / row(right)['path']), 'Initializer, binding or environment locale changed initial artwork'
        assert row('environment-de')['environmentLocale'] == 'de_DE' and row('environment-de')['formattedValue'] == '1,234'
    normal = bykey[('normal', 'light', 1, 2)]
    assert normal['componentRect']['width'] == 132.5
    assert normal['layoutWitnessRects']['minus-button']['height'] == 3.5, 'Native minus hit geometry changed'
    assert normal['layoutWitnessRects']['plus-button']['height'] == 12.5
    assert bykey[('width-12', 'light', 1, 2)]['componentRect']['width'] == 82, 'Native narrow overflow changed'

    behavior = read('behavior/behavior.json')
    traces = behavior['traces']
    assert behavior['reference'] == reference['revision'] and len(traces) == report['nativeBehaviorTraces'] == 25
    assert len({t['fixture'] for t in traces}) == 25
    for trace in traces:
        value, lower, upper, step = (integer(trace[k]) for k in ['initialValue', 'lowerBound', 'upperBound', 'step'])
        requests, writes = [], []
        for action in trace['actions']:
            assert integer(action['before']) == value
            kind = action['action']
            enabled = not trace['disabled'] and ((kind == 'decrement' and value > lower) or (kind == 'increment' and value < upper))
            expected = max(lower, value - step) if kind == 'decrement' else min(upper, value + step)
            requested = [str(expected)] if enabled else []
            assert action['requests'] == requested, 'Native request arithmetic or one-sided clamp changed'
            assert action['modelWrites'] == ([] if trace['observeOnly'] else requested), 'Binding ownership changed'
            requests += requested
            writes += action['modelWrites']
            if action['modelWrites']:
                value = expected
            assert integer(action['after']) == value
        assert trace['requests'] == requests and trace['modelWrites'] == writes
        update = trace['externalUpdate']
        assert update['requestCountBefore'] == update['requestCountAfter'] == len(requests), 'External update emitted a request'
        assert update['value'] == '6' and update['formattedValue'] == '106'
        value = 6
        for action in trace['afterExternalActions']:
            assert integer(action['before']) == value
            expected = min(7, value + 2) if action['action'] == 'increment' else max(5, value - 2)
            assert action['requests'] == [str(expected)]
            assert action['modelWrites'] == ([] if trace['observeOnly'] else [str(expected)])
            if not trace['observeOnly']:
                value = expected
            assert integer(action['after']) == value
        assert integer(trace['finalValue']) == value and trace['finalFormattedValue'] == str(value + 100)
    grids = behavior['hitGrid']
    assert {(g['button'], g['axis']) for g in grids} == set(itertools.product(['minus-button', 'plus-button'], ['horizontal', 'vertical']))
    counts = {('minus-button', 'horizontal'): (36, 27), ('minus-button', 'vertical'): (77, 7), ('plus-button', 'horizontal'): (36, 25), ('plus-button', 'vertical'): (77, 25)}
    for grid in grids:
        points = grid['points']
        assert (len(points), sum(bool(p['requests']) for p in points)) == counts[(grid['button'], grid['axis'])], 'Finite native hit grid changed'

    phases = read('states/states.json')['phases']
    assert len(phases) == report['pointerPhaseTraces'] == 10
    assert {(p['fixture'], p['action']) for p in phases} == set(itertools.product(['normal', 'lower', 'upper', 'disabled', 'step-zero'], ['decrement', 'increment']))
    for phase in phases:
        assert phase['afterDown'] == {'modelWrites': [], 'requests': [], 'value': phase['initial']}, 'Pointer-down/hold emitted a native request'
        assert len(phase['afterUp']['requests']) <= 1 and phase['afterUp']['modelWrites'] == phase['afterUp']['requests']
        for suffix in ['before', 'down', 'up']:
            assert png_size(directory / 'states' / (phase['pathStem'] + '-' + suffix + '.png')) == (1440, 360)
    assert next(p for p in phases if p['fixture'] == 'normal' and p['action'] == 'increment')['holdSeconds'] == 1.2

    values = {str(v) for v in [-(2 ** 63), -(2 ** 63) + 1, -9007199254740993, -1234567, -1000, -999, -1, 0, 1, 999, 1000, 1234, 1234567, 9007199254740991, 9007199254740992, 9007199254740993, 2 ** 63 - 2, 2 ** 63 - 1]}
    for locale in LOCALES:
        formatting = read('locale-' + locale + '/formatting.json')
        assert formatting['processLocale'] == locale and len(formatting['formatting']) == 18
        assert {r['value'] for r in formatting['formatting']} == values, 'Integer formatter coverage changed'
        assert all(isinstance(r['text'], str) for r in formatting['formatting'])
    assert report['integerFormatterWitnesses'] == 126

    traps = read('traps/traps.json')['cases']
    names = {'display-overflow', 'display-underflow', 'decrement-overflow', 'increment-overflow', 'negative-step-decrement-overflow', 'negative-step-increment-underflow', 'display-after-increment', 'display-after-decrement', 'invalid-range'}
    assert len(traps) == report['nativeTrapCases'] == 9 and {r['case'] for r in traps} == names
    for trap in traps:
        name = trap['case']
        assert trap['returnCode'] == -5 and trap['trapped'] is True, 'Native overflow/range failure was hidden'
        phases = ['setup:' + name]
        if name not in {'display-overflow', 'display-underflow', 'invalid-range'}:
            phases.append('constructed:' + name)
        if name in {'display-after-increment', 'display-after-decrement'}:
            value = str(2 ** 63 - 1 if name.endswith('increment') else -(2 ** 63))
            phases += ['binding-request:' + value, 'binding-write:' + value]
        assert trap['phases'] == phases, 'Native arithmetic-before-clamp or display failure phase changed'
        assert (directory / 'traps' / (name + '.stdout')).read_text().splitlines() == phases
        for stream in ['stdout', 'stderr']:
            assert digest(directory / 'traps' / (name + '.' + stream)) == trap[stream + 'Sha256']

    diagnostic = read('image-renderer-diagnostic/captures.json')['captures']
    assert len(diagnostic) == report['unsupportedImageRendererCaptures'] == 24
    anchors = read('cross-method-anchors.json')['results']
    assert len(anchors) == 8 and {a['path'] for a in anchors} == {r['path'] for r in rows if r['api'] == 'BleeckerButton'}
    for anchor in anchors:
        assert anchor['geometryIdentical'] is True and anchor['oldRect'] == anchor['newRect'] and anchor['alphaIdentical'] is True
        old = ROOT / 'evidence/reference-investigations/data-metrics-20261015' / relative(anchor['oldPath'])
        with Image.open(old) as image:
            a = image.convert('RGBA')
        with Image.open(directory / 'captures' / relative(anchor['path'])) as image:
            b = image.convert('RGBA')
        difference = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
        assert ImageChops.difference(a.getchannel('A'), b.getchannel('A')).getbbox() is None
        assert list(difference.getbbox()) == anchor['rgbDifferenceBounds'] and max(v[1] for v in difference.getextrema()) == anchor['rgbMaximum']
        assert sum(v != (0, 0, 0) for v in difference.get_flattened_data()) == anchor['rgbChangedPixels'] > 0, 'Cross-method RGB mismatch cannot be waived'

    replay = read('clean-replay.json')
    expected_outputs = {name for name in report['files'] if name.split('/')[0] in {'captures', 'behavior', 'states', 'image-renderer-diagnostic', 'traps'} or name.startswith('locale-')}
    assert replay['compiledInputs'] == [] and replay['inputFiles'] == 7 and replay['sourceFilesUnchanged'] == 89
    assert replay['filesCompared'] == replay['byteIdenticalFiles'] == report['cleanReplayFiles'] == len(replay['results']) == 1168
    assert len({r['path'] for r in replay['results']}) == len(replay['results']) and {r['path'] for r in replay['results']} == expected_outputs, 'Replay output coverage changed'
    assert replay['differentFiles'] == []
    for row in replay['results']:
        assert row['byteIdentical'] is True and row['sha256'] == row['replaySha256'] == digest(directory / relative(row['path'])), 'Replayed output differs from preserved source evidence'
    catalog = read('catalog-investigation.json')
    assert catalog['reference'] == reference['revision'] and catalog['buildTarget'] == 'SabellaCatalog'
    assert catalog['buildExitCode'] == 0 and catalog['pinnedSourceFilesUnchanged'] == 89 and catalog['accepted'] is False
    return {'hostedCaptures': 344, 'stepperCaptures': 336, 'sourceReplayIdenticalFiles': 1168,
            'behaviorTraces': 25, 'pointerPhaseTraces': 10, 'integerFormatterWitnesses': 126,
            'nativeTrapCases': 9, 'accepted': False}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
