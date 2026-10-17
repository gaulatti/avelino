#!/usr/bin/env python3
"""Recompute the Linux dropdown evidence without approving native parity."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tarfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/dropdown-menu-20261017'
GATES = ['nativeFontsSymbolsRaster', 'nativeLabelBuilderTiming', 'nativeItemIdentityUpdates',
    'nativeSizing', 'nativePopupPresentationPlacementShadow', 'nativeInputTiming',
    'nativeAccessibility', 'physicalInputDisplay', 'readers', 'independentMachineReplay']


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


capture = module('dropdown_capture', 'scripts/capture-dropdown-menu.py')
boundary = module('dropdown_boundary', 'scripts/check-linux-boundary.py')
digest = lambda data: hashlib.sha256(data).hexdigest()


def validate_report(report):
    assert report['reference'] == capture.REFERENCE
    assert report['baseRevision'] == '021b5ef30624de60f49767baad32e4fa8a95082f'
    assert report['status'] == 'verification-pending' and report['accepted'] is False
    assert report['expectedImagesChanged'] is False and report['tolerance'] == 'none'
    assert report['approvedExceptions'] == [] and report['remainingAcceptance'] == GATES
    assert report['strictComparison']['accepted'] is False and report['strictComparison']['cases'] == 256
    assert report['validation'] == dict(qtTargets=41, focusedDpr1=16, focusedDpr2=16,
        malformedInputs=9, isolatedCatalogDefinitions=32, malformedCatalogDefinitions=19,
        independentModes=37, installedCatalogs=151, unchangedPriorCatalogs=147,
        nativePairs=256, virtualProfiles=8, operatorControls=15,
        operatorExactCallerStates=24, operatorOwnerScreenshots=3,
        physicalDisplay=False, hardwareAcceleration=False)


def verify(directory=DIRECTORY):
    read = lambda name: json.loads((directory / name).read_text())
    report = read('report.json')
    validate_report(report)
    files = read('files.json')
    assert set(files) == {str(f.relative_to(directory)) for f in directory.rglob('*')
        if f.is_file() and f.name != 'files.json'}
    for name, record in files.items():
        data = (directory / name).read_bytes()
        assert len(data) == record['bytes'] and digest(data) == record['sha256'], name
    archived = {}

    def unpack(record, parent):
        path = directory / parent / record['archive']
        assert digest(path.read_bytes()) == record['sha256']
        manifest = read(str(Path(parent) / record['manifest']))
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
    for record in report['archives'].values():
        unpack(record, '')
    replay = read('replay/source-replay.json')
    assert replay['baseRevision'] == report['baseRevision'] and replay['accepted'] is False
    assert replay['buildCacheInputs'] is False and len(replay['snapshots']) == 12
    for record in replay['archives'].values():
        unpack(record, 'replay')
    objects = replay['objects']
    tree = {row.split(b'\t', 1)[1].decode(): row.split(b'\t', 1)[0].split()[2].decode()
        for row in subprocess.check_output(['git', 'ls-tree', '-rz', '--full-tree', replay['baseRevision']], cwd=ROOT).split(b'\0') if row}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for sha, record in objects.items():
            if 'gitBlob' in record:
                assert not boundary.forbidden_path(record['sourcePath'])
                assert tree[record['sourcePath']] == record['gitBlob']
                process.stdin.write((record['gitBlob'] + '\n').encode()); process.stdin.flush()
                header = process.stdout.readline().split(); assert header[0].decode() == record['gitBlob'] and header[1] == b'blob'
                data = process.stdout.read(int(header[2])); assert process.stdout.read(1) == b'\n'
            else:
                data = archived[record['archivePath']]
            assert len(data) == record['bytes'] and digest(data) == sha
        process.stdin.close(); assert process.wait() == 0
    snapshots = {}
    for name, record in replay['snapshots'].items():
        path = 'replay/' + record['manifest']
        assert digest((directory / path).read_bytes()) == record['sha256']
        snapshot = read(path); assert len(snapshot) == record['files']
        assert all(not boundary.forbidden_path(name) and value['sha256'] in objects
            and value['bytes'] == objects[value['sha256']]['bytes'] for name, value in snapshot.items())
        snapshots[name] = snapshot
    binding = read('package/artifact-binding.json')
    for name, sha in binding['installedFiles'].items():
        assert digest(archived['install/' + name]) == sha
    assert digest(archived['consumer-build/InstalledConsumer']) == binding['consumerSha256']
    assert binding['consumerFiles'] == {name: row['sha256'] for name, row in snapshots['dropdown-menu-package-pilot-v5'].items()}
    producer = snapshots['dropdown-menu-build-v8']
    assert binding['producerCompiledFiles'] == {name: row['sha256'] for name, row in producer.items()
        if name.startswith(('src/', 'samples/', 'assets/', 'cmake/')) or name == 'CMakeLists.txt'}
    before = snapshots['dropdown-menu-build-v7']
    changed = {name for name in binding['producerCompiledFiles'] if producer[name]['sha256'] != before[name]['sha256']}
    assert changed == {'src/Avelino/BleeckerDropdownMenu.qml'}
    assert read('attempts/dropdown-menu-qt-v2/result.json')['exitCode'] == 0
    assert read('attempts/dropdown-menu-qt-v3/result.json')['exitCode'] == 0
    expected = capture.rows()
    comparison = read('comparison/observations.json')
    assert {key: value for key, value in comparison.items() if key != 'witnesses'} == report['strictComparison']
    pixels = frames = states = body = 0
    witnesses = {row['path']: row for row in comparison['witnesses']}
    assert set(witnesses) == {row['path'] for row in expected}
    for row in expected:
        path = directory / 'captures' / row['path']
        actual = json.loads(Path(str(path) + '.json').read_text())
        observation = capture.observations(row, actual)
        assert witnesses[row['path']] == dict(path=row['path'], reference=row['reference'], **observation)
        frames += observation['nativeFrameStatus'] == 'passed'
        body += observation['bodyCallerFrameStatus'] == 'passed'
        states += observation['stateStatus'] == 'passed'
        with Image.open(ROOT / row['reference']) as reference, Image.open(path) as candidate:
            pixels += reference.size == candidate.size and reference.convert('RGBA').tobytes() == candidate.convert('RGBA').tobytes()
    assert (pixels, frames, states, body) == tuple(comparison[key] for key in ['exactPixels', 'frames', 'states', 'bodyCallerFrames'])
    regression = read('regression/catalogs.json')
    assert regression['status'] == 'passed' and len(regression['records']) == 147
    for row in regression['records']:
        path = directory / 'catalogs' / row['path']
        assert digest(path.read_bytes()) == row['sha256']
        assert digest(Path(str(path) + '.json').read_bytes()) == row['metadataSha256']
        assert path.read_bytes() == (ROOT / regression['baseline'] / row['path']).read_bytes()
    profiles = sorted((directory / 'runtime').glob('dropdown-menu-*.json'))
    assert len(profiles) == 8
    for path in profiles:
        profile = json.loads(path.read_text())
        assert profile['accepted'] is False and profile['structuralChecks'] == 'passed'
        assert len(profile['closed']) == len(profile['sizing']) == profile['images'] == 32
        assert profile['pointerDeliveries'] == 11 and profile['keyDeliveries'] == 1 and len(profile['actions']) == 6
        assert all(row['state']['popupVisible'] is False for row in profile['actions'])
        assert [item['name'] for item in profile['qtMenuAccessibility']] == ['Open', 'Duplicate', 'Remove']
        assert all(profile[key] == 'pending' for key in ['nativeRasterAcceptance', 'physicalInputAcceptance', 'readerAcceptance'])
    operator = read('operator/result.json')
    assert operator['status'] == 'passed' and operator['controls'] == 15 and operator['phases'] == 27
    assert all(row['passed'] for row in operator['records'])
    assert len(read('operator/visual-review.json')['records']) == 3
    print(f'Dropdown candidate: {pixels}/256 pixels, {frames}/256 complete frames, {states}/256 states; native acceptance pending')


if __name__ == '__main__':
    verify()
