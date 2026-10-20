#!/usr/bin/env python3
"""Verify the completed, historical normal Linux-driver receipt."""
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/qt-rectangle-linux-driver-20261020'
CHECKPOINT = '8213635e91c08dff9ed1cfca1bfa757fd0c94e64'
IMAGE = 'sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7'


def read(name):
    return json.loads((CAPSULE / name).read_text())


def blobs(expressions):
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=('\n'.join(expressions) + '\n').encode(), stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(result.stdout)
    for expression in expressions:
        header = stream.readline().split()
        assert len(header) == 3 and header[1] == b'blob', expression
        content = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        yield content
    assert not stream.read()


def verify():
    manifest = read('files.json')
    assert set(manifest) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    relative = CAPSULE.relative_to(ROOT)
    names = sorted({str(relative / n) for n in manifest} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names)
    for name, content in zip(names, blobs([':' + n for n in names]), strict=True):
        assert content == (ROOT / name).read_bytes()
        if name != str(relative / 'files.json'):
            assert hashlib.sha256(content).hexdigest() == manifest[str(Path(name).relative_to(relative))]
    inputs, environment, result = read('inputs.json'), read('environment.json'), read('result.json')
    assert inputs['imageId'] == result['imageId'] == IMAGE
    assert len(inputs['sourceFiles']) == 837 and environment['sourceInputs'] == inputs['sourceFiles']
    for (name, checksum), content in zip(inputs['sourceFiles'].items(), blobs([CHECKPOINT + ':' + n for n in inputs['sourceFiles']]), strict=True):
        assert hashlib.sha256(content).hexdigest() == checksum, name
    assert result['exitCode'] == 0
    for key in ['completeLinuxDriverExecuted', 'sourceInputsUnchanged', 'stalePackageRegenerated', 'chainedSdkProvenance']:
        assert result[key] is True
    for key in ['fullMirrorAccepted', 'nativeAcceptance', 'accepted']:
        assert result[key] is False
    stages = environment['qtSoftwareRendererStages']
    assert len(stages) == 2
    assert stages[1]['previousStage'] == 'qt-software-opacity'
    assert stages[1]['originalLibrarySha256'] == stages[0]['installedLibrarySha256']
    assert stages[1]['installedLibrarySha256'] == environment['qtQuickSha256']
    commands = read('commands.json')
    assert [r['label'] for r in commands] == ['retain-toolchain-stages', 'linux-driver']
    assert all(r['exitCode'] == 0 and IMAGE in r['command'] for r in commands)
    assert commands[1]['command'][-2:] == ['bash', 'scripts/check-linux.sh']
    assert '100% tests passed, 0 tests failed out of 55' in (CAPSULE / 'linux-driver.log').read_text()
    assert (CAPSULE / 'ctest.log').read_text().count('Test Passed.') == 55
    audit, scope = read('audit.json'), read('scope.json')
    assert audit['allFrozenFilesMatchGitCheckpoint'] == scope['frozenSourceCheckpoint'] == CHECKPOINT
    assert audit['frozenSourceFiles'] == scope['sourceInputCount'] == 837
    assert audit['allFrozenSourceBytesUnchanged'] and scope['completeNormalLinuxDriver']
    assert scope['reusedCoreBuild'] and scope['freshIndependentConsumerBuild']
    assert scope['newAdminShellIncluded'] is scope['expectedImagesChanged'] is scope['accepted'] is False
    outputs = read('retained-output-manifest.json')
    assert len(outputs) == scope['outputMembers'] == 49164 and scope['manifestOnlyForOutputs']
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in outputs)
    assert all(r['kind'] in ['file', 'symlink'] for r in outputs.values())
    print('Completed historical Linux driver: 837 pinned inputs, 55 test groups, fresh consumer, chained SDK and 49164 retained output members; parity pending')


if __name__ == '__main__':
    verify()
