#!/usr/bin/env python3
"""Audit formatted-text reflow and all preserved native differences."""
import hashlib
import importlib.util
import json
import io
from pathlib import Path
import tarfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/media-library-caption-20261017'
PREVIOUS = ROOT / 'evidence/development/media-library-reflow-20261017'
spec = importlib.util.spec_from_file_location('media_evidence', ROOT / 'scripts/verify-media-library-candidate.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)

def validate_report(report):
    assert report['reference'] == evidence.inputs.REFERENCE and report['accepted'] is False
    assert report['baseRevision'] == '1691bbff68b2cd6ac063f09f23aeb5afc0635b4d'
    assert report['previousCandidateSha256'] == evidence.digest(PREVIOUS / 'candidate.json')
    assert report['status'] == 'verification-pending' and report['remainingAcceptance'] == evidence.GATES
    assert report['tolerance'] == 'none' and report['approvedExceptions'] == [] and report['expectedImagesChanged'] is False
    assert report['strictComparisonStatus'] == 'failed'
    summary = report['strictComparison']
    expected = dict(cases=1608, exactMatches=1008, pixelMatches=1168, nativeFrameMatches=1288,
        nativeLifecycleMatches=1608, stateMatches=1608, sizingObservations=0,
        nativeSizingContexts=496, nativeSizingQueries=7440, retainedRestoreObservations=48, retainedRestorePixelMatches=48)
    assert all(summary[k] == value for k, value in expected.items())
    assert summary['byKind'] == dict(closed=dict(cases=496, exactMatches=344),
        edge=dict(cases=104, exactMatches=80), history=dict(cases=1008, exactMatches=584))
    validation = report['validation']
    for key, value in dict(componentChecksDpr1=15, componentChecksDpr2=15, formattedTextChecksDpr1=16, formattedTextChecksDpr2=16, fullQtTargets=33,
            malformedConfigurations=13, isolatedCatalogInputs=76, independentModes=34, catalogCaptures=139,
            installedFiles=134, virtualProfiles=8, formattedVirtualProfiles=16, formattedFontCases=1656, formattedPillCases=2112,
            operatorControls=14, operatorClicks=23, operatorStates=24,
            operatorExactStates=24, strictDefaultExitCode=1, strictImageExitCode=1, fatalProcesses=8,
            virtualRestoreObservations=48, virtualRestorePixelMatches=48, legacyPngs=139, legacyMetadata=139).items():
        assert validation[key] == value, key
    assert validation['operatorStatus'] == 'passed'
    assert validation['physicalDisplay'] is False and validation['hardwareAcceleration'] is False

def verify_formatted_corpora(directory, report):
    archived = {}
    for key, record in report['archives'].items():
        if key.startswith('formatted-observations-'):
            with tarfile.open(directory / record['archive']) as stream:
                for member in stream.getmembers():
                    if member.name.startswith(('font-captures/', 'pill-captures/')):
                        archived[member.name] = stream.extractfile(member).read()
    def module(name, filename):
        spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
        value = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(value)
        return value
    font_inputs = module('caption_font_inputs', 'capture-font-modifier-cases.py')
    font_observations = module('caption_font_observations', 'font-modifier-observations.py').observations
    pill_inputs = module('caption_pill_inputs', 'capture-pill-modifier-cases.py')
    for kind, inputs, observations, previous_path, count in [
            ('font', font_inputs, font_observations, ROOT / 'evidence/development/font-modifier/comparison/comparison.json', 1656),
            ('pill', pill_inputs, pill_inputs.observations, ROOT / 'evidence/development/pill-modifier-20261017/comparison/comparison.json', 2112)]:
        current = json.loads((directory / 'formatted' / (kind + '-comparison.json')).read_text())
        previous = json.loads(previous_path.read_text())
        assert report['formattedPreviousSha256'][kind] == evidence.digest(previous_path)
        assert current['accepted'] is False and len(current['results']) == count
        corpus = inputs.rows()
        expected = {row['path']: row for row in corpus}
        results = {row['fixture']: row for row in current['results']}
        before = {row['fixture']: row for row in previous['results']}
        assert expected.keys() == results.keys() == before.keys() and len(expected) == count
        totals = dict(exactMatches=0, pixelMatches=0, partFrameMatches=0, baselineMatches=0, stateMatches=0)
        for name, row in expected.items():
            value = archived[kind + '-captures/' + name]
            assert hashlib.sha256(value).hexdigest() == evidence.digest(previous_path.parent.parent / 'captures' / name)
            metadata = json.loads(archived[kind + '-captures/' + name + '.json'])
            result = results[name]
            assert result['referenceRevision'] == evidence.inputs.REFERENCE
            assert result['tolerance'] == 'none; glyph-edge policy has not been calibrated or approved'
            reference = row['directory'] / 'captures' / row['source']['paths'][0] if kind == 'font' else ROOT / row['reference']
            assert result['candidateSHA256'] == hashlib.sha256(value).hexdigest()
            assert result['referenceSHA256'] == evidence.digest(reference)
            dpr = row['source']['dpr'] if kind == 'font' else row['dpr']
            with Image.open(reference) as native, Image.open(io.BytesIO(value)) as candidate:
                assert native.size == candidate.size == (640 * dpr, 400 * dpr)
                pixels_equal = native.convert('RGBA').tobytes() == candidate.convert('RGBA').tobytes()
            observed = observations(row, metadata)
            assert all(result[key] == value for key, value in observed.items()), name
            exact = pixels_equal and all(observed[key] == 'passed' for key in ['partFramesStatus', 'baselineStatus', 'stateStatus'])
            assert result['status'] == ('passed' if exact else 'failed')
            if kind == 'pill':
                assert result['pixelStatus'] == ('passed' if pixels_equal else 'failed')
                old_pixel_pass = before[name]['pixelStatus'] == 'passed'
            else:
                assert (result['changedPixels'] == 0 and result['maximumChannelError'] == 0) is pixels_equal
                old_pixel_pass = before[name]['changedPixels'] == 0 and before[name]['maximumChannelError'] == 0
            assert not old_pixel_pass or pixels_equal, (kind, name, 'previous pixel match')
            for key in ['partFramesStatus', 'baselineStatus', 'stateStatus']:
                if before[name][key] == 'passed':
                    assert observed[key] == 'passed', (kind, name, key)
            totals['exactMatches'] += exact
            totals['pixelMatches'] += pixels_equal
            for total, key in [('partFrameMatches', 'partFramesStatus'), ('baselineMatches', 'baselineStatus'), ('stateMatches', 'stateStatus')]:
                totals[total] += observed[key] == 'passed'
        summary = current['summary']
        assert current['status'] == ('passed' if totals['exactMatches'] == count else 'failed')
        assert summary['cases'] == totals['stateMatches'] == count
        assert summary['partFrameMatches'] == totals['partFrameMatches'] and summary['baselineMatches'] == totals['baselineMatches']
        assert summary['exactPixelAndGeometryMatches' if kind == 'font' else 'exactMatches'] == totals['exactMatches']
        if kind == 'pill':
            assert summary['pixelMatches'] == totals['pixelMatches']
        assert report['formattedComparisons'][kind] == summary
        print(kind + ': all ' + str(count) + ' native comparisons recomputed; no previous passing observation regressed')
    assert json.loads((directory / 'formatted-runtime-proof/result.json').read_text())['exitCode'] == 0
    for kind in ['font-modifier', 'pill-modifier']:
        profiles = sorted((directory / 'formatted-runtime').glob(kind + '-*.json'))
        assert len(profiles) == 8
        seen = set()
        for path in profiles:
            value = json.loads(path.read_text())
            protocol, backend, configuration = path.stem.removeprefix(kind + '-').split('-')
            seen.add((protocol, backend, configuration))
            assert value['accepted'] is False and value['physicalDisplay'] is False and value['hardwareAcceleration'] is False
            assert value['qt'] == '6.8.3'
            assert value['platform'] == protocol and value['graphicsApi'] == (1 if backend == 'software' else 3)
            assert value['dpr'] == (1 if configuration == 'standard' else 2)
            assert value['textScale'] == (1 if configuration == 'standard' else 1.5)
            assert value['appearance'] == ('light' if configuration == 'standard' else 'dark')
            if kind == 'font-modifier':
                assert all(value[key] == 'passed' for key in ['fontModifierChecks', 'callerStateChecks', 'liveFontPaintChecks', 'focusChecks', 'qtAccessibilityChecks'])
                assert value['closedContextCount'] == len(value['closedContexts']) == 207 and len(value['retainedUpdates']) == 3
            else:
                assert value['structuralChecks'] == 'passed'
                assert len(value['rows']) == 111 and len(value['histories']) == 7
        assert seen == {(p, b, c) for p in ['xcb', 'wayland'] for b in ['software', 'opengl'] for c in ['standard', 'scaled']}

def verify_diagnostics(directory, report):
    archived = {}
    for key, record in report['archives'].items():
        if key.startswith(('diagnostic-outputs-', 'diagnostic-binaries-')):
            with tarfile.open(directory / record['archive']) as stream:
                for member in stream.getmembers():
                    archived[member.name] = stream.extractfile(member).read()
    read = lambda path: json.loads(path.read_text())
    current = read(directory / 'package/artifact-binding.json')['installedFiles']
    previous = read(PREVIOUS / 'package/artifact-binding.json')['installedFiles']
    bindings = read(directory / 'regression/diagnostic-install-bindings.json')
    producers = {
        'media-library-caption-trace-operator-v1': 'media-library-caption-trace-build-v1',
        'media-library-caption-glyph-trace-operator-v1': 'media-library-caption-glyph-trace-build-v2',
        'media-library-caption-session-v1': 'published-reflow',
        'media-library-caption-offset-session-v1': 'media-library-caption-offset-build-v1'}
    assert bindings.keys() == producers.keys()
    for run, binding in bindings.items():
        producer = producers[run]
        assert binding['producer'] == producer and binding['installedFiles'].keys() == current.keys()
        manifest = directory / 'attempts' / producer / 'inputs.json' if producer != 'published-reflow' else PREVIOUS / 'qt/inputs.json'
        assert binding['producerSourceManifestSha256'] == evidence.digest(manifest)
        for name, value in binding['installedFiles'].items():
            location = value['location']
            if location.startswith('current:'):
                assert location == 'current:install/' + name and value['sha256'] == current[name]
            elif location.startswith('previous:'):
                assert location == 'previous:install/' + name and value['sha256'] == previous[name]
            else:
                assert location == 'diagnostic-binaries/' + value['sha256']
                assert hashlib.sha256(archived[location]).hexdigest() == value['sha256']
    outputs = read(directory / 'replay/diagnostic-outputs.json')
    def output(name):
        location = outputs[name]['location']
        return (directory / location.removeprefix('candidate/')).read_bytes() if location.startswith('candidate/') else archived[location]
    def rgba(data):
        with Image.open(io.BytesIO(data)) as bitmap:
            return bitmap.size, bitmap.convert('RGBA').tobytes()
    old_operator = read(PREVIOUS / 'operator/result.json')
    assert len(old_operator['records']) == 24 and sum(row['passed'] for row in old_operator['records']) == 20
    for row in old_operator['records']:
        expected = rgba((PREVIOUS / 'operator' / row['reference']).read_bytes())
        for platform in ['xcb', 'offscreen']:
            assert rgba(output('media-library-caption-session-v1/' + platform + '-' + row['phase'] + '.png')) == expected
            with Image.open(io.BytesIO(output('media-library-caption-offset-session-v1/' + platform + '-' + row['phase'] + '.png'))) as bitmap:
                assert bitmap.size == (1120, 820)
                crop = bitmap.convert('RGBA').crop((24, 200, 664, 600))
                assert (crop.size, crop.tobytes()) == expected
    def traces(data):
        return [json.loads(line.split('MEDIA_CAPTION_TRACE ', 1)[1]) for line in data.decode().splitlines() if 'MEDIA_CAPTION_TRACE ' in line]
    stem = 'media-library-caption-glyph-trace-operator-v1/'
    actual = traces(output(stem + 'client.log'))
    observations = 0
    for phase in ['width460', 'minimum160', 'light', 'scale-restored']:
        fresh = {row['id']: row for row in traces(output(stem + 'references/' + phase + '.log'))}
        assert len(fresh) == 7
        for expected in fresh.values():
            matching = [row for row in actual if all(row[key] == expected[key] for key in ['id', 'title', 'offered', 'minimum', 'rtl', 'dark', 'textScale', 'disabled', 'scroll'])]
            retained = matching[-1]
            assert retained['renderer']['width'] == expected['renderer']['width']
            assert expected['layout']['lineWidth'] == expected['renderer']['width']
            assert retained['layout']['lineWidth'] == 101 + 1 / 3
            assert retained['layout']['sourceFont'] == expected['layout']['sourceFont']
            observations += 1
    assert observations == 28

def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = evidence.verify(directory, report_validator=validate_report)
    old = json.loads((PREVIOUS / 'comparison/comparison.json').read_text())
    new = json.loads((directory / 'comparison/comparison.json').read_text())
    previous = {r['fixture']: r for r in old['results']}
    current = {r['fixture']: r for r in new['results']}
    assert previous.keys() == current.keys() and len(current) == 1608
    for name, before in previous.items():
        after = current[name]
        for key in ['pixelStatus', 'nativeFrameStatus', 'nativeLifecycleStatus', 'stateStatus', 'retainedRasterStatus']:
            if before[key] == 'passed':
                assert after[key] == 'passed', (name, key)
    regression = json.loads((directory / 'regression/native-pairs.json').read_text())
    assert regression['comparedPairs'] == 1608 and regression['regressions'] == []
    assert regression['previousComparisonSha256'] == evidence.digest(PREVIOUS / 'comparison/comparison.json')
    assert regression['currentComparisonSha256'] == evidence.digest(directory / 'comparison/comparison.json')
    catalogs = json.loads((directory / 'regression/catalogs.json').read_text())
    assert catalogs['status'] == 'passed' and catalogs['accepted'] is False and len(catalogs['records']) == 139
    for row in catalogs['records']:
        for suffix, before_key, after_key in [('', 'previousSha256', 'currentSha256'),
                ('.json', 'previousMetadataSha256', 'currentMetadataSha256')]:
            before = evidence.digest(PREVIOUS / 'catalogs' / (row['path'] + suffix))
            after = evidence.digest(directory / 'catalogs' / (row['path'] + suffix))
            assert row[before_key] == before == after == row[after_key]
        assert row['pixelsIdentical'] is True and row['metadataIdentical'] is True
    strict = json.loads((directory / 'package/strict-images.json').read_text())
    assert len(strict) == 201
    for row in strict.values():
        assert row['identical'] is True
        assert row['sha256'] == evidence.digest(directory / 'captures' / row['identicalCapture'])
    producer = json.loads((directory / 'qt/inputs.json').read_text())['sourceFiles']
    assert not any('__pycache__' in Path(name).parts or name.endswith('.pyc') for name in producer)
    for path in (directory / 'captures').glob('*.log'):
        assert 'QPainter::begin:' not in path.read_text(), path.name
    profiles = sorted((directory / 'runtime').glob('media-library-*.json'))
    assert len(profiles) == 8
    restored_pairs = []
    for path in profiles:
        value = json.loads(path.read_text())
        assert value['structuralChecks'] == 'passed' and value['retainedRestoreRasterStatus'] == 'passed'
        assert value['retainedRestorePixelMatches'] == 6 and value['physicalDisplay'] is False and value['hardwareAcceleration'] is False
        assert len(value['histories']) == 6
        for history in value['histories']:
            assert history['steps'][13]['step'] == 'restore' and history['steps'][13]['matchesInitialPixels'] is True
            stem = 'runtime/' + path.stem + '-' + history['configuration']['id'] + '-history-step'
            restored_pairs.append((stem + '0.png', stem + '13.png'))
    required = {name for pair in restored_pairs for name in pair}
    restored_images = {}
    for key, record in report['archives'].items():
        if not key.startswith('runtime-images-'):
            continue
        with tarfile.open(directory / record['archive']) as stream:
            for member in stream.getmembers():
                if member.name in required:
                    with Image.open(io.BytesIO(stream.extractfile(member).read())) as bitmap:
                        restored_images[member.name] = (bitmap.size, bitmap.convert('RGBA').tobytes())
    assert set(restored_images) == required and len(restored_pairs) == 48
    assert all(restored_images[first] == restored_images[last] for first, last in restored_pairs)
    before = (directory / 'attempts/media-library-caption-regression-v2/run.log').read_text()
    assert '14 passed, 2 failed' in before and before.count('FAIL!') == 2
    for name in ['qt/run.log', 'qt/full/run.log']:
        assert '15 passed, 0 failed' in (directory / name).read_text()
    assert (directory / 'qt/full/run.log').read_text().count('16 passed, 0 failed') >= 2
    verify_formatted_corpora(directory, report)
    verify_diagnostics(directory, report)
    if 'hostCommands' in report['validation']:
        host = json.loads((directory / 'host/result.json').read_text())
        commands = json.loads((directory / 'host/results.json').read_text())
        assert host['exitCode'] == 0 and host['commands'] == len(commands) == report['validation']['hostCommands']
        assert host['contractTests'] == report['validation']['hostContractTests']
        assert all(row['exitCode'] == 0 for row in commands)
        initial = directory / report['validation']['hostCandidateInput']
        frozen_inputs = json.loads((directory / 'host/inputs.json').read_text())
        assert frozen_inputs[str(directory.relative_to(ROOT) / 'candidate.json')] == evidence.digest(initial)
        assert report['validation']['cleanLinuxEvidenceReplay'] is True
        assert json.loads((directory / 'host/clean-linux/result.json').read_text())['exitCode'] == 0
        assert 'Ran 69 tests' in (directory / 'host/clean-linux/run.log').read_text()
    print('Formatted media: all 24 gallery states match fresh callers, all 1608 native lifecycles retained; complete mirror acceptance pending')
    return report

if __name__ == '__main__':
    verify()
