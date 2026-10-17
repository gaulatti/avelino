from pathlib import Path
import json, os, subprocess, tempfile, time
p=Path('/probe');children=[]
runtime=tempfile.mkdtemp(prefix='avelino-wayland-');os.chmod(runtime,0o700)
os.environ.update(XDG_RUNTIME_DIR=runtime,LIBGL_ALWAYS_SOFTWARE='1',QSG_INFO='1')
def spawn(command,name,stdout=None):
    with(p/name).open('wb')as log:child=subprocess.Popen(command,stdout=stdout or log,stderr=log)
    children.append(child);return child
def until(predicate,child):
    while not predicate():
        if child.poll()is not None:raise RuntimeError(str(child.args)+' exited '+str(child.returncode))
        time.sleep(.05)
try:
    with(p/'display').open('w')as display:
        x=spawn(['Xvfb','-displayfd','1','-screen','0','2560x1920x24','-nolisten','tcp','-noreset'],'xvfb.log',display)
    until(lambda:(p/'display').read_text().strip(),x)
    os.environ['DISPLAY']=':'+(p/'display').read_text().strip()
    (p/'weston.ini').write_text('[shell]\npanel-position=none\nbackground-color=0xffdbe1e7\nlocking=false\n')
    compositor=spawn(['weston','--backend=x11','--renderer=pixman','--width=2400','--height=1800','--socket=avelino-wayland','--idle-time=0','--config=/probe/weston.ini','--log=/probe/weston.log'],'weston-client.log')
    until(lambda:Path(runtime+'/avelino-wayland').is_socket(),compositor)
    os.environ.update(WAYLAND_DISPLAY='avelino-wayland',QT_QPA_PLATFORM='wayland',QSG_RHI_BACKEND='opengl',QT_SCALE_FACTOR='2',QT_LINUX_ACCESSIBILITY_ALWAYS_ON='1',LANG='C.UTF-8')
    keys=['DISPLAY','DBUS_SESSION_BUS_ADDRESS','XDG_RUNTIME_DIR','WAYLAND_DISPLAY','QT_QPA_PLATFORM','QSG_RHI_BACKEND','QT_SCALE_FACTOR','QT_LINUX_ACCESSIBILITY_ALWAYS_ON','LIBGL_ALWAYS_SOFTWARE','QSG_INFO','LANG']
    (p/'session-env.json').write_text(json.dumps({k:os.environ[k]for k in keys},indent=2)+'\n')
    monitor=spawn(['python3','/probe/event-monitor.py'],'event-monitor.log')
    until(lambda:(p/'event-monitor-ready').exists(),monitor)
    subprocess.run(['xdotool','mousemove','--sync','2559','1919'],check=True)
    app=spawn(['install/bin/AvelinoCatalog','--fixture','file-input','--file-input-folder','/probe/fixtures','--dark','--text-scale','1.5'],'client.log')
    (p/'client-pid.json').write_text(json.dumps(dict(pid=app.pid))+'\n');(p/'ready').touch()
    while not(p/'finished').exists():
        if app.poll()is not None:raise RuntimeError('Catalog exited '+str(app.returncode))
        time.sleep(.1)
finally:
    for child in reversed(children):
        if child.poll()is None:child.terminate();child.wait()
