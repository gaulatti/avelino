from pathlib import Path
import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import time

from PIL import Image, ImageChops

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
ORIGINAL = Path('/Users/gaulatti/source/gaulatti/avelino')
BASE = ORIGINAL / 'artifacts/resumed-avelino-20261016'
PRODUCER = BASE / 'qt-software-final-image-v2'
PREDECESSOR = BASE / 'qt-software-reader-replay-v1'
SOURCE = ROOT / 'evidence/reference-investigations/footer-slots-20261019'
IMAGE = 'sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'
DOCKER = ['docker', '--context', 'colima-avelino-verify']
OUTPUT = P.parent / 'footer-compiled-v1/output'
PACKAGE = OUTPUT / 'package'
RUNTIME = P / 'runtime'
commands = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (P / name).write_text(json.dumps(value, indent=2) + '\n')


def run(name, command):
    write('phase.json', dict(phase=name, startedAt=time.time()))
    started = time.monotonic()
    with (P / (name + '.log')).open('x') as output:
        completed = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT)
    commands.append(dict(name=name, command=command, exitCode=completed.returncode,
                         seconds=time.monotonic() - started))
    write('commands.json', commands)
    print(name, completed.returncode, flush=True)
    assert completed.returncode == 0, (name, completed.returncode)


def clone_tree(source, target):
    clone = ctypes.CDLL(None, use_errno=True).clonefile
    clone.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    count = size = 0
    target.mkdir()
    for parent, directories, filenames in os.walk(source, followlinks=False):
        relative = Path(parent).relative_to(source)
        for name in directories[:]:
            src, dst = Path(parent) / name, target / relative / name
            if src.is_symlink():
                dst.symlink_to(os.readlink(src)); directories.remove(name)
            else:
                dst.mkdir()
        for name in filenames:
            src, dst = Path(parent) / name, target / relative / name
            if src.is_symlink():
                dst.symlink_to(os.readlink(src))
            else:
                if clone(os.fsencode(src), os.fsencode(dst), 0):
                    error = ctypes.get_errno()
                    raise OSError(error, os.strerror(error), str(src))
                count += 1; size += src.stat().st_size
    return dict(method='APFS clonefile; no original build mutations', files=count, logicalBytes=size)


