#!/usr/bin/env python3
"""Recompute surface supplement evidence without granting mirror acceptance."""
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/surface-supplement-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
GATES = ['nativeCurvedStrokeInput', 'nativeRasterShadow', 'systemFontsAndButton',
         'nativeFirstBaseline', 'physicalDisplaysInput', 'readers']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_report(report):
    assert report['reference'] == REFERENCE
    assert report['accepted'] is False and report['status'] == 'verification-pending'
    assert report['expectedImagesChanged'] is False
    assert report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    assert report['remainingAcceptance'] == GATES
    summary = report['strictComparison']
    for key, value in dict(baselineContexts=440, inputProfiles=288, inputModes=576,
                           inputPoints=57792, images=1016).items():
        assert summary[key] == value, key
    validation = report['validation']
    for key, value in dict(fullQtTargets=27, componentChecksDpr1=5319,
                           componentChecksDpr2=5547, independentModes=31,
                           catalogCaptures=127, installedFiles=125, virtualProfiles=32,
                           strictBaselineExitCode=1, strictInputExitCode=1,
                           strictImageComparisonExitCode=1).items():
        assert validation[key] == value, key
    assert validation['physicalDisplay'] is False
    assert validation['hardwareAcceleration'] is False


def validate_profile(row, kind, projected):
    assert row['accepted'] is False and row['structuralChecks'] == 'passed'
    assert row['reference'] == REFERENCE and row['nativeComparisonStatus'] == 'failed'
    for gate in ['physicalInputAcceptance', 'rasterAcceptance', 'readerAcceptance']:
        assert row[gate] == 'pending'
    assert row['physicalDisplay'] is False and row['hardwareAcceleration'] is False
    assert row['fixture'] == 'surface-' + kind
    expected = {r['configuration']['fixture']: r for r in projected[
        'nativeBaselineContexts' if kind == 'baseline' else 'nativeInputProfiles']
        if (r['appearance'], r['textScale'], r['dpr']) ==
        (row['appearance'], row['textScale'], row['dpr'])}
    assert len(row['rows']) == len(expected) == (55 if kind == 'baseline' else 36)
    assert {r['configuration']['fixture'] for r in row['rows']} == set(expected)
    frames = guides = modes = points = activations = sequences = 0
    for actual in row['rows']:
        native = expected[actual['configuration']['fixture']]
        assert actual['configuration'] == native['configuration']
        if kind == 'baseline':
            frame_match = actual['parts'] == native['parts']
            guide_match = actual['guides'] == native['guides']
            assert actual['nativeFramesMatch'] is frame_match
            assert actual['nativeGuidesMatch'] is guide_match
            assert actual['state'] == native['state']
            frames += frame_match
            guides += guide_match
        else:
            assert [r['mode'] for r in actual['modes']] == [0, 3]
            for mode, source in zip(actual['modes'], native['modes']):
                assert mode['callerRetained'] is True
                assert len(mode['activations']) == len(mode['sequences']) == len(native['points'])
                different = [i for i, (a, b) in enumerate(zip(mode['activations'], source['activations'])) if a != b]
                sequence = [i for i, (a, b) in enumerate(zip(mode['sequences'], source['sequences'])) if a != b]
                assert mode['differentActivationPoints'] == different
                assert mode['differentSequencePoints'] == sequence
                frame_match = mode['parts'] == native['parts']
                match = frame_match and not different and not sequence
                assert mode['nativeInputMatch'] is bool(match)
                frames += frame_match
                modes += bool(match)
                points += len(native['points'])
                activations += len(different)
                sequences += len(sequence)
    assert (row['exactFrameSets'], row['exactGuideSets'], row['exactInputModes'],
            row['inputPoints'], row['activationMismatches'], row['sequenceMismatches']) == (
                frames, guides, modes, points, activations, sequences)


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('candidate.json')
    validate_report(report)
    assert set(report['files']) == {str(p.relative_to(directory)) for p in directory.rglob('*')
                                   if p.is_file() and p.name not in ['candidate.json', 'README.md']}
    for name, checksum in report['files'].items():
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts
        assert digest(directory / name) == checksum, name
    archive_data = {}
    for key, archive in report['archives'].items():
        manifest = read(archive['manifest'])
        with tarfile.open(directory / archive['archive']) as stream:
            members = stream.getmembers()
            assert len(members) == len(manifest) == archive['files']
            assert {m.name for m in members} == set(manifest)
            archive_data[key] = {}
            for member in members:
                assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
                data = stream.extractfile(member).read()
                assert len(data) == manifest[member.name]['bytes']
                assert hashlib.sha256(data).hexdigest() == manifest[member.name]['sha256']
                archive_data[key][member.name] = data
    attempt_parts = [data for key, data in archive_data.items() if key.startswith('attempts')]
    attempts = {name: data for part in attempt_parts for name, data in part.items()}
    assert len(attempts) == sum(len(part) for part in attempt_parts)
    expected_exits = {**{f'surface-supplement-build-v{i}': code for i, code in enumerate([125, 1, 0, 0, 0], 1)},
                      **{f'surface-supplement-package-v{i}': 1 for i in range(1, 5)},
                      'surface-supplement-package-final-v1': 0, 'surface-supplement-comparison-v1': 1,
                      'surface-supplement-full-v1': 0, 'surface-supplement-runtime-v1': 0,
                      'surface-supplement-legacy-capture-v1': 0}
    assert {r['name']: r['exitCode'] for r in report['attempts']} == expected_exits
    for name, code in expected_exits.items():
        recorded = json.loads(attempts[name + '/result.json'])
        assert recorded == read('attempts/' + name + '/result.json')
        assert recorded['exitCode'] == code
    package = 'surface-supplement-package-final-v1'
    steps = read('attempts/' + package + '/steps.json')
    assert [r['exitCode'] for r in steps] == [0, 0, 1, 1]
    assert [r['expectedExitCode'] for r in steps] == [0, 0, 1, 1]
    assert steps[2]['command'] == ['consumer-build/InstalledConsumer', '--surface-baseline']
    assert steps[3]['command'] == ['consumer-build/InstalledConsumer', '--surface-input']
    binding = read('package/artifact-binding.json')
    package_inputs = read('package/inputs.json')
    runtime_inputs = read('runtime-proof/inputs.json')['files']
    for inputs in [package_inputs, runtime_inputs]:
        assert {n.removeprefix('install/'): v for n, v in inputs.items() if n.startswith('install/')} == binding['installedFiles']
    assert len(binding['installedFiles']) == 125
    assert runtime_inputs['consumer-build/InstalledConsumer'] == binding['consumerSha256']
    implementation = archive_data['implementation']
    for name, checksum in binding['consumerFiles'].items():
        assert package_inputs['consumer/' + name] == checksum
        assert hashlib.sha256(implementation['tests/consumer/' + name]).hexdigest() == checksum
    for name, checksum in binding['producerCriticalFiles'].items():
        if name.startswith('src/'):
            assert hashlib.sha256(implementation[name]).hexdigest() == checksum
    producer_inputs = attempts['surface-supplement-build-v5/inputs.json']
    assert hashlib.sha256(producer_inputs).hexdigest() == binding['producerSourceManifestSha256']
    assert read('qt/inputs.json')['sourceManifestSha256'] == binding['producerSourceManifestSha256']
    qt = (directory / 'qt/run.log').read_text()
    assert '100% tests passed, 0 tests failed out of 27' in qt
    component_log = (directory / 'qt/LastTest.log').read_text()
    for count in [5319, 5547]:
        assert f'Totals: {count} passed, 0 failed, 0 skipped, 0 blacklisted' in component_log
    assert sum('QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer' in line
               for line in (directory / 'package/check-installed.sh').read_text().splitlines()) == 31
    assert 'Installed catalog: 127 fixture captures passed without source/build import paths' in (directory / 'package/0.log').read_text()
    assert len(list((directory / 'catalogs').glob('*.png'))) == 127
    projected = json.loads(implementation['tests/consumer/native-surface-supplement-witnesses.json'])
    profiles = {prefix + protocol + '-' + backend + '-' + scale + '.json'
                for prefix, protocol, backend, scale in itertools.product(
                    ['', 'surface-modifier-', 'surface-baseline-', 'surface-input-'],
                    ['xcb', 'wayland'], ['software', 'opengl'], ['standard', 'scaled'])}
    assert {p.name for p in (directory / 'runtime').glob('*.json')} == profiles | {'environment.json'}
    for name in profiles:
        row = read('runtime/' + name)
        assert row['physicalDisplay'] is False and row['hardwareAcceleration'] is False
        prefix = name.removesuffix('.json')
        assert digest(directory / 'runtime' / row['sessionCapture']) == row['sessionCaptureSha256']
        assert digest(directory / 'runtime' / (prefix + '.png')) == row['windowCaptureSha256']
        for kind in ['baseline', 'input']:
            if name.startswith('surface-' + kind + '-'):
                validate_profile(row, kind, projected)
    spec = importlib.util.spec_from_file_location('surface_supplement_comparison', ROOT / 'scripts/compare-surface-supplement.py')
    compare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compare)
    assert digest(ROOT / 'scripts/compare-surface-supplement.py') == hashlib.sha256(implementation['scripts/compare-surface-supplement.py']).hexdigest()
    with tempfile.TemporaryDirectory() as temporary:
        target = Path(temporary) / 'comparison'
        assert compare.compare(directory / 'captures', target) == 1
        replay = json.loads((target / 'comparison.json').read_text())
        assert replay == read('comparison/comparison.json')
        assert replay['summary'] == report['strictComparison']
    regression = read('regression/surface-supplement-catalog-regression.json')
    assert regression['pngs'] == regression['metadata'] == 127
    assert regression['changedMetadata'] == []
    assert len(regression['changedPngs']) == 2
    old_directory = ROOT / 'evidence/development/surface-modifier'
    old_manifest = json.loads((old_directory / 'packages-and-host-files.json').read_text())
    old_prefix = 'surface-matrix-package-v3/catalog-evidence/'
    assert len(regression['pairs']) == 254
    for pair in regression['pairs']:
        assert pair['before'] == old_manifest[old_prefix + pair['file']]['sha256']
        assert pair['after'] == digest(directory / 'catalogs' / pair['file'])
    with tarfile.open(old_directory / 'packages-and-host.tar.gz') as old_archive:
        for name in regression['changedPngs']:
            before = old_archive.extractfile(old_prefix + name).read()
            assert hashlib.sha256(before).hexdigest() == old_manifest[old_prefix + name]['sha256']
            assert regression['changedImageMetrics'][name] == compare.pixel_metrics(
                io.BytesIO(before), directory / 'catalogs' / name)
    legacy = read('regression/surface-supplement-legacy-pixels.json')
    assert legacy['accepted'] is False and len(legacy['changed']) == 80
    assert (legacy['improvedChangedPixels'], legacy['unchangedChangedPixels'], legacy['worsenedChangedPixels']) == (24, 50, 6)
    legacy_regression = read('regression/surface-supplement-legacy-regression.json')
    assert legacy_regression['images'] == legacy_regression['metadata'] == 416
    assert len(legacy_regression['pairs']) == 832
    changed_images = []
    changed_metadata = []
    for pair in legacy_regression['pairs']:
        name = pair['file']
        assert digest(old_directory / 'captures' / name) == pair['beforeSha256']
        assert hashlib.sha256(archive_data['legacy'][name]).hexdigest() == pair['afterSha256']
        if pair['beforeSha256'] != pair['afterSha256']:
            (changed_images if name.endswith('.png') else changed_metadata).append(name)
    assert sorted(changed_images) == sorted(legacy_regression['changedPngs'])
    assert sorted(changed_metadata) == sorted(legacy_regression['changedMetadata'])
    assert len(changed_metadata) == 8
    assert {r['file'] for r in legacy['changed']} == set(changed_images)
    improved = equal = worsened = 0
    for row in legacy['changed']:
        name = row['file']
        reference = ROOT / 'evidence/reference-investigations/surface-modifier-20261016/captures' / name.removeprefix('surface-')
        before = compare.pixel_metrics(reference, old_directory / 'captures' / name)
        after = compare.pixel_metrics(reference, io.BytesIO(archive_data['legacy'][name]))
        assert row['before'] == before and row['after'] == after
        improved += after['changedPixels'] < before['changedPixels']
        equal += after['changedPixels'] == before['changedPixels']
        worsened += after['changedPixels'] > before['changedPixels']
    assert (improved, equal, worsened) == (24, 50, 6)
    return replay['summary']


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
