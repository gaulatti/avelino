from pathlib import Path
import json, os, subprocess, tempfile, time

p = Path('/probe')
runtime = tempfile.mkdtemp(prefix='avelino-atspi-')
os.chmod(runtime, 0o700)
os.environ['XDG_RUNTIME_DIR'] = runtime
children = []
def spawn(command, log):
    with (p / log).open('wb') as stream:
        child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
    children.append(child)
    return child
def wait_for(predicate, child):
    while not predicate():
        if child.poll() is not None:
            raise RuntimeError('Process exited before readiness: ' + str(child.args))
        time.sleep(.05)
try:
    display = (p / 'display').open('w')
    with (p / 'xvfb.log').open('wb') as log:
        x = subprocess.Popen(['Xvfb', '-displayfd', '1', '-screen', '0', '1280x800x24', '-nolisten', 'tcp', '-noreset'], stdout=display, stderr=log)
    children.append(x)
    wait_for(lambda: bool((p / 'display').read_text().strip()), x)
    os.environ.update(DISPLAY=':' + (p / 'display').read_text().strip(), QT_QPA_PLATFORM='xcb',
                      QT_QUICK_BACKEND='software', QT_SCALE_FACTOR='1',
                      QT_LINUX_ACCESSIBILITY_ALWAYS_ON='1', LANG='C.UTF-8')
    keys = ['DISPLAY', 'DBUS_SESSION_BUS_ADDRESS', 'XDG_RUNTIME_DIR', 'QT_QPA_PLATFORM',
            'QT_QUICK_BACKEND', 'QT_SCALE_FACTOR', 'QT_LINUX_ACCESSIBILITY_ALWAYS_ON', 'LANG']
    (p / 'session-env.json').write_text(json.dumps({key: os.environ[key] for key in keys}, indent=2) + '\n')
    monitor = spawn(['python3', '/probe/event-monitor.py'], 'event-monitor.log')
    wait_for(lambda: (p / 'event-monitor-ready').exists(), monitor)
    command = ['orca', '--replace', '--user-prefs=/probe/orca-prefs', '--disable=braille',
               '--enable=speech', '--debug-file=/probe/orca-debug.log']
    reader = spawn(command, 'orca-stdout.log')
    (p / 'orca-pid.json').write_text(json.dumps(dict(pid=reader.pid, command=command), indent=2) + '\n')
    wait_for(lambda: (p / 'orca-debug.log').exists() and "SPEECH OUTPUT: 'Screen reader on.'" in (p / 'orca-debug.log').read_text(), reader)
    subprocess.run(['xdotool', 'mousemove', '--sync', '1279', '799'], check=True)
    app = spawn(['install/bin/AvelinoCatalog', '--fixture', 'file-input', '--file-input-folder', '/probe/fixtures'], 'client.log')
    (p / 'client-pid.json').write_text(json.dumps(dict(pid=app.pid)) + '\n')
    (p / 'ready').touch()
    while not (p / 'finished').exists():
        for child in [app, reader, monitor, x]:
            if child.poll() is not None:
                raise RuntimeError('Session process exited: ' + str(child.args))
        time.sleep(.1)
finally:
    for child in reversed(children):
        if child.poll() is None:
            child.terminate()
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired: child.kill(); child.wait()
