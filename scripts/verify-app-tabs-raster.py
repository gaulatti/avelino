#!/usr/bin/env python3
"""Audit the supplemental badge fix without accepting the native mirror."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/app-tabs-raster-20261017'
BASE = 'c3f84a00f73a291b8f344066ee1bfd85815567f8'
spec = importlib.util.spec_from_file_location('app_tabs_prior', ROOT / 'scripts/verify-app-tabs-candidate.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)


def validate_report(report):
    assert report['baseRevision'] == BASE
    assert report['reference'] == prior.comparison.capture.REFERENCE
    assert report['accepted'] is False and report['status'] == 'verification-pending'
    assert report['expectedImagesChanged'] is False
    assert report['tolerance'] == 'none' and report['approvedExceptions'] == []
    assert report['strictComparison'] == dict(cases=1208, exactMatches=56, pixelMatches=56,
        nativeFrameMatches=940, stateMatches=1208, retainedRestoreObservations=48,
        retainedRestorePixelMatches=48, sizingObservations=0, nativeSizingContexts=344,
        nativeSizingQueries=5160)
    assert report['validation'] == dict(fullQtTargets=37, retainedStatesPerDpr=28, dprs=[1, 2],
        operatorStates=28, operatorExactStates=28, installedModes=35, catalogCaptures=143,
        legacyCatalogs=139, virtualProfiles=8, physicalDisplay=False, hardwareAcceleration=False)
    assert report['remainingAcceptance'] == ['nativeGeometryRasterAndLabelFitting', 'nativeSizing',
        'nativeGenericIdentity', 'nativeKeyboardAndInputTiming', 'nativeAccessibility',
        'physicalDisplaysInput', 'readers', 'independentMachineReplay']


class Payloads:
    def __init__(self, directory, report):
        self.directory = directory
        self.mapping = json.loads((directory / 'payload-map.json').read_text())
        assert self.mapping['baseRevision'] == BASE
        assert self.mapping['sourceAttempts'] == ['app-tabs-raster-build-old-v1', 'app-tabs-raster-build-old-v2'] + [
            f'app-tabs-raster-build-new-v{i}' for i in range(1, 5)]
        assert self.mapping['priorDirectory'] == str(prior.DIRECTORY.relative_to(ROOT))
        self.blobs = prior.verify_archives(directory, report)
        old = json.loads((prior.DIRECTORY / 'candidate.json').read_text())
        self.old_archives = old['archives']
        self.old_blobs = {}
        self.git = {}
        self.verified = set()
        self.verified_hashes = set()
        self.sources = {}
        tree = {}
        for row in subprocess.check_output(['git', 'ls-tree', '-rz', '--full-tree', BASE], cwd=ROOT).split(b'\0'):
            if row:
                head, name = row.split(b'\t', 1)
                tree[name.decode()] = head.decode().split()[2]
        objects = {}
        for record in self.mapping['payloads'].values():
            location = record['location']
            if location['kind'] == 'git':
                objects[location['gitObject']] = location['path']
        with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE) as reader:
            for object_id, path in objects.items():
                assert tree[path] == object_id
                reader.stdin.write((object_id + '\n').encode())
                reader.stdin.flush()
                oid, kind, size = reader.stdout.readline().decode().split()
                assert oid == object_id and kind == 'blob'
                self.git[object_id] = reader.stdout.read(int(size))
                assert reader.stdout.read(1) == b'\n'
            reader.stdin.close()
            assert reader.wait() == 0

    def data(self, key):
        if '/source/' in key and key.split('/source/', 1)[0] in self.mapping['sourceAttempts']:
            attempt, name = key.split('/source/', 1)
            if attempt not in self.sources:
                self.sources[attempt] = self.json(attempt + '/inputs.json')['sourceFiles']
            checksum = self.sources[attempt][name]
        else:
            checksum = self.mapping['records'][key]
        record = self.mapping['payloads'][checksum]
        assert record['sha256'] == checksum
        location = record['location']
        for field in ['path', 'member', 'archive']:
            if field in location:
                assert not Path(location[field]).is_absolute() and '..' not in Path(location[field]).parts
        if location['kind'] == 'git':
            data = self.git[location['gitObject']]
        elif location['kind'] == 'blob':
            data = self.blobs[location['member']]
        elif location['kind'] == 'priorFile':
            data = (prior.DIRECTORY / location['path']).read_bytes()
        else:
            assert location['kind'] == 'priorArchive'
            name = location['archive']
            if name not in self.old_blobs:
                entry = next(v for v in self.old_archives.values() if v['archive'] == name)
                self.old_blobs[name] = prior.verify_archives(prior.DIRECTORY, {'archives': {name: entry}})
            data = self.old_blobs[name][location['member']]
        if checksum not in self.verified_hashes:
            assert len(data) == record['bytes']
            assert hashlib.sha256(data).hexdigest() == checksum, key
            self.verified_hashes.add(checksum)
        inspection = (Path(key).suffix, record['sha256'])
        if inspection not in self.verified:
            assert not prior.boundary.inspect_payload(key, data), key
            self.verified.add(inspection)
        assert not prior.boundary.forbidden_path(key), key
        return data

    def json(self, key):
        return json.loads(self.data(key))


def same(a, b):
    assert a.size == b.size
    return a.convert('RGBA').tobytes() == b.convert('RGBA').tobytes()


def sunset_mask(data):
    with Image.open(io.BytesIO(data)) as raw:
        image = raw.convert('RGBA')
    channels = [image.getchannel(c).point([255 if x == v else 0 for x in range(256)])
        for c, v in [('R', 255), ('G', 150), ('B', 119), ('A', 255)]]
    result = channels[0]
    for channel in channels[1:]:
        result = ImageChops.multiply(result, channel)
    return result


def verify_badge_masks(directory, payloads):
    report = json.loads((directory / 'sunset-mask-diagnostic.json').read_text())
    assert report['accepted'] is False and len(report['rows']) == 312
    expected = {r['path']: r for r in prior.comparison.capture.rows() if r['kind'] == 'closed'}
    for row in report['rows']:
        native = sunset_mask((ROOT / expected[row['path']]['reference']).read_bytes())
        images = [sunset_mask((prior.DIRECTORY / 'captures' / row['path']).read_bytes()),
            sunset_mask(payloads.data('app-tabs-raster-matrix-v1/captures/' + row['path'])),
            sunset_mask((directory / 'captures' / row['path']).read_bytes())]
        assert native.getbbox() and row['nativeBounds'] == list(native.getbbox())
        for image, count, bounds in zip(images,
                ['oldMismatchPixels', 'initialLayerMismatchPixels', 'rasterMismatchPixels'],
                ['oldBounds', 'initialLayerBounds', 'rasterBounds']):
            assert row[count] == sum(ImageChops.difference(native, image).histogram()[1:])
            assert row[bounds] == (list(image.getbbox()) if image.getbbox() else None)
        assert row['rasterMaskSameAsOld'] is (images[0].tobytes() == images[2].tobytes())
        assert row['rasterMismatchPixels'] <= row['oldMismatchPixels']
    for dpr in [1, 2]:
        rows = [r for r in report['rows'] if r['dpr'] == dpr]
        improved = sum(r['rasterMismatchPixels'] < r['oldMismatchPixels'] for r in rows)
        assert report['summary'][str(dpr)] == dict(cases=156, improved=improved, worse=0,
            same=156-improved, identicalOldMasks=156-improved)
        assert improved == (0 if dpr == 1 else 8)


def verify_retained(payloads, producer, failures):
    keys = [name for name in payloads.mapping['records']
        if name.startswith(producer + '/') and name.endswith('/observations.json')
        and ('/app-tabs-raster/' in name or '/app-tabs-raster.' in name)]
    assert len(keys) == 2
    seen = []
    for key in keys:
        report = payloads.json(key)
        assert report['accepted'] is False and report['clicks'] == 27
        assert len(report['states']) == 28
        seen.append(report['dpr'])
        failed = []
        for row in report['states']:
            prefix = key.removesuffix('observations.json') + row['phase']
            with Image.open(io.BytesIO(payloads.data(prefix + '-retained.png'))) as actual, \
                    Image.open(io.BytesIO(payloads.data(prefix + '-fresh.png'))) as expected:
                identical = same(actual, expected)
                if not failures and row['phase'] not in ['empty', 'disabled', 'disabled-home']:
                    colors = actual.convert('RGBA').getcolors(actual.width * actual.height)
                    assert any(color == (255, 150, 119, 255) for count, color in colors), row['phase']
            assert row['identical'] is identical
            if not identical:
                failed.append(row['phase'])
        assert failed == failures
        assert report['mismatches'] == len(failures)
    assert sorted(seen) == [1, 2]


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
        assert prior.digest(directory / name) == checksum, name
    payloads = Payloads(directory, report)
    for key in payloads.mapping['records']:
        assert not Path(key).is_absolute() and '..' not in Path(key).parts
        payloads.data(key)
    for attempt in payloads.mapping['sourceAttempts']:
        source = payloads.json(attempt + '/inputs.json')['sourceFiles']
        for name in source:
            payloads.data(attempt + '/source/' + name)
    for key in payloads.mapping['records']:
        if not key.endswith('/inputs.json'):
            continue
        raw = payloads.json(key)
        if 'sourceFiles' in raw:
            continue
        for name, checksum in raw.get('files', raw).items():
            if isinstance(checksum, str) and len(checksum) == 64:
                actual = payloads.mapping['records'][key.removesuffix('inputs.json') + name]
                assert actual == checksum
    for attempt in read('attempts.json'):
        assert payloads.json(attempt['result']).get('exitCode') == attempt['exitCode']
    opacity = payloads.json('app-tabs-native-opacity-v1/observations.json')
    assert opacity['accepted'] is False and len(opacity['rows']) == 8
    assert sum(r['opaqueWhiteInteriorSamples'] for r in opacity['rows']) == 136
    for row in opacity['rows']:
        for source in row['source']:
            assert prior.digest(ROOT / source['path']) == source['sha256']
        assert row['opaqueWhiteInteriorSamples'] == (0 if row['dpr'] == 1 else 34)
        if row['dpr'] == 2:
            assert row['disabledSampleColors'] == [dict(
                rgb=[255, 229, 221] if row['appearance'] == 'light' else [198, 174, 170], pixels=34)]
    binding = read('package/artifact-binding.json')
    assert binding['projectionSha256'] == prior.digest(prior.comparison.capture.PROJECTION)
    assert binding['iconMetricsSha256'] == prior.digest(ROOT / 'tests/consumer/native-app-tab-icon-metrics.json')
    producer = binding['producerAttempt']
    source = payloads.json(producer + '/inputs.json')['sourceFiles']
    sequence = json.loads(payloads.data(producer + '/source/tests/components/app-tabs-raster-sequence.json'))
    assert sequence == json.loads((prior.DIRECTORY / 'operator/phases.json').read_text())
    prior.validate_producer_inputs(binding, source)
    for name, checksum in source.items():
        assert hashlib.sha256(payloads.data(producer + '/source/' + name)).hexdigest() == checksum
    for name, checksum in binding['installedFiles'].items():
        assert hashlib.sha256(payloads.data('final/install/' + name)).hexdigest() == checksum
        for field in ['producerAttempt', 'packageAttempt', 'operatorAttempt', 'runtimeAttempt', 'readinessAttempt']:
            assert payloads.mapping['records'][binding[field] + '/install/' + name] == checksum
    assert hashlib.sha256(payloads.data('final/consumer-build/InstalledConsumer')).hexdigest() == binding['consumerSha256']
    full = read('qt/full/result.json')
    assert full == payloads.json(binding['fullTestAttempt'] + '/result.json')
    assert full['exitCode'] == 0 and full['producer'] == producer
    assert '100% tests passed, 0 tests failed out of 37' in (directory / 'qt/full/run.log').read_text()
    verify_retained(payloads, 'app-tabs-raster-build-old-v2', ['disabled', 'disabled-home'])
    verify_retained(payloads, producer, [])
    actual = prior.comparison.compare(directory / 'captures')
    assert actual == read('comparison.json') and actual['summary'] == report['strictComparison']
    verify_badge_masks(directory, payloads)
    operator = read('operator/result.json')
    assert operator['status'] == 'passed' and operator['exitCode'] == 0
    assert operator['physicalDisplay'] is False and operator['controls'] == 14
    assert len(operator['records']) == 28 and sum(r['click'] is not None for r in operator['records']) == 27
    for row in operator['records']:
        assert row['passed'] is True and row['viewport'] == [0, 180, 640, 400]
        with Image.open(directory / 'operator' / row['reference']) as expected:
            for observation in row['attempts']:
                path = directory / 'operator' / observation['path']
                assert prior.digest(path) == observation['sha256']
                with Image.open(path) as image:
                    identical = same(image.crop((0, 180, 640, 580)), expected)
                assert observation['exactViewportMatch'] is identical
        assert row['attempts'][-1]['exactViewportMatch'] is True
    previous = json.loads((prior.DIRECTORY / 'operator/result.json').read_text())['records']
    unchanged = read('operator/prior-operator-comparison.json')['rows']
    assert len(unchanged) == 28
    for old, new, observed in zip(previous, operator['records'], unchanged):
        assert old['phase'] == new['phase'] == observed['phase']
        with Image.open(prior.DIRECTORY / 'operator' / old['attempts'][-1]['path']) as first, \
                Image.open(directory / 'operator' / new['attempts'][-1]['path']) as last:
            first, last = [image.convert('RGBA').crop((0, 180, 640, 580)) for image in [first, last]]
            assert observed['identical'] is same(first, last)
            bounds = ImageChops.difference(first, last).convert('RGB').getbbox()
            assert observed['differenceBounds'] == (list(bounds) if bounds else None)
    assert [r['phase'] for r in unchanged if not r['identical']] == ['disabled', 'disabled-home']
    assert read('readiness/result.json')['exitCode'] == read('runtime-proof/result.json')['exitCode'] == 0
    assert len(list((directory / 'catalogs').glob('*.png'))) == 143
    assert read('catalogs/catalog-results.json')['status'] == 'passed'
    legacy = read('legacy-catalogs.json')
    assert len(legacy) == 139
    for row in legacy:
        for suffix, key in [('', 'pngSha256'), ('.json', 'metadataSha256')]:
            name = row['path'] + suffix
            assert prior.digest(directory / 'catalogs' / name) == row[key]
            assert prior.digest(ROOT / 'evidence/development/media-library-caption-20261017/catalogs' / name) == row[key]
    profiles = sorted((directory / 'runtime').glob('app-tabs-*.json'))
    assert len(profiles) == 8
    runtime_images = {}
    for path in profiles:
        row = json.loads(path.read_text())
        assert row['structuralChecks'] == 'passed' and row['images'] == row['stateMatches'] == 151
        assert row['physicalDisplay'] is row['hardwareAcceleration'] is row['accepted'] is False
        for history in row['histories']:
            for index in [0, 16]:
                name = path.stem + '-' + history['configuration']['id'] + '-history-step' + str(index) + '.png'
                runtime_images['runtime/' + name] = payloads.data(binding['runtimeAttempt'] + '/display-evidence/' + name)
    restores = prior.runtime_restores(directory, runtime_images)
    assert restores == read('runtime-restores.json') and restores['observations'] == 48
    for name in ['readiness/environment.json', 'runtime-proof/environment.json', 'runtime/environment.json']:
        environment = read(name)
        assert environment['consumerSha256'] == binding['consumerSha256']
        assert {n.removeprefix('install/'): s for n, s in environment['installedFiles'].items()} == binding['installedFiles']
    print('App-tab badge raster: before/after DPR 1/2 and 28 XTest states verified; native mirror remains pending')
    return report


if __name__ == '__main__':
    verify()
