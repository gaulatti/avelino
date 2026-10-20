from pathlib import Path
import json, os, subprocess, tempfile, time, shutil

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
        x = subprocess.Popen(['Xvfb', '-displayfd', '1', '-screen', '0', '2560x1920x24', '-nolisten', 'tcp', '-noreset'], stdout=display, stderr=log)
    children.append(x)
    wait_for(lambda: bool((p / 'display').read_text().strip()), x)
    os.environ.update(DISPLAY=':' + (p / 'display').read_text().strip(), QT_QPA_PLATFORM='wayland',
                      QSG_RHI_BACKEND='opengl', QT_SCALE_FACTOR='2', LIBGL_ALWAYS_SOFTWARE='1', QSG_INFO='1',
                      QT_LINUX_ACCESSIBILITY_ALWAYS_ON='1', LANG='C.UTF-8', WAYLAND_DEBUG='1')
    os.environ['XDG_CONFIG_HOME'] = '/probe/config'
    config = p / 'config/speech-dispatcher'
    shutil.copytree('/etc/speech-dispatcher', config)
    speech_config = config / 'speechd.conf'
    source_config = speech_config.read_text()
    assert '# AudioOutputMethod \"pulse\"' in source_config
    assert '#AudioALSADevice \"default\"' in source_config
    speech_config.write_text(source_config.replace('# AudioOutputMethod \"pulse\"', 'AudioOutputMethod \"alsa\"').replace('#AudioALSADevice \"default\"', 'AudioALSADevice \"null\"'))
    keys = ['XDG_CONFIG_HOME', 'DISPLAY', 'DBUS_SESSION_BUS_ADDRESS', 'XDG_RUNTIME_DIR', 'QT_QPA_PLATFORM',
            'QT_SCALE_FACTOR', 'QT_LINUX_ACCESSIBILITY_ALWAYS_ON', 'LANG']
    (p / 'session-env.json').write_text(json.dumps({key: os.environ[key] for key in keys}, indent=2) + '\n')
    (p/'weston.ini').write_text('[shell]\npanel-position=none\nlocking=false\n')
    weston=spawn(['weston','--backend=x11','--renderer=pixman','--width=2400','--height=1800','--socket=avelino-errors','--idle-time=0','--config=/probe/weston.ini','--log=/probe/weston.log'],'weston-client.log')
    (p/'weston-pid.json').write_text(json.dumps(dict(pid=weston.pid))+'\n')
    wait_for(lambda: Path(runtime+'/avelino-errors').is_socket(),weston)
    # XTest targets the nested compositor's X11 host, not PointerRoot.
    # This changes only test transport focus; no native key is sent here.
    command=['xdotool','search','--onlyvisible','--name','^Weston Compositor - screen0$']
    hosts=subprocess.check_output(command,text=True).split();assert len(hosts)==1,hosts
    host=hosts[0];focus_command=['xdotool','windowfocus','--sync',host]
    subprocess.run(focus_command,check=True)
    observed=subprocess.check_output(['xdotool','getwindowfocus'],text=True).strip();assert observed==host
    (p/'native-focus-setup.json').write_text(json.dumps(dict(searchCommand=command,focusCommand=focus_command,focusedWindow=observed,exitCode=0,keyEventsSent=0),indent=2)+'\n')
    os.environ['WAYLAND_DISPLAY']='avelino-errors'
    keys=[key for key in keys if key!='QT_QUICK_BACKEND']+['WAYLAND_DISPLAY','QSG_RHI_BACKEND','LIBGL_ALWAYS_SOFTWARE','QSG_INFO','WAYLAND_DEBUG']
    (p/'session-env.json').write_text(json.dumps({key:os.environ[key] for key in keys},indent=2)+'\n')
    monitor = spawn(['python3', '/probe/event-monitor.py'], 'event-monitor.log')
    wait_for(lambda: (p / 'event-monitor-ready').exists(), monitor)
    command = ['python3', '/probe/reader-diagnostic.py', '--replace', '--user-prefs=/probe/orca-prefs', '--disable=braille',
               '--enable=speech', '--debug-file=/probe/orca-debug.log']
    reader = spawn(command, 'orca-stdout.log')
    (p / 'orca-pid.json').write_text(json.dumps(dict(pid=reader.pid, command=command), indent=2) + '\n')
    wait_for(lambda: (p / 'orca-debug.log').exists() and "SPEECH OUTPUT: 'Screen reader on.'" in (p / 'orca-debug.log').read_text(), reader)
    subprocess.run(['xdotool', 'mousemove', '--sync', '2559', '1919'], check=True)
    app = spawn(['install/bin/AvelinoCatalog', '--fixture', 'file-input', '--file-input-folder', '/probe/fixtures', '--dark', '--text-scale', '1.5'], 'client.log')
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
