from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
IMAGE_PRODUCER = P.parent / 'qt-software-toolchain-build-v4'
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
    files = [ROOT / 'CMakeLists.txt', ROOT / 'CMakePresets.json']
    for folder in ['src', 'samples', 'assets', 'tokens', 'tests', 'scripts',
                   'cmake', 'tools', 'evidence/geometry']:
        files.extend(p for p in (ROOT / folder).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts)
    frozen = {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}
    write('inputs.json', dict(files=frozen, sourceRevision=subprocess.check_output(
        ['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        fullMirrorAccepted=False))
    write('phase.json', dict(phase='waiting-for-candidate-image', startedAt=time.time()))
    while not (IMAGE_PRODUCER / 'result.json').exists():
        time.sleep(10)
    image = json.loads((IMAGE_PRODUCER / 'result.json').read_text())
    assert image['exitCode'] == 0 and image['sourcePatchValidated'], image
    image_id = subprocess.check_output(DOCKER + ['image', 'inspect', '--format',
                                               '{{.Id}}', image['image']], text=True).strip()
    assert image_id == image['imageId']
    assert all(sha(ROOT / name) == value for name, value in frozen.items())
    write('image.json', image)
    output = P / 'output'
    (output / 'build').mkdir(parents=True)
    (output / 'artifacts').mkdir()
    artifact_prefix = '/work/artifacts'
    run('toolchain-evidence', DOCKER + ['run', '--rm', '-v',
        str(output / 'artifacts') + ':/evidence', image_id, 'bash', '-euc',
        'mkdir -p /evidence/linux/toolchain\n'
        'cp -R /opt/qt/share/avelino/qt-software-opacity /evidence/linux/toolchain/'])
    stale = output / 'artifacts/package'
    (stale / 'consumer').mkdir(parents=True)
    (stale / 'install').mkdir()
    (stale / 'consumer/main.cpp').write_text('obsolete consumer fixture\n')
    (stale / 'install/obsolete-fixture').touch()
    run('linux-core-runtime', DOCKER + ['run', '--rm', '--ulimit', 'core=0',
        '-e', 'GIT_OPTIONAL_LOCKS=0', '-v', str(ROOT) + ':/work:ro',
        '-v', str(output / 'build') + ':/work/build',
        '-v', str(output / 'artifacts') + ':' + artifact_prefix,
        '-w', '/work', image_id, 'bash', 'scripts/check-linux.sh'])
    package = output / 'artifacts/package'
    for name in ['main.cpp', 'Main.qml']:
        assert (ROOT / 'tests/consumer' / name).read_bytes() == (package / 'consumer' / name).read_bytes()
    assert not (package / 'install/obsolete-fixture').exists()
    assert not (package / 'consumer/consumer').exists()
    environment = json.loads((output / 'artifacts/linux/environment.json').read_text())
    assert environment['qtQuickSha256'] == environment['qtSoftwareRenderer']['installedLibrarySha256']
    package_base = DOCKER + ['run', '--rm', '--ulimit', 'core=0',
                            '-v', str(package) + ':/package', '-w', '/package', image_id]
    run('independent-consumer-configure', package_base + ['cmake', '-S', 'consumer',
        '-B', 'consumer-build', '-G', 'Ninja', '-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'])
    run('independent-consumer-build', package_base + ['cmake', '--build', 'consumer-build', '--parallel', '2'])
    runtime = P / 'runtime'
    runtime.mkdir()
    shutil.copytree(package / 'install', runtime / 'install')
    (runtime / 'consumer-build').mkdir()
    shutil.copy2(package / 'consumer-build/InstalledConsumer', runtime / 'consumer-build/InstalledConsumer')
    for name in ['environment.json', 'check-installed-catalog.sh',
                 'check-installed-date-range-catalog.sh', 'check-display-sessions-date-range.sh',
                 'check-display-sessions.sh', 'check-display-sessions-hero-carousel.sh']:
        shutil.copy2(package / name, runtime / name)
    original = (package / 'check-installed.sh').read_text().splitlines(keepends=True)
    build_lines = [line for line in original if line.startswith('cmake ')]
    assert len(build_lines) == 2
    assert build_lines[0].startswith('cmake -S consumer -B consumer-build ')
    assert build_lines[1] == 'cmake --build consumer-build --parallel 2\n'
    (runtime / 'check-runtime.sh').write_text(''.join(line for line in original if line not in build_lines))
    write('runtime-inputs.json', dict(consumerSha256=sha(runtime / 'consumer-build/InstalledConsumer'),
        originalInstalledDriverSha256=sha(package / 'check-installed.sh'),
        runtimeDriverSha256=sha(runtime / 'check-runtime.sh'),
        excludedDriverLines=build_lines, rationale='Fresh consumer build completed in separate package mount; runtime receives installed prefix and ELF only.',
        packageFiles={str(p.relative_to(runtime)): sha(p) for p in sorted(runtime.rglob('*')) if p.is_file()},
        fullMirrorAccepted=False))
    runtime_base = DOCKER + ['run', '--rm', '--ulimit', 'core=0',
                            '-v', str(runtime) + ':/package', '-w', '/package', image_id]
    run('runtime-source-absence', runtime_base + ['python3', '-c',
        'from pathlib import Path; '
        'assert not any(Path(p).exists() for p in ["/work", "/package/consumer", '
        '"/package/src", "/package/build", "/package/consumer-build/CMakeCache.txt", '
        '"/Users/gaulatti/source/gaulatti/avelino"]); '
        'assert Path("/package/consumer-build/InstalledConsumer").is_file(); '
        'print("Library and consumer project sources and producer builds absent")'])
    run('installed-runtime-and-date', runtime_base + ['bash', 'check-runtime.sh'])
    run('general-display-sessions', runtime_base + ['bash', 'check-display-sessions.sh'])
    run('hero-display-sessions', runtime_base + ['bash', 'check-display-sessions-hero-carousel.sh',
                                              '/package/display-evidence/hero-carousel'])
    assert all(sha(ROOT / name) == value for name, value in frozen.items())
    write('result.json', dict(exitCode=0, imageId=image_id, completeLinuxDriver=True,
        independentConsumerBuilt=True, libraryAndConsumerProjectSourcesAbsentAtRuntime=True,
        installedRuntimeDateAndGeneralDisplayPassed=True, fullMirrorAccepted=False,
        nativeAcceptance='pending'))
    write('phase.json', dict(phase='complete', finishedAt=time.time()))
except BaseException as error:
    write('result.json', dict(exitCode=1, error=repr(error), fullMirrorAccepted=False))
    raise
