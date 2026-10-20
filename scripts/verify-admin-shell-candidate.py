#!/usr/bin/env python3
"""Verify the public QML candidate checkpoint without accepting package parity."""
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/admin-shell-20261020'


def read(name):
    return json.loads((CAPSULE / name).read_text())


def sha(content):
    return hashlib.sha256(content).hexdigest()


def git_bytes(expressions):
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=('\n'.join(expressions) + '\n').encode(), stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(result.stdout)
    for expression in expressions:
        header = stream.readline().split()
        assert len(header) == 3 and header[1] == b'blob', expression
        content = stream.read(int(header[2]))
        assert stream.read(1) == b'\n'
        yield content
    assert not stream.read()


def verify():
    manifest = read('files.json')
    actual = {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    assert set(manifest) == actual
    relative = CAPSULE.relative_to(ROOT)
    names = sorted({str(relative / n) for n in manifest} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names), 'Every candidate capsule member must be in the Git index'
    for name, content in zip(names, git_bytes([':' + n for n in names]), strict=True):
        assert content == (ROOT / name).read_bytes(), name
        if name != str(relative / 'files.json'):
            assert sha(content) == manifest[str(Path(name).relative_to(relative))], name
    result = read('result.json')
    assert result['publicType'] == 'BleeckerAdminShell'
    assert result['sourceReference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert (result['sourceStaticProfiles'], result['nativeOwnerHistoryStates'], result['nativeFreshDividerCases']) == (80, 160, 168)
    for key in ['freshCompilation', 'installedConsumerExecuted', 'candidatePixelsCompared',
                'nativeToolbarEquivalentVerified', 'physicalInput', 'readerAcceptance', 'accepted',
                'sourcePinsChanged', 'existingExpectedImagesChanged']:
        assert result[key] is False
    for key in ['toolbarPointer', 'callerControlsRetained', 'disabledInputVerified', 'qtKeyboardVerified',
                'qtShortcutVerified', 'windowHostAndResizeVerified']:
        assert result[key] is True
    assert result['qtTestCasesPerCurrentContext'] == 260
    assert result['currentContexts'] == [dict(attempt=6, platform='wayland', scale=2),
                                         dict(attempt=7, platform='offscreen', scale=1),
                                         dict(attempt=8, platform='xcb', scale=1),
                                         dict(attempt=9, platform='offscreen', scale=2)]
    current = {row['attempt'] for row in result['currentContexts']}
    # These files gained a later visible-divider implementation and native
    # divider cases. The initial receipt still proves its recorded producer.
    evolved = {'src/Avelino/BleeckerAdminShell.qml', 'tests/components/tst_admin_shell.qml',
               'tests/consumer/AdminShellCase.qml'}
    historical = dict(zip(sorted(evolved), git_bytes([result['sourceCheckpoint'] + ':' + n for n in sorted(evolved)]), strict=True))
    for attempt in range(1, 10):
        receipt = read(f'run-v{attempt}.json')
        assert receipt['exitCode'] == (1 if attempt == 2 else 0)
        assert receipt['freshCompilation'] is receipt['accepted'] is False
        assert 'QT_QUICK_BACKEND=software' in receipt['command']
        assert 'sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7' in receipt['command']
        original = {n: (CAPSULE / f'inputs-v{attempt}' / n).read_bytes() for n in receipt['sourceInputHashes']}
        assert {n: sha(b) for n, b in original.items()} == receipt['sourceInputHashes']
        payload = dict(original)
        payload['tests/components/witnesses.js'] = b'var data = ' + original['tests/consumer/native-admin-shell-witnesses.json'] + b';\n'
        name = 'tests/components/tst_admin_shell.qml'
        text = payload[name].decode().replace('import QtTest', 'import QtTest\nimport "witnesses.js" as Native', 1)
        text = text.replace('    id: root', '    id: root\n    property var nativeAdminShellWitnesses: Native.data', 1)
        payload[name] = text.encode()
        assert {n: sha(b) for n, b in payload.items()} == receipt['executedPayloadHashes']
        log = (CAPSULE / f'run-v{attempt}.log').read_text()
        assert 'Qt 6.8.3 (arm64-little_endian-lp64' in log
        if attempt == 2:
            assert '258 passed, 1 failed' in log and 'test_toolbar_keyboard_and_shortcut' in log
        else:
            count = 258 if attempt == 1 else 260
            assert f'Totals: {count} passed, 0 failed' in log
        if attempt in current:
            row = next(r for r in result['currentContexts'] if r['attempt'] == attempt)
            assert 'QT_QPA_PLATFORM=' + row['platform'] in receipt['command']
            assert 'QT_SCALE_FACTOR=' + str(row['scale']) in receipt['command']
            assert all((historical[n] if n in evolved else (ROOT / n).read_bytes()) == b for n, b in original.items())
    inheritance = read('runtime-inheritance.json')
    assert inheritance['sourceCppModuleReused'] and inheritance['qmlInterpreted']
    assert inheritance['freshCompilation'] is inheritance['installedConsumerExecuted'] is False
    assert inheritance['baseLinuxDriverCompleteAtCapture'] is inheritance['accepted'] is False
    assert inheritance['imageId'] == 'sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7'
    base = inheritance['unchangedBaseModuleSources']
    assert all(n.startswith('src/') and n != 'src/Avelino/CMakeLists.txt' for n in base)
    base_revision = inheritance['baseModuleSourceCheckpoint']
    for (name, checksum), content in zip(base.items(), git_bytes([base_revision + ':' + n for n in base]), strict=True):
        assert sha(content) == checksum, name
    producer = result['sourceCheckpoint']
    inputs = read('implementation-inputs.json')
    for (name, checksum), content in zip(inputs.items(), git_bytes([producer + ':' + n for n in inputs]), strict=True):
        assert sha(content) == checksum, name
    return result


if __name__ == '__main__':
    summary = verify()
    print('AdminShell public QML: 260 tests in four captured contexts; fresh build, package, raster and physical acceptance pending')
