from pathlib import Path
import json,os,subprocess,tempfile,time
p=Path('/probe');runtime=tempfile.mkdtemp(prefix='avelino-atspi-');os.chmod(runtime,0o700);os.environ['XDG_RUNTIME_DIR']=runtime
log=(p/'xvfb.log').open('wb');display=(p/'display').open('w');x=subprocess.Popen(['Xvfb','-displayfd','1','-screen','0','1280x800x24','-nolisten','tcp','-noreset'],stdout=display,stderr=log)
app=None
try:
 while not (p/'display').read_text().strip():
  if x.poll()is not None:raise RuntimeError('Xvfb exited before readiness')
  time.sleep(.05)
 os.environ.update(DISPLAY=':'+ (p/'display').read_text().strip(),QT_QPA_PLATFORM='xcb',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1',QT_LINUX_ACCESSIBILITY_ALWAYS_ON='1',LANG='C.UTF-8')
 (p/'session-env.json').write_text(json.dumps({key:os.environ[key]for key in ['DISPLAY','DBUS_SESSION_BUS_ADDRESS','XDG_RUNTIME_DIR','QT_QPA_PLATFORM','QT_QUICK_BACKEND','QT_SCALE_FACTOR','QT_LINUX_ACCESSIBILITY_ALWAYS_ON','LANG']},indent=2)+chr(10))
 subprocess.run(['xdotool','mousemove','--sync','1279','799'],check=True)
 with(p/'client.log').open('wb')as client:app=subprocess.Popen(['install/bin/AvelinoCatalog','--fixture','file-input','--file-input-folder','/probe/fixtures'],stdout=client,stderr=subprocess.STDOUT)
 (p/'client-pid.json').write_text(json.dumps(dict(pid=app.pid))+chr(10));(p/'ready').touch()
 while not(p/'finished').exists():
  if app.poll()is not None:raise RuntimeError('Catalog exited '+str(app.returncode))
  time.sleep(.1)
finally:
 if app is not None and app.poll()is None:app.terminate();app.wait()
 x.terminate();x.wait();display.close();log.close()
