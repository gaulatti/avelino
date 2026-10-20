from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PREVIOUS = P.parent / 'qt-software-final-image-v2'
DOCKER = ['docker', '--context', 'colima-avelino-verify']
steps = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (P / name).write_text(json.dumps(value, indent=2) + '\n')


def run(name, command):
    write('phase.json', dict(phase=name, startedAt=time.time()))
    started = time.monotonic()
    with (P / (name + '.log')).open('x') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    steps.append(dict(name=name, command=command, exitCode=result.returncode,
                      seconds=time.monotonic() - started))
    write('commands.json', steps)
    print(name, result.returncode, flush=True)
    assert result.returncode == 0, (name, result.returncode)


try:
    write('phase.json', dict(phase='waiting-for-existing-producer', startedAt=time.time()))
    while not (PREVIOUS / 'result.json').exists():
        time.sleep(10)
    previous = json.loads((PREVIOUS / 'result.json').read_text())
    commands = json.loads((PREVIOUS / 'commands.json').read_text())
    assert previous['exitCode'] == 1
    assert [(row['name'], row['exitCode']) for row in commands] == [
        ('toolchain-evidence', 0), ('linux-core-runtime', 0),
        ('independent-consumer-configure', 0), ('independent-consumer-build', 0),
        ('runtime-source-absence', 1)], commands
    assert 'AssertionError' in (PREVIOUS / 'runtime-source-absence.log').read_text()
    write('phase.json', dict(phase='waiting-for-existing-sdk-audit', startedAt=time.time()))
    while not (PREVIOUS / 'sdk-audit/result.json').exists():
        time.sleep(10)
    sdk = json.loads((PREVIOUS / 'sdk-audit/result.json').read_text())
    assert sdk['exitCode'] == 0 and sdk['actualImageInventoryAudited'] and not sdk['runtimeVerificationPassed']
    image = json.loads((PREVIOUS / 'image.json').read_text())
    image_id = image['imageId']; assert image_id == sdk['imageId']
    frozen = json.loads((PREVIOUS / 'inputs.json').read_text())
    assert all(sha(ROOT / name) == value for name, value in frozen['files'].items())
    write('inputs.json', frozen)
    write('image.json', image)
    receipt = json.loads((PREVIOUS / 'runtime-inputs.json').read_text())
    old_runtime = PREVIOUS / 'runtime'
    assert all(sha(old_runtime / name) == value for name, value in receipt['packageFiles'].items())
    runtime = P / 'runtime'
    shutil.copytree(old_runtime, runtime, symlinks=True)
    assert all(sha(runtime / name) == value for name, value in receipt['packageFiles'].items())
    assert sha(runtime / 'consumer-build/InstalledConsumer') == receipt['consumerSha256']
    write('runtime-inputs.json', dict(receipt, freshConsumerCompilationProducer=PREVIOUS.name,
        previousProducerFailure='Source-absence harness rejected the empty SDK /work directory',
        priorCommandsRetainedUnmodified=True))
    base = DOCKER + ['run', '--rm', '--ulimit', 'core=0', '-v', str(runtime) + ':/package',
                     '-w', '/package', image_id]
    check = '''from pathlib import Path
work = Path('/work')
assert not work.exists() or (work.is_dir() and not any(work.iterdir())), 'SDK workdir contains files'
paths = ['/work/src/Avelino', '/work/CMakeLists.txt', '/work/build',
         '/package/consumer', '/package/src', '/package/build',
         '/package/consumer-build/CMakeCache.txt', '/Users/gaulatti/source/gaulatti/avelino']
assert not any(Path(name).exists() for name in paths)
assert Path('/package/consumer-build/InstalledConsumer').is_file()
print('SDK workdir empty; library and consumer project sources and producer build trees absent')
'''
    run('runtime-source-absence', base + ['python3', '-c', check])
    run('installed-runtime-and-date', base + ['bash', 'check-runtime.sh'])
    run('general-display-sessions', base + ['bash', 'check-display-sessions.sh'])
    run('hero-display-sessions', base + ['bash', 'check-display-sessions-hero-carousel.sh',
                                      '/package/display-evidence/hero-carousel'])
    assert all(sha(ROOT / name) == value for name, value in frozen['files'].items())
    assert all(sha(runtime / name) == value for name, value in receipt['packageFiles'].items())
    write('result.json', dict(exitCode=0, imageId=image_id, completeLinuxDriver=True,
        completeLinuxDriverProducer=PREVIOUS.name, independentConsumerBuilt=True,
        independentConsumerCompilationProducer=PREVIOUS.name,
        libraryAndConsumerProjectSourcesAbsentAtRuntime=True,
        installedRuntimeDateAndGeneralDisplayPassed=True,
        emptySdkWorkdirAllowed=True, projectSourcePresenceStillRejected=True,
        previousHarnessFailureRetained=True, nativeAcceptance='pending', fullMirrorAccepted=False))
    write('sdk-audit-result.json', dict(sdk, runtimeVerificationPassed=True,
        runtimeVerificationProducer=P.name, immutableSdkAuditProducer=PREVIOUS.name,
        immutableSdkAuditResultSha256=sha(PREVIOUS / 'sdk-audit/result.json'),
        actualImageSdkInventorySha256=sha(PREVIOUS / 'sdk-audit/actual-image-sdk.json'),
        previousRuntimeFailure='Resolved empty-workdir assertion; original result retained',
        fullMirrorAccepted=False))
    write('phase.json', dict(phase='complete', finishedAt=time.time()))
except BaseException as error:
    write('result.json', dict(exitCode=1, error=repr(error), fullMirrorAccepted=False))
    raise
