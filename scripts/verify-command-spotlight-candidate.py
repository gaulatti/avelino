#!/usr/bin/env python3
"""Recompute sealed Linux spotlight observations without approving parity."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tarfile
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/command-spotlight-20261017'
GATES = ['nativeFontsSymbolsRaster', 'retainedRasterStability', 'nativeQueryCallbackAndFocusTiming',
    'genericIdentityAndBuilderTiming', 'lazyMeasurementEviction', 'nativeSizing',
    'nativeAccessibility', 'physicalInputDisplay', 'readers', 'independentMachineReplay']


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


capture = module('spotlight_capture', 'scripts/capture-command-spotlight.py')
boundary = module('spotlight_boundary', 'scripts/check-linux-boundary.py')
digest = lambda data: hashlib.sha256(data).hexdigest()


def validate_report(report):
    assert report['reference'] == capture.REFERENCE
    assert report['baseRevision'] == '3a52764fbad843025446c3e33a305d40b5ad7c4c'
    assert report['accepted'] is False and report['status'] == 'verification-pending'
    assert report['expectedImagesChanged'] is False
    assert report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    assert report['remainingAcceptance'] == GATES
    assert report['strictComparison']['accepted'] is False
    assert report['strictComparison']['cases'] == 1792
    required = dict(qtTargets=39, focusedDpr1=11, focusedDpr2=11, contracts=730,
        malformedInputs=14, isolatedCatalogDefinitions=32, independentModes=36,
        installedCatalogs=147, unchangedPriorCatalogs=143, nativePairs=1792,
        virtualProfiles=8, virtualRestoreObservations=64, virtualInitialPixelMatches=53,
        virtualExpectedInitialPixelMatches=56, virtualRestoreMatchesNative=61, operatorControls=15, operatorStates=23, operatorClicks=22,
        operatorStatus='passed', physicalDisplay=False, hardwareAcceleration=False)
    assert all(report['validation'][key] == value for key, value in required.items())


def verify(directory=DIRECTORY):
    read = lambda path: json.loads((directory / path).read_text())
    report = read('report.json')
    validate_report(report)
    files = read('files.json')
    actual_files = {str(path.relative_to(directory)) for path in directory.rglob('*')
        if path.is_file() and path.name != 'files.json'}
    assert actual_files == set(files), 'Sealed file inventory differs'
    for name, record in files.items():
        data = (directory / name).read_bytes()
        assert len(data) == record['bytes'] and digest(data) == record['sha256'], name
    archived = {}
    for record in report['archives'].values():
        path = directory / record['archive']
        assert digest(path.read_bytes()) == record['sha256']
        manifest = read(record['manifest'])
        with tarfile.open(path) as stream:
            members = stream.getmembers()
            assert len(members) == record['files'] == len(manifest)
            assert sum(member.size for member in members) == record['expandedBytes'] < 48 * 1024 * 1024
            assert {member.name for member in members} == set(manifest)
            for member in members:
                assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
                assert not boundary.forbidden_path(member.name)
                data = stream.extractfile(member).read()
                assert len(data) == manifest[member.name]['bytes'] and digest(data) == manifest[member.name]['sha256']
                assert member.name not in archived
                archived[member.name] = data
    replay = read('source-replay.json')
    objects = {}
    tree = {}
    for row in subprocess.check_output(['git', 'ls-tree', '-rz', '--full-tree', replay['baseRevision']], cwd=ROOT).split(b'\0'):
        if row:
            head, name = row.split(b'\t', 1)
            tree[name.decode()] = head.decode().split()[2]
    for name, record in replay['baseFiles'].items():
        assert tree[name] == record['gitBlob'] and not boundary.forbidden_path(name)
        objects[record['gitBlob']] = record['sha256']
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as reader:
        for object_id, checksum in objects.items():
            reader.stdin.write((object_id + '\n').encode()); reader.stdin.flush()
            header = reader.stdout.readline().split(); assert header[0].decode() == object_id and header[1] == b'blob'
            data = reader.stdout.read(int(header[2])); assert reader.stdout.read(1) == b'\n' and digest(data) == checksum
        reader.stdin.close(); assert reader.wait() == 0
    for checksum, record in replay['blobs'].items():
        data = archived[record['path']]
        assert len(data) == record['bytes'] and digest(data) == checksum
    for snapshot, mapping in replay['snapshots'].items():
        reconstructed = {}
        for name, record in mapping.items():
            assert not boundary.forbidden_path(name)
            if record['kind'] == 'git':
                assert record['path'] == name and name in replay['baseFiles']
                reconstructed[name] = replay['baseFiles'][name]['sha256']
            else:
                assert record['kind'] == 'blob' and record['sha256'] in replay['blobs']
                reconstructed[name] = record['sha256']
        inputs = read('attempts/' + snapshot + '/inputs.json')
        assert reconstructed == inputs['sourceFiles' if 'build-v' in snapshot else 'driverFiles']
    binding = read('package/artifact-binding.json')
    producer = read('attempts/command-spotlight-build-v7/inputs.json')['sourceFiles']
    critical = {name: value for name, value in producer.items()
        if name.startswith(('src/', 'samples/', 'assets/', 'tokens/', 'cmake/', 'tests/components/', 'tests/consumer/'))
        or name in ['CMakeLists.txt', 'CMakePresets.json']}
    assert critical == binding['producerCriticalFiles']
    full_producer = read('attempts/command-spotlight-build-v5/inputs.json')['sourceFiles']
    product = lambda values: {name: value for name, value in values.items()
        if name.startswith(('src/', 'samples/', 'assets/', 'cmake/', 'tests/consumer/')) or name == 'CMakeLists.txt'}
    module_binding = read('qt/module-binding.json')
    assert product(full_producer) == product(producer) == module_binding['compiledProductSources']
    assert module_binding['installedFiles'] == binding['installedFiles']
    assert module_binding['fullRunExitCode'] == 8 and module_binding['correctedTargetsExitCode'] == 0
    assert binding['consumerFiles'] == {name.removeprefix('tests/consumer/'): value
        for name, value in producer.items() if name.startswith('tests/consumer/')}
    for name, checksum in binding['installedFiles'].items(): assert digest(archived['install/' + name]) == checksum
    assert digest(archived['consumer-build/InstalledConsumer']) == binding['consumerSha256']
    pixels = {row['fixture']: row for row in read('comparison/pixels/comparison.json')['results']}
    frames = states = retained = exact = 0
    for expected in capture.rows():
        path = directory / 'captures' / expected['path']
        actual = json.loads(Path(str(path) + '.json').read_text())
        measured = capture.observations(expected, actual)
        frames += measured['nativeFrameStatus'] == 'passed'
        states += measured['stateStatus'] == 'passed'
        retained += measured['retainedRasterStatus'] == 'passed'
        record = pixels[expected['reference']]
        assert record['referenceSHA256'] == digest((ROOT / expected['reference']).read_bytes())
        assert record['candidateSHA256'] == digest(path.read_bytes())
        with Image.open(ROOT / expected['reference']) as source, Image.open(path) as candidate:
            assert source.size == candidate.size == (720 * expected['dpr'], 520 * expected['dpr'])
            delta = ImageChops.difference(source.convert('RGB'), candidate.convert('RGB'))
            alpha = ImageChops.difference(source.convert('RGBA').getchannel('A'), candidate.convert('RGBA').getchannel('A'))
            red, green, blue = delta.split()
            maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
            changed = delta.width * delta.height - maximum.histogram()[0]
            assert changed == record['changedPixels'] and maximum.getextrema()[1] == record['maximumChannelError']
            passed = not delta.getbbox() and not alpha.getbbox()
            assert record['status'] == ('passed' if passed else 'failed')
            exact += passed
    assert len(pixels) == 1792
    summary = report['strictComparison']
    assert (exact, frames, states, retained) == tuple(summary[key] for key in ['exactPixels', 'frames', 'states', 'retainedRasterChecks'])
    profiles = list((directory / 'runtime').glob('command-spotlight-*.json'))
    assert {path.stem for path in profiles} == {
        f'command-spotlight-{protocol}-{backend}-{configuration}'
        for protocol in ['xcb', 'wayland'] for backend in ['software', 'opengl']
        for configuration in ['standard', 'scaled']}
    for path in profiles:
        row = json.loads(path.read_text())
        _, _, protocol, backend, configuration = path.stem.split('-')
        assert row['platform'] == protocol and row['graphicsApi'] == (1 if backend == 'software' else 3)
        assert row['dpr'] == (1 if configuration == 'standard' else 2)
        assert row['appearance'] == ('light' if configuration == 'standard' else 'dark')
        assert row['textScale'] == (1 if configuration == 'standard' else 1.5)
        assert row['accepted'] is False and row['structuralChecks'] == 'passed' and row['images'] == 224
        assert row['pointerDeliveries'] == 40 and row['keyDeliveries'] == 8
        assert row['nativeRasterAcceptance'] == row['physicalInputAcceptance'] == row['readerAcceptance'] == 'pending'
    restores = read('runtime-proof/retained-restores.json')
    assert restores['observations'] == len(restores['records']) == 64 and restores['matchesExpected'] == 61
    for row in restores['records']:
        with Image.open(io.BytesIO(archived['runtime/' + row['initial']])) as initial, Image.open(io.BytesIO(archived['runtime/' + row['restored']])) as restored:
            delta = ImageChops.difference(initial.convert('RGBA'), restored.convert('RGBA'))
            matches = not delta.getbbox(alpha_only=False)
            assert matches == row['matchesInitialPixels']
            assert row['expectedInitialPixelMatch'] == (row['configuration'] != 'many-buttons')
    assert sum(row['matchesInitialPixels'] for row in restores['records']) == 53
    operator = read('operator/result.json')
    assert operator['status'] == 'passed' and len(operator['records']) == 23 and all(row['passed'] for row in operator['records'])
    top_reference = directory / 'operator/references/top.png'
    for row in operator['records']:
        if 'attempts' in row:
            observed = row['attempts'][-1]
            path = directory / 'operator' / observed['path']
            assert digest(path.read_bytes()) == observed['sha256']
            reference = directory / 'operator' / row['reference']
        else:
            path = directory / 'operator' / row['path']
            assert digest(path.read_bytes()) == row['sha256']
            reference = top_reference
        with Image.open(path) as source, Image.open(reference) as expected:
            actual = source.convert('RGBA').crop((0, 180, 720, 700))
            equal = actual.tobytes() == expected.convert('RGBA').tobytes()
            assert equal is (row['phase'] != 'scroll-bottom')
    regressions = read('regression/catalogs.json')['records']
    assert len(regressions) == 143
    for row in regressions:
        assert digest((directory / 'catalogs' / row['path']).read_bytes()) == row['pngSha256']
        assert digest((directory / 'catalogs' / (row['path'] + '.json')).read_bytes()) == row['metadataSha256']
    print(f'Spotlight: 1792 strict pairs, {frames} frame sets, {states} state records; acceptance pending')


if __name__ == '__main__':
    verify()
