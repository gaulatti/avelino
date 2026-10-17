#!/usr/bin/env python3
"""Recompute the sealed app-tab candidate while preserving failed mirror gates."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tarfile
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/app-tabs-20261017'
BASE = '685f7442cb87785aea6563c2817ea4f28845816e'
GATES = ['nativeGeometryRasterAndLabelFitting', 'retainedCallerRasterStability', 'nativeSizing',
    'nativeGenericIdentity', 'nativeKeyboardAndInputTiming', 'nativeAccessibility',
    'physicalDisplaysInput', 'readers', 'independentMachineReplay']


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


comparison = module('app_tab_comparison', 'scripts/compare-app-tabs-captures.py')
boundary = module('app_tab_boundary', 'scripts/check-linux-boundary.py')
offset = module('app_tab_offset', 'scripts/verify-app-tab-offset.py')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_report(report):
    assert report['reference'] == comparison.capture.REFERENCE and report['baseRevision'] == BASE
    assert report['accepted'] is False and report['status'] == 'verification-pending'
    assert report['tolerance'] == 'none' and report['approvedExceptions'] == []
    assert report['expectedImagesChanged'] is False and report['strictComparisonStatus'] == 'failed'
    assert report['remainingAcceptance'] == GATES
    assert report['strictComparison'] == dict(cases=1208, exactMatches=56, pixelMatches=56,
        nativeFrameMatches=940, stateMatches=1208, retainedRestoreObservations=48,
        retainedRestorePixelMatches=48, sizingObservations=0, nativeSizingContexts=344,
        nativeSizingQueries=5160)
    expected = dict(componentChecksDpr1=17, componentChecksDpr2=17, fullQtTargets=34,
        additionalCatalogTargets=1, malformedConfigurations=18, isolatedCatalogInputs=43,
        isolatedCatalogRefusals=26, independentModes=35, catalogCaptures=143, legacyPngs=139,
        legacyMetadata=139, virtualProfiles=8, operatorControls=14, operatorClicks=27,
        virtualRestoreObservations=48, virtualRestorePixelMatches=42,
        operatorStates=28, operatorExactStates=26, operatorStatus='failed',
        strictDefaultExitCode=1, strictImageExitCode=1, physicalDisplay=False, hardwareAcceleration=False)
    assert all(report['validation'][key] == value for key, value in expected.items())


def validate_producer_inputs(binding, producer):
    critical = {name: checksum for name, checksum in producer.items()
        if name.startswith(('src/', 'samples/', 'assets/', 'tokens/', 'cmake/', 'tests/components/', 'tests/consumer/'))
        or name in ['CMakeLists.txt', 'CMakePresets.json']}
    assert binding['producerCriticalFiles'] == critical, 'Incomplete frozen producer binding'


def verify_archives(directory, report):
    archived = {}
    for record in report['archives'].values():
        manifest = json.loads((directory / record['manifest']).read_text())
        with tarfile.open(directory / record['archive']) as stream:
            members = stream.getmembers()
            assert len(members) == len(manifest) == record['files']
            assert sum(m.size for m in members) < 48 * 1024 * 1024
            assert {m.name for m in members} == set(manifest)
            for member in members:
                assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
                data = stream.extractfile(member).read()
                assert len(data) == manifest[member.name]['bytes']
                assert hashlib.sha256(data).hexdigest() == manifest[member.name]['sha256']
                assert member.name not in archived
                archived[member.name] = data
    return archived


def verify_sources(directory, archived):
    read = lambda name: json.loads((directory / name).read_text())
    base, replay = read('replay/base-files.json'), read('replay/source-overlays.json')
    assert base['baseRevision'] == replay['baseRevision'] == BASE
    tree = {}
    for row in subprocess.check_output(['git', 'ls-tree', '-rz', '--full-tree', BASE], cwd=ROOT).split(b'\0'):
        if row:
            head, name = row.split(b'\t', 1)
            tree[name.decode()] = head.decode().split()[2]
    objects = {}
    for name, record in base['files'].items():
        assert not boundary.forbidden_path(name) and tree[name] == record['gitObject']
        if record['gitObject'] in objects:
            assert objects[record['gitObject']] == record['sha256']
        objects[record['gitObject']] = record['sha256']
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE) as reader:
        for object_id, checksum in objects.items():
            reader.stdin.write((object_id + '\n').encode())
            reader.stdin.flush()
            actual_id, kind, size = reader.stdout.readline().decode().split()
            assert actual_id == object_id and kind == 'blob'
            data = reader.stdout.read(int(size))
            assert hashlib.sha256(data).hexdigest() == checksum
            assert reader.stdout.read(1) == b'\n'
        reader.stdin.close()
        assert reader.wait() == 0
    inspected = set()
    def logical_input(path, checksum):
        key = path, checksum
        data = archived['blobs/' + checksum]
        assert hashlib.sha256(data).hexdigest() == checksum
        if key not in inspected:
            assert not boundary.inspect_payload(path, data), path
            inspected.add(key)
    for name, overlay in replay['attempts'].items():
        manifest = read('attempts/' + name + '/inputs.json')['sourceFiles']
        assert set(overlay) <= set(manifest)
        for path, checksum in manifest.items():
            if path in overlay:
                assert overlay[path] == checksum
                logical_input(path, checksum)
            else:
                assert base['files'][path]['sha256'] == checksum
    for manifest in read('replay/package-inputs.json').values():
        for path, checksum in manifest.items():
            logical_input(path, checksum)
    for record in read('replay/diagnostic-outputs.json').values():
        location = record['location']
        data = (directory / location.removeprefix('candidate/')).read_bytes() if location.startswith('candidate/') else archived[location]
        assert hashlib.sha256(data).hexdigest() == record['sha256']


def runtime_restores(directory, archived):
    records = []
    for path in sorted((directory / 'runtime').glob('app-tabs-*.json')):
        report = json.loads(path.read_text())
        for history in report['histories']:
            prefix = path.stem + '-' + history['configuration']['id'] + '-history-step'
            initial, restore = [prefix + str(index) + '.png' for index in [0, 16]]
            with Image.open(io.BytesIO(archived['runtime/' + initial])) as first, Image.open(io.BytesIO(archived['runtime/' + restore])) as last:
                assert first.size == last.size
                difference = ImageChops.difference(first.convert('RGBA'), last.convert('RGBA'))
                identical = all(bounds == (0, 0) for bounds in difference.getextrema())
                bounds = difference.convert('RGB').getbbox()
            assert history['steps'][16]['step'] == 'restore'
            assert history['steps'][16]['matchesInitialPixels'] is identical
            records.append(dict(profile=path.stem, configuration=history['configuration']['id'],
                initial=initial, restore=restore, identical=identical,
                differenceBounds=list(bounds) if bounds else None))
    return dict(accepted=False, observations=len(records), exactMatches=sum(r['identical'] for r in records), rows=records)


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('candidate.json')
    validate_report(report)
    files = {str(p.relative_to(directory)) for p in directory.rglob('*')
        if p.is_file() and p.name not in ['candidate.json', 'README.md']}
    assert files == set(report['files'])
    for name, checksum in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == checksum, name
    archived = verify_archives(directory, report)
    binding = read('package/artifact-binding.json')
    assert binding['projectionSha256'] == digest(comparison.capture.PROJECTION)
    assert binding['iconMetricsSha256'] == digest(ROOT / 'tests/consumer/native-app-tab-icon-metrics.json')
    assert binding['producerSourceManifestSha256'] == digest(directory / 'qt/inputs.json')
    assert hashlib.sha256(archived['consumer-build/InstalledConsumer']).hexdigest() == binding['consumerSha256']
    for name, checksum in binding['installedFiles'].items():
        assert hashlib.sha256(archived['install/' + name]).hexdigest() == checksum
    validate_producer_inputs(binding, read('qt/inputs.json')['sourceFiles'])
    actual = comparison.compare(directory / 'captures')
    assert actual == read('comparison.json')
    assert actual['summary'] == report['strictComparison']
    assert offset.observe() == read('native-offset.json')
    for context in comparison.capture.CONTEXTS:
        name = comparison.capture.prefix(*context)
        row = read('captures/' + name + '.json')
        assert (row['appearance'], row['textScale'], row['dpr']) == context
        assert row['images'] == row['stateMatches'] == 151 and row['structuralChecks'] == 'passed'
        assert row['pointerDeliveries'] == 24 and row['retainedRestores'] == 6 and row['accepted'] is False
        assert read('captures/' + name + '-process.json')['exitCode'] == 0
        assert row['nativeSizingAcceptance'] == 'pending' and row['nativeAccessibilityAcceptance'] == 'unobserved'
    assert read('qt/full/result.json')['exitCode'] == 0
    assert '100% tests passed, 0 tests failed out of 34' in (directory / 'qt/full/run.log').read_text()
    assert '100% tests passed, 0 tests failed out of 1' in (directory / 'qt/catalog/LastTest.log').read_text() or 'Test Passed.' in (directory / 'qt/catalog/LastTest.log').read_text()
    assert read('readiness/result.json')['exitCode'] == read('runtime-proof/result.json')['exitCode'] == 0
    assert len(list((directory / 'catalogs').glob('*.png'))) == 143
    assert read('catalogs/catalog-results.json')['status'] == 'passed'
    legacy = read('regression/catalogs.json')
    assert len(legacy['records']) == 139
    for row in legacy['records']:
        current, previous = directory / 'catalogs' / row['path'], ROOT / legacy['baseline'] / row['path']
        assert digest(current) == digest(previous) == row['previousSha256'] == row['currentSha256']
        assert digest(Path(str(current) + '.json')) == digest(Path(str(previous) + '.json')) == row['previousMetadataSha256'] == row['currentMetadataSha256']
    profiles = sorted((directory / 'runtime').glob('app-tabs-*.json'))
    assert len(profiles) == 8
    for path in profiles:
        row = json.loads(path.read_text())
        assert row['structuralChecks'] == 'passed' and row['images'] == row['stateMatches'] == 151
        assert row['pointerDeliveries'] == 24
        assert row['retainedRestores'] == sum(h['steps'][16]['matchesInitialPixels'] for h in row['histories'])
        assert row['physicalDisplay'] is row['hardwareAcceleration'] is row['accepted'] is False
        data = archived['runtime/' + row['sessionCapture']]
        assert hashlib.sha256(data).hexdigest() == row['sessionCaptureSha256']
    restores = runtime_restores(directory, archived)
    assert restores == read('runtime-restores.json')
    assert restores['observations'] == 48 and restores['exactMatches'] == 42
    for name in ['readiness/environment.json', 'runtime-proof/environment.json', 'runtime/environment.json']:
        environment = read(name)
        assert environment['consumerSha256'] == binding['consumerSha256']
        assert {name.removeprefix('install/'): value for name, value in environment['installedFiles'].items()} == binding['installedFiles']
    operator = read('operator/result.json')
    assert operator['status'] == 'failed' and operator['exitCode'] == 1 and operator['physicalDisplay'] is False
    assert len(operator['records']) == 28 and sum(r['click'] is not None for r in operator['records']) == 27
    assert [r['phase'] for r in operator['records'] if not r['passed']] == ['disabled', 'disabled-home']
    for record in operator['records']:
        assert record['viewport'] == [0, 180, 640, 400]
        for attempt in record['attempts']:
            path = directory / 'operator' / attempt['path']
            assert digest(path) == attempt['sha256']
            with Image.open(path) as source, Image.open(directory / 'operator' / record['reference']) as target:
                candidate = source.convert('RGBA').crop((0, 180, 640, 580))
                identical = candidate.tobytes() == target.convert('RGBA').tobytes()
                difference = ImageChops.difference(candidate, target.convert('RGBA')).convert('RGB')
                assert attempt['differenceBounds'] == (list(difference.getbbox()) if difference.getbbox() else None)
            assert attempt['exactViewportMatch'] is identical
        assert record['passed'] is record['attempts'][-1]['exactViewportMatch']
    for attempt in report['attempts']:
        assert read('attempts/' + attempt['name'] + '/result.json')['exitCode'] == attempt['exitCode']
    verify_sources(directory, archived)
    print('AppTabBar: all 1208 strict pairs retained; 26/28 operator states match; mirror acceptance pending')
    return report


if __name__ == '__main__':
    verify()