try:
    original = P.parent / 'footer-compiled-v1'
    initial = json.loads((original / 'inputs.json').read_text())
    frozen = initial['sourceFiles']
    previous_failure = json.loads((original / 'result.json').read_text())
    assert previous_failure['exitCode'] == 1 and "candidate-configure" in previous_failure['error']
    assert "read-only file system" in (original / 'candidate-configure.log').read_text()
    assert all(sha(ROOT / name) == digest for name, digest in frozen.items())
    for name in ['qt-software-final-image-v3', 'qt-software-date-replay-v1', 'qt-software-reader-image-v1', 'qt-software-reader-replay-v1']:
        result = json.loads((BASE / name / 'result.json').read_text())
        assert result['exitCode'] == 0, (name, result)
    assert not (ROOT / 'build').exists()
    (ROOT / 'build').mkdir()
    write('inputs.json', dict(initial, continuationDriverSha256=sha(P / 'run.py'),
        sourceEvidenceCommit='fe396c27f0d9aaf22fd6c8bf36380500db3f026a',
        previousProducer=str(original), previousFailure=previous_failure,
        originalCandidateFilesUnchanged=True,
        mountRepair='Created the ignored empty /work/build mountpoint before binding the preserved COW build into the read-only source mount'))
    write('build-reuse.json', dict(json.loads((original / 'build-reuse.json').read_text()),
        reusedExistingClone=True, previousConfigureNeverStarted=True))
    compile_base = DOCKER + ['run', '--rm', '--ulimit', 'core=0',
        '-v', str(ROOT) + ':/work:ro', '-v', str(OUTPUT / 'build') + ':/work/build',
        '-v', str(PACKAGE) + ':/package', '-w', '/work', IMAGE]
    run('candidate-configure', compile_base + ['cmake', '-S', '/work', '-B', '/work/build/linux',
        '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=RelWithDebInfo', '-DBUILD_TESTING=ON'])
    run('candidate-target-build', compile_base + ['cmake', '--build', '/work/build/linux',
        '--parallel', '2', '--target', 'AvelinoComponentTests', 'AvelinoCatalog'])
    for dpr in [1, 2]:
        for suite in ['footer', 'composition']:
            run(suite + '-dpr' + str(dpr), compile_base + ['env', 'QT_QPA_PLATFORM=offscreen',
                'QT_QUICK_BACKEND=software', 'QT_SCALE_FACTOR=' + str(dpr),
                '/work/build/linux/tests/components/AvelinoComponentTests',
                '-input', '/work/tests/components/tst_' + suite + '.qml',
                '-import', '/work/build/linux/qml'])
    run('candidate-install', compile_base + ['cmake', '--install', '/work/build/linux', '--prefix', '/package/install'])
    assert sha(PACKAGE / 'install/lib/qml/Avelino/BleeckerFooter.qml') == sha(ROOT / 'src/Avelino/BleeckerFooter.qml')
    clone_tree(ROOT / 'tests/consumer', PACKAGE / 'consumer')
    package_base = DOCKER + ['run', '--rm', '--ulimit', 'core=0', '-v', str(PACKAGE) + ':/package', '-w', '/package', IMAGE]
    run('fresh-consumer-configure', package_base + ['cmake', '-S', 'consumer', '-B', 'consumer-build',
        '-G', 'Ninja', '-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'])
    run('fresh-consumer-build', package_base + ['cmake', '--build', 'consumer-build', '--parallel', '2'])
    RUNTIME.mkdir()
    clone_tree(PACKAGE / 'install', RUNTIME / 'install')
    (RUNTIME / 'consumer-build').mkdir()
    shutil.copy2(PACKAGE / 'consumer-build/InstalledConsumer', RUNTIME / 'consumer-build/InstalledConsumer')
    shutil.copy2(SOURCE / 'fixtures.json', RUNTIME / 'fixtures.json')
    (RUNTIME / 'captures').mkdir()
    runtime_base = DOCKER + ['run', '--rm', '--ulimit', 'core=0', '-v', str(RUNTIME) + ':/package', '-w', '/package', IMAGE]
    run('runtime-source-absence', runtime_base + ['python3', '-c',
        'from pathlib import Path; '
        'assert not Path("/work").exists() or not any(Path("/work").iterdir()); '
        'assert not any(Path(p).exists() for p in ["/package/consumer", "/package/build", "/package/src", '
        '"/package/consumer-build/CMakeCache.txt", "/Users/gaulatti/source/gaulatti/avelino"]); '
        'print("Library and consumer project sources and producer builds absent")'])
    for dark in [False, True]:
        for scale in [1, 1.5]:
            for dpr in [1, 2]:
                context = ('dark' if dark else 'light') + '-text' + str(scale) + '-dpr' + str(dpr)
                args = ['env', 'QT_QPA_PLATFORM=offscreen', 'QT_QUICK_BACKEND=software',
                    'QT_SCALE_FACTOR=' + str(dpr), './consumer-build/InstalledConsumer', '--composition', '--text-scale', str(scale)]
                if dark: args.append('--dark')
                run('installed-composition-' + context, runtime_base + args)
    rows = json.loads((SOURCE / 'captures.json').read_text())['captures']
    comparisons = []
    for index, row in enumerate(rows):
        args = ['env', 'QT_QPA_PLATFORM=offscreen', 'QT_QUICK_BACKEND=software',
            'QT_SCALE_FACTOR=' + str(row['dpr']), './install/bin/AvelinoCatalog', '--fixture', 'reference-case',
            '--case', row['fixture'], '--case-definitions', '/package/fixtures.json',
            '--text-scale', str(row['textScale']), '--capture', '/package/captures/' + row['path']]
        if row['appearance'] == 'dark': args.append('--dark')
        run('catalog-' + str(index).zfill(3), runtime_base + args)
        capture = RUNTIME / 'captures' / row['path']
        metadata = json.loads(Path(str(capture) + '.json').read_text())
        actual = metadata['footerFrames']
        geometry = {name: {axis: actual[name][axis] - value for axis, value in frame.items()}
                    for name, frame in row['frames'].items()}
        passed = all(abs(delta) <= 1e-6 for frame in geometry.values() for delta in frame.values())
        with Image.open(SOURCE / row['path']) as before, Image.open(capture) as after:
            before, after = before.convert('RGBA'), after.convert('RGBA')
            assert before.size == after.size
            delta = ImageChops.difference(before, after)
            mask = delta.getchannel('R')
            for channel in ['G', 'B', 'A']: mask = ImageChops.lighter(mask, delta.getchannel(channel))
            changed = before.width * before.height - mask.histogram()[0]
        comparisons.append(dict(source=row['path'], sha256=sha(capture), geometry=geometry,
            geometryPassed=passed, changedPixels=changed, differenceBounds=mask.getbbox(), accepted=False))
        write('comparison.json', dict(results=comparisons, rawPixels=True, referencesModified=False, accepted=False))
        assert passed, (row['path'], geometry)
    original = (ROOT / 'scripts/check-display-sessions.sh').read_text()
    loop = next(line for line in original.splitlines() if line.strip().startswith('for fixture in '))
    focused = original.replace(loop, '    for fixture in composition; do', 1)
    (RUNTIME / 'check-composition-display.sh').write_text(focused)
    environment = json.loads((PRODUCER / 'output/artifacts/linux/environment.json').read_text())
    environment.update(candidateSourceFiles=frozen, baselineProducer=str(PRODUCER), sourceBase='2b837a5fd52b462b59d8d66dae4a71a3a88bce20', uncommittedCandidate=True)
    (RUNTIME / 'environment.json').write_text(json.dumps(environment, indent=2) + '\n')
    write('display-harness.json', dict(source='scripts/check-display-sessions.sh', sourceSha256=sha(ROOT / 'scripts/check-display-sessions.sh'),
          focusedSha256=sha(RUNTIME / 'check-composition-display.sh'), originalLoop=loop,
          replacementLoop='    for fixture in composition; do', otherChanges=False))
    run('installed-composition-display', runtime_base + ['bash', 'check-composition-display.sh'])
    assert all(sha(ROOT / name) == digest for name, digest in frozen.items())
    write('result.json', dict(exitCode=0, sourceProfiles=len(rows), geometryPassed=sum(r['geometryPassed'] for r in comparisons),
          exactPixels=sum(r['changedPixels'] == 0 for r in comparisons), sourceFreeConsumerContexts=8,
          virtualCompositionDisplayContexts=8, completeFreshBuild=False, freshIndependentConsumerBuild=True,
          physicalDisplay=False, readerAcceptance=False, accepted=False, fullMirrorAccepted=False))
    write('phase.json', dict(phase='complete', finishedAt=time.time()))
except BaseException as error:
    write('result.json', dict(exitCode=1, error=repr(error), accepted=False, fullMirrorAccepted=False))
    raise
