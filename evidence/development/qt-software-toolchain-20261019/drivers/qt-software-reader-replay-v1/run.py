"""Replay retained reader flows against the fresh package and patched Qt image."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time
import traceback

P = Path(__file__).resolve().parent
BASE = P.parent
ROOT = P.parents[2]
DOCKER = ['docker', '--context', 'colima-avelino-verify']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def inventory(path):
    return {str(f.relative_to(path)): sha(f) for f in sorted(path.rglob('*'))
            if f.is_file()}


def wait_result(directory):
    while not (directory / 'result.json').exists():
        time.sleep(10)
    value = json.loads((directory / 'result.json').read_text())
    assert value['exitCode'] == 0, value
    return value


def command(profile, name, args):
    started = time.monotonic()
    with (profile / (name + '.log')).open('x') as output:
        completed = subprocess.run(args, stdout=output, stderr=subprocess.STDOUT)
    write(profile / (name + '-command.json'), dict(command=args,
          exitCode=completed.returncode, seconds=time.monotonic() - started))
    return completed.returncode


def run_profile(name, producer, image_id, package, frozen):
    previous = BASE / producer
    profile = P / name
    profile.mkdir()
    copied = ['session.py', 'exercise.py', 'event-monitor.py',
              'reader-diagnostic.py', 'collect.py', 'profile.json']
    for filename in copied:
        shutil.copy2(previous / filename, profile / filename)
    shutil.copytree(previous / 'fixtures', profile / 'fixtures')
    (profile / 'orca-prefs').mkdir()
    for filename in ['user-settings.conf', 'orca-customizations.py', '__init__.py']:
        shutil.copy2(previous / 'orca-prefs' / filename,
                     profile / 'orca-prefs' / filename)
    shutil.copytree(package, profile / 'install', symlinks=True)
    package_files = inventory(profile / 'install')
    assert package_files == inventory(package)
    write(profile / 'inputs.json', dict(previousProducer=producer,
          scripts={filename: sha(profile / filename) for filename in copied},
          fixtures=inventory(profile / 'fixtures'),
          readerPreferences=inventory(profile / 'orca-prefs'),
          packageFiles=package_files, imageId=image_id,
          packageProducer='qt-software-final-image-v3',
          sourceRevision=frozen['sourceRevision'] if 'sourceRevision' in frozen else None,
          libraryProjectSourcesMounted=False, accepted=False))
    container = 'avelino-qt-opacity-reader-v1-' + name
    launch = DOCKER + ['run', '--detach', '--name', container, '--ulimit', 'core=0',
                      '-v', str(profile) + ':/probe', '-w', '/probe', image_id,
                      'dbus-run-session', '--', 'python3', '/probe/session.py']
    container_id = subprocess.check_output(launch, text=True).strip()
    write(profile / 'session-launch.json', dict(command=launch, containerId=container_id))
    exercise_exit = None
    collect_exit = None
    failure = None
    try:
        while not (profile / 'ready').exists():
            running = subprocess.check_output(DOCKER + ['inspect', '--format',
                '{{.State.Running}}', container_id], text=True).strip()
            assert running == 'true', 'Reader session ended before readiness'
            time.sleep(1)
        exercise_exit = command(profile, 'exercise',
            DOCKER + ['exec', container_id, 'python3', '/probe/exercise.py'])
        collect_exit = command(profile, 'collect',
            DOCKER + ['exec', container_id, 'python3', '/probe/collect.py'])
        assert exercise_exit == collect_exit == 0
    except BaseException:
        failure = traceback.format_exc()
    finally:
        (profile / 'finished').touch()
        session_exit = subprocess.check_output(DOCKER + ['wait', container_id], text=True).strip()
        command(profile, 'session-output', DOCKER + ['logs', container_id])
    assert failure is None, failure
    assert session_exit == '0'
    report = json.loads((profile / 'operator-controls-v1/result.json').read_text())
    assert report['status'] == 'passed' and len(report['phases']) == 21
    assert report['nativeKeyFlow'] == report['directAssistiveTextEdit'] == 'passed'
    assert not report['physicalListening'] and not report['physicalInput']
    speech = (profile / 'orca-debug.log').read_bytes()
    phases = report['phases']
    speech_windows = {}
    for phase_name, observation_key, target in [
        ('go-to-native-arrows-preserve-input', 'arrowReaderStartBytes', 'Alpine'),
        ('go-to-assistive-selection-keeps-input', 'readerStartBytes', 'Alphabet')]:
        row = next(row for row in phases if row['phase'] == phase_name)
        start = row['observations'][observation_key]
        end = row['readerLogBytes']
        lines = speech[start:end].decode().splitlines()
        spoken = [line for line in lines if 'SPEECH OUTPUT:' in line and target in line]
        backend = [line for line in lines if 'SPEECH DISPATCHER: Speaking' in line and target in line]
        assert spoken and backend, (phase_name, target)
        speech_windows[phase_name] = dict(startBytes=start, endBytes=end,
            sha256=hashlib.sha256(speech[start:end]).hexdigest(),
            utterances=spoken, backendCommands=backend)
    assert inventory(profile / 'install') == package_files
    assert all(sha(ROOT / filename) == value for filename, value in frozen['files'].items())
    result = dict(exitCode=0, profile=report['profile'], phases=len(phases),
        nativeKeyFlow='passed', directAssistiveTextEdit='passed',
        speechWindows=speech_windows, exerciseExit=exercise_exit,
        collectExit=collect_exit, sessionExit=int(session_exit),
        packageFilesUnchanged=True, rootSourceInputsUnchanged=True,
        physicalListening=False, physicalInput=False,
        nativeReaderComparison='pending', fullMirrorAccepted=False)
    write(profile / 'result.json', result)
    print(name, '21 reader phases passed', flush=True)
    return result


try:
    write(P / 'phase.json', dict(phase='waiting-for-reader-image', startedAt=time.time()))
    reader = wait_result(BASE / 'qt-software-reader-image-v1')
    runtime = wait_result(BASE / 'qt-software-final-image-v3')
    assert reader['baseImageId'] == runtime['imageId']
    assert reader['qtSdkEntriesUnchanged'] == 9236
    frozen = json.loads((BASE / 'qt-software-final-image-v2/inputs.json').read_text())
    assert all(sha(ROOT / filename) == value for filename, value in frozen['files'].items())
    write(P / 'inputs.json', dict(readerImage=reader,
        runtimeProducer='qt-software-final-image-v3', sourceInputs=frozen,
        previousReaderProducers=['file-input-go-to-reader-v13', 'file-input-go-to-reader-v14']))
    package = BASE / 'qt-software-final-image-v3/runtime/install'
    profiles = {}
    for name, producer in [('x11-software', 'file-input-go-to-reader-v13'),
                           ('wayland-opengl-scaled', 'file-input-go-to-reader-v14')]:
        write(P / 'phase.json', dict(phase=name, startedAt=time.time()))
        profiles[name] = run_profile(name, producer, reader['imageId'], package, frozen)
    write(P / 'result.json', dict(exitCode=0, imageId=reader['imageId'],
        baseImageId=reader['baseImageId'], profiles=profiles, phases=42,
        freshInstalledPackage=True, qtSdkUnchanged=True,
        physicalListening=False, nativeReaderComparison='pending', fullMirrorAccepted=False))
    write(P / 'phase.json', dict(phase='complete', finishedAt=time.time()))
except BaseException as error:
    write(P / 'result.json', dict(exitCode=1, error=repr(error), fullMirrorAccepted=False))
    raise
