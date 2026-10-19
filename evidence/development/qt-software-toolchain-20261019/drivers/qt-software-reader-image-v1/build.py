from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time

P = Path(__file__).resolve().parent
BASE = P.parent
DOCKER = ['docker', '--context', 'colima-avelino-verify']
TAG = 'avelino-toolchain:qt-software-opacity-reader-v1-20261019-qt6.8.3'


def write(name, value):
    (P / name).write_text(json.dumps(value, indent=2) + '\n')


try:
    write('phase.json', dict(phase='waiting-for-complete-toolchain-and-date-verification', startedAt=time.time()))
    while not (BASE / 'qt-software-date-replay-v1/result.json').exists():
        time.sleep(10)
    verification = json.loads((BASE / 'qt-software-date-replay-v1/result.json').read_text())
    assert verification['exitCode'] == 0 and verification['coldByteIdentical'] == 437
    image = json.loads((BASE / 'qt-software-toolchain-build-v4/result.json').read_text())
    assert image['exitCode'] == 0 and image['imageId'] == verification['imageId']
    actual = subprocess.check_output(DOCKER + ['image', 'inspect', '--format', '{{.Id}}', image['image']], text=True).strip()
    assert actual == image['imageId']
    assert shutil.disk_usage(P).free >= 6 * 1024**3
    expected = (BASE / 'file-input-go-to-reader-v14/package-versions.txt').read_text()
    write('inputs.json', dict(baseImage=image, readerPackageVersions=expected,
        dockerfileSha256=hashlib.sha256((P / 'Dockerfile').read_bytes()).hexdigest(),
        existingReaderProducer='file-input-go-to-reader-v14', physicalListeningAccepted=False))
    write('phase.json', dict(phase='building-reader-addon', startedAt=time.time()))
    command = DOCKER + ['build', '--progress=plain', '--tag', TAG, '-f', str(P / 'Dockerfile'), str(P)]
    started = time.monotonic()
    with (P / 'build.log').open('x') as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT)
    write('command.json', dict(command=command, exitCode=result.returncode, seconds=time.monotonic()-started))
    assert result.returncode == 0
    image_id = subprocess.check_output(DOCKER + ['image', 'inspect', '--format', '{{.Id}}', TAG], text=True).strip()
    packages = ['at-spi2-core', 'orca', 'python3-pyatspi', 'speech-dispatcher', 'speech-dispatcher-espeak-ng']
    versions = subprocess.check_output(DOCKER + ['run', '--rm', image_id, 'dpkg-query', '-W', *packages], text=True)
    (P / 'package-versions.txt').write_text(versions)
    assert versions == expected
    code = '''from pathlib import Path
import hashlib,json,os
p=Path('/opt/qt');metadata=p/'share/avelino/qt-software-opacity';result={}
for f in sorted(p.rglob('*')):
 if metadata in f.parents:continue
 name=str(f.relative_to(p))
 if f.is_symlink():result[name]=dict(type='symlink',target=os.readlink(f))
 elif f.is_file():result[name]=dict(type='file',bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest())
print(json.dumps(result,indent=2))
'''
    with (P / 'actual-sdk.json').open('x') as output:
        subprocess.run(DOCKER + ['run', '--rm', image_id, 'python3', '-c', code], stdout=output, check=True)
    before = json.loads((BASE / 'qt-software-final-image-v2/early-sdk-inventory.json').read_text())['after']
    after = json.loads((P / 'actual-sdk.json').read_text())
    assert before == after
    write('result.json', dict(exitCode=0, image=TAG, imageId=image_id, baseImageId=image['imageId'],
        qtSdkEntriesUnchanged=len(after), readerVersionsMatchRecordedProducer=True,
        readerFlowsExecuted=False, physicalListeningAccepted=False, fullMirrorAccepted=False))
    write('phase.json', dict(phase='complete', finishedAt=time.time()))
    print('Reader addon built with recorded versions; Qt SDK unchanged', image_id, flush=True)
except BaseException as error:
    write('result.json', dict(exitCode=1, error=repr(error), fullMirrorAccepted=False))
    raise
