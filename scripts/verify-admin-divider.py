#!/usr/bin/env python3
"""Verify the interpreted divider checkpoint without accepting native raster parity."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/admin-divider-20261020'


def read(name):
    return json.loads((CAPSULE / name).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify():
    files = read('files.json')
    assert set(files) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    relative = CAPSULE.relative_to(ROOT)
    names = sorted({str(relative / n) for n in files} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names), 'Every divider checkpoint member must be in the Git index'
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=('\n'.join(':' + n for n in names) + '\n').encode(), stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(result.stdout)
    for name in names:
        header = stream.readline().split(); assert len(header) == 3 and header[1] == b'blob'
        raw = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        assert raw == (ROOT / name).read_bytes()
        if name != str(relative / 'files.json'):
            assert sha(raw) == files[str(Path(name).relative_to(relative))]
    assert not stream.read()
    scope = read('scope.json')
    assert scope['publicDividerImplemented'] and scope['sourceUncommittedAtCapture']
    assert scope['currentAttempts'] == [4, 5] and scope['scaleFactors'] == [1, 2]
    assert scope['qtTestsPerContext'] == 264 and scope['newNativeDividerCases'] == 4
    for key in ['freshModuleCompilation', 'newInstalledConsumerExecuted', 'sourceDpr1RasterAccepted',
                'nativeRasterAccepted', 'physicalInput', 'readerAcceptance', 'accepted']:
        assert scope[key] is False
    failure = read('runtime/controller-failure-v1.json')
    assert failure['errorType'] == 'KeyError' and not failure['runtimeStarted']
    assert failure['sourceSha256'] == sha((CAPSULE / 'runtime/controller-v1-failed.py').read_bytes())
    for attempt, expected_exit in [(2, 1), (3, 2), (4, 0), (5, 0)]:
        receipt = read(f'runtime/run-v{attempt}.json')
        assert receipt['exitCode'] == expected_exit and receipt['freshCompilation'] is receipt['accepted'] is False
        original = {name: (CAPSULE / f'runtime/inputs-v{attempt}' / name).read_bytes() for name in receipt['sourceInputHashes']}
        assert {n: sha(b) for n, b in original.items()} == receipt['sourceInputHashes']
        payload = dict(original)
        payload['tests/components/witnesses.js'] = b'var data = ' + original['tests/consumer/native-admin-shell-witnesses.json'] + b';\n'
        name = 'tests/components/tst_admin_shell.qml'
        text = payload[name].decode().replace('import QtTest', 'import QtTest\nimport "witnesses.js" as Native', 1)
        payload[name] = text.replace('    id: root', '    id: root\n    property var nativeAdminShellWitnesses: Native.data', 1).encode()
        assert {n: sha(b) for n, b in payload.items()} == receipt['executedPayloadHashes']
        log = (CAPSULE / f'runtime/run-v{attempt}.log').read_text()
        if attempt == 2:
            assert 'Read-only file system' in log and 'Start testing' not in log
        elif attempt == 3:
            assert '262 passed, 2 failed' in log and 'NaN' in log
        else:
            assert '264 passed, 0 failed' in log
            assert 'QT_SCALE_FACTOR=' + str(attempt - 3) in receipt['command']
            evolved = {'src/Avelino/BleeckerAdminShell.qml', 'tests/components/tst_admin_shell.qml'}
            for name, raw in original.items():
                if name in evolved:
                    historical = subprocess.check_output([
                        'git', 'show', '166ac74ccf442e45ac111cbe134ad0022f13a2ba:' + name], cwd=ROOT)
                    assert historical == raw
                else:
                    assert (ROOT / name).read_bytes() == raw
    base = read('base-module.json')
    assert base['moduleReused'] and base['newQmlInterpreted'] and base['accepted'] is False
    published_inputs = json.loads((ROOT / 'evidence/development/admin-shell-sessions-20261020/inputs.json').read_text())
    assert base['sha256'] == published_inputs['librarySha256']
    images = read('images.json'); assert len(images) == 4
    render = read('render-check.json')
    assert render['onePhysicalColumnChanged'] and render['adjacentColumnsUnchanged']
    assert render['nativePixelEquivalence'] is render['accepted'] is False
    for name, row in images.items():
        raw = (CAPSULE / row['stored']).read_bytes()
        assert sha(raw) == row['sha256'] == Path(row['stored']).stem and len(raw) == row['bytes']
        phase, theme = Path(name).parts
        check = next(r for r in render['checks'] if r['phase'] == phase and r['theme'] == Path(theme).stem)
        with Image.open(io.BytesIO(raw)) as image:
            image.load(); assert image.size == (check['width'], check['height']) == (1680, 1000)
            assert [list(image.convert('RGBA').getpixel((p['x'], p['y']))) for p in check['pixels']] == [p['rgba'] for p in check['pixels']]
    for theme in ['light', 'dark']:
        before = Image.open(CAPSULE / images[f'before/{theme}.png']['stored']).convert('RGB')
        after = Image.open(CAPSULE / images[f'after/{theme}.png']['stored']).convert('RGB')
        assert ImageChops.difference(before, after).getbbox() == (599, 0, 600, 1000)
    comparator = read('render-check/comparator-source.json')
    historical = subprocess.check_output(['git', 'show', comparator['sourceRevision'] + ':' + comparator['path']], cwd=ROOT)
    assert sha(historical) == comparator['sha256'] == sha((ROOT / comparator['path']).read_bytes())
    assert comparator['iccReviewGateChanged'] is comparator['accepted'] is False
    for version in [1, 2]:
        inputs = read(f'render-check/v{version}/inputs.json')
        for name, checksum in inputs['files'].items():
            assert sha((CAPSULE / f'render-check/v{version}/recipe' / name).read_bytes()) == checksum
        execution = read(f'render-check/v{version}/result.json')
        assert execution['exitCode'] == 0 and execution['freshModuleCompilation'] is execution['accepted'] is False
        for kind in ['raw', 'matched']:
            report = read(f'render-check/v{version}/canonical-{kind}/comparison.json')
            assert report['status'] == 'failed' and len(report['results']) == 80
            assert all(r['error'] == 'ICC-managed captures require an explicitly reviewed color-space conversion'
                       and r['status'] == 'failed' for r in report['results'])
    print('Admin divider: 264 tests at DPR 1 and 2; visible one-column render verified; new compilation, ICC review and native raster acceptance pending')


if __name__ == '__main__':
    verify()
