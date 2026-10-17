#!/usr/bin/env python3
"""Recompute sealed MediaLibrary observations without accepting native differences."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tarfile
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/media-library-20261017'
GATES = ['nativeGeometryAndRaster', 'retainedCallerRasterStability', 'nativeSizingAndWitnessDifference', 'nativeLazyViewportTiming',
    'nativeGenericIDContexts', 'nativeInputTiming', 'physicalDisplaysInput', 'readers',
    'independentMachineReferenceReplay']
spec = importlib.util.spec_from_file_location('media_candidate_inputs', ROOT / 'scripts/capture-media-library.py')
inputs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inputs)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_report(report):
    assert report['reference'] == inputs.REFERENCE and report['accepted'] is False
    assert report['baseRevision'] == '616abb40affb769029f80144a2f0807c79679f44'
    assert report['status'] == 'verification-pending' and report['remainingAcceptance'] == GATES
    assert report['tolerance'] == 'none' and report['approvedExceptions'] == []
    assert report['expectedImagesChanged'] is False and report['strictComparisonStatus'] == 'failed'
    summary = report['strictComparison']
    assert summary['cases'] == summary['stateMatches'] == 1608
    assert 0 <= summary['exactMatches'] <= summary['pixelMatches'] < 1608
    assert 0 <= summary['nativeFrameMatches'] < 1608 and 0 <= summary['nativeLifecycleMatches'] < 1608
    assert summary['retainedRestoreObservations'] == 48 and 0 <= summary['retainedRestorePixelMatches'] <= 48
    assert summary['sizingObservations'] == 0 and summary['nativeSizingContexts'] == 496 and summary['nativeSizingQueries'] == 7440
    assert {k: v['cases'] for k, v in summary['byKind'].items()} == dict(closed=496, edge=104, history=1008)
    validation = report['validation']
    for key, value in dict(componentChecksDpr1=11, componentChecksDpr2=11, fullQtTargets=33,
            malformedConfigurations=13, isolatedCatalogInputs=76, independentModes=34, catalogCaptures=139,
            legacyPngs=135, legacyMetadata=135, virtualProfiles=8, operatorControls=14,
            operatorClicks=23, operatorStates=24, strictDefaultExitCode=1, strictImageExitCode=1,
            fatalProcesses=8).items():
        assert validation[key] == value, key
    assert validation['physicalDisplay'] is False and validation['hardwareAcceleration'] is False

def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('candidate.json')
    validate_report(report)
    files = {str(p.relative_to(directory)) for p in directory.rglob('*')
        if p.is_file() and p.name not in ['candidate.json', 'README.md']}
    assert set(report['files']) == files
    for name, checksum in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == checksum, name
    archived = {}
    for record in report['archives'].values():
        manifest = read(record['manifest'])
        with tarfile.open(directory / record['archive']) as stream:
            members = stream.getmembers()
            assert len(members) == len(manifest) == record['files']
            assert sum(m.size for m in members) < 48 * 1024 * 1024
            assert {m.name for m in members} == set(manifest)
            for member in members:
                assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
                value = stream.extractfile(member).read()
                expected = manifest[member.name]
                assert len(value) == expected['bytes'] and hashlib.sha256(value).hexdigest() == expected['sha256']
                assert member.name not in archived
                archived[member.name] = value
    projection = json.loads(inputs.PROJECTION.read_text())
    binding = read('package/artifact-binding.json')
    assert binding['projectionSha256'] == digest(inputs.PROJECTION)
    assert hashlib.sha256(archived['consumer-build/InstalledConsumer']).hexdigest() == binding['consumerSha256']
    for name, checksum in binding['installedFiles'].items():
        assert hashlib.sha256(archived['install/' + name]).hexdigest() == checksum, name
    for name, checksum in binding['producerCriticalFiles'].items():
        assert digest(ROOT / name) == checksum, name
    corpus = inputs.rows(projection)
    comparisons = {r['fixture']: r for r in read('comparison/comparison.json')['results']}
    assert set(comparisons) == {r['path'] for r in corpus}
    totals = dict(exactMatches=0, pixelMatches=0, nativeFrameMatches=0, nativeLifecycleMatches=0, stateMatches=0)
    restore_matches = 0
    by_kind = {kind: dict(cases=0, exactMatches=0) for kind in ['closed', 'edge', 'history']}
    for expected in corpus:
        path = expected['path']
        actual = read('captures/' + path + '.json')
        observed = inputs.observations(expected, actual)
        result = comparisons[path]
        for key, value in observed.items():
            assert result[key] == value, (path, key)
        assert actual['reference'] == expected['reference'] and actual['source'] == inputs.REFERENCE
        assert actual['accepted'] is False and actual['nativeFrameMatches'] is (observed['nativeFrameStatus'] == 'passed')
        assert actual['nativeLifecycleMatches'] is (observed['nativeLifecycleStatus'] == 'passed')
        assert result['referenceSHA256'] == digest(ROOT / expected['reference'])
        assert result['candidateSHA256'] == digest(directory / 'captures' / path)
        with Image.open(ROOT / expected['reference']) as reference, Image.open(directory / 'captures' / path) as candidate:
            assert reference.size == candidate.size == (640 * expected['dpr'], 400 * expected['dpr'])
            difference = ImageChops.difference(reference.convert('RGBA'), candidate.convert('RGBA'))
            identical = all(extrema == (0, 0) for extrema in difference.getextrema())
        assert result['pixelStatus'] == ('passed' if identical else 'failed')
        exact = identical and all(observed[k] == 'passed' for k in ['nativeFrameStatus', 'nativeLifecycleStatus', 'stateStatus', 'retainedRasterStatus'])
        assert result['status'] == ('passed' if exact else 'failed')
        totals['exactMatches'] += exact
        totals['pixelMatches'] += identical
        for key, status in [('nativeFrameMatches', 'nativeFrameStatus'), ('nativeLifecycleMatches', 'nativeLifecycleStatus'), ('stateMatches', 'stateStatus')]:
            totals[key] += observed[status] == 'passed'
        restore_matches += expected['kind']=='history' and expected['step']=='restore' and observed['retainedRasterStatus']=='passed'
        by_kind[expected['kind']]['cases'] += 1
        by_kind[expected['kind']]['exactMatches'] += exact
    summary = report['strictComparison']
    assert summary['retainedRestorePixelMatches'] == restore_matches
    assert all(summary[k] == value for k, value in totals.items()) and summary['byKind'] == by_kind
    assert read('comparison/comparison.json')['summary'] == summary
    for context in inputs.CONTEXTS:
        name = inputs.prefix(*context)
        actual = read('captures/' + name + '.json')
        assert (actual['appearance'], actual['textScale'], actual['dpr']) == context
        assert actual['structuralChecks'] == 'passed' and actual['images'] == actual['geometryObservations'] == 201
        assert actual['pointerDeliveries'] == 12 and actual['accepted'] is False
        expected_sizing = [r for r in projection['sizing'] if (r['appearance'], r['textScale'], r['dpr']) == context]
        assert len(actual['sizing']) == len(expected_sizing) == 62
        for value, source in zip(actual['sizing'], expected_sizing):
            for key in ['configuration', 'public', 'witnesses']:
                assert value[key] == source[key]
            assert value['actual'] is None and value['status'].startswith('unobserved')
        fatal = read('captures/' + name + '-fatal-process.json')
        assert fatal['exitCode'] in [-6, 134] and 'minimumTileWidth -16' in (directory / 'captures' / fatal['log']).read_text()
    assert read('qt/full/result.json')['exitCode'] == 0
    assert '100% tests passed, 0 tests failed out of 33' in (directory / 'qt/full/run.log').read_text()
    assert read('runtime-proof/result.json')['exitCode'] == 0
    operator = read('operator/result.json')
    assert operator['status'] in ['passed', 'failed'] and operator['controls'] == 14 and len(operator['records']) == 24
    exact_states = sum(r['passed'] for r in operator['records'])
    assert operator['status'] == ('passed' if exact_states == 24 else 'failed')
    assert report['validation']['operatorExactStates'] == exact_states and operator['physicalDisplay'] is False
    assert sum(r['click'] is not None for r in operator['records']) == 23
    for record in operator['records']:
        reference = directory / 'operator' / record['reference']
        for attempt in record['attempts']:
            path = directory / 'operator' / attempt['path']
            assert digest(path) == attempt['sha256']
            with Image.open(path) as image, Image.open(reference) as expected:
                actual = image.convert('RGBA').crop((24, 200, 664, 600))
                identical = actual.tobytes() == expected.convert('RGBA').tobytes()
            assert attempt['exactViewportMatch'] is identical
        assert record['passed'] is record['attempts'][-1]['exactViewportMatch']
    replay = read('replay/source-overlays.json')
    base = read('replay/base-files.json')
    assert replay['baseRevision'] == base['baseRevision'] == report['baseRevision']
    tree = {}
    for row in subprocess.check_output(['git', 'ls-tree', '-rz', '--full-tree', report['baseRevision']], cwd=ROOT).split(b'\0'):
        if row:
            head, name = row.split(b'\t', 1)
            tree[name.decode()] = head.decode().split()[2]
    unique_base = {}
    for path, record in base['files'].items():
        assert tree[path] == record['gitObject']
        if record['gitObject'] in unique_base:
            assert unique_base[record['gitObject']] == record['sha256']
        unique_base[record['gitObject']] = record['sha256']
    objects = list(unique_base)
    payload = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT,
        input=('\n'.join(objects) + '\n').encode())
    offset = 0
    for object_id in objects:
        end = payload.index(b'\n', offset)
        actual_id, kind, size = payload[offset:end].decode().split()
        assert actual_id == object_id and kind == 'blob'
        size = int(size)
        data = payload[end + 1:end + 1 + size]
        assert hashlib.sha256(data).hexdigest() == unique_base[object_id]
        offset = end + size + 2
    assert offset == len(payload)
    for name, overlay in replay['attempts'].items():
        manifest = read('attempts/' + name + '/inputs.json')['sourceFiles']
        for path, checksum in manifest.items():
            if path in overlay:
                assert overlay[path] == checksum and hashlib.sha256(archived['blobs/' + checksum]).hexdigest() == checksum
            else:
                assert base['files'][path]['sha256'] == checksum
    for manifest in read('replay/package-inputs.json').values():
        for checksum in manifest.values():
            assert hashlib.sha256(archived['blobs/' + checksum]).hexdigest() == checksum
    for record in read('replay/diagnostic-outputs.json').values():
        location = record['location']
        value = (directory / location.removeprefix('candidate/')).read_bytes() if location.startswith('candidate/') else archived[location]
        assert hashlib.sha256(value).hexdigest() == record['sha256']
    print('MediaLibrary: 1608 strict pairs, eight fatal outcomes and all 7440 unobserved sizing queries retained; mirror acceptance pending')
    return report

if __name__ == '__main__':
    verify()
