from pathlib import Path
import hashlib,json,os,subprocess,tempfile,time
p=Path('/probe');runtime=tempfile.mkdtemp(prefix='stock-wayland-');os.chmod(runtime,0o700)
os.environ.update(XDG_RUNTIME_DIR=runtime,QT_QPA_PLATFORM='wayland',QT_QUICK_BACKEND='software',LIBGL_ALWAYS_SOFTWARE='1',WAYLAND_DISPLAY='stock-popup',LANG='C.UTF-8')
children=[]
def spawn(command,log):
 with(p/log).open('wb')as stream:child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT)
 children.append(child);return child
def wait_for(predicate,child):
 end=time.monotonic()+10
 while not predicate():
  assert child.poll()is None,child.args
  assert time.monotonic()<end,'Readiness timeout'
  time.sleep(.05)
try:
 display=(p/'display').open('w')
 with(p/'xvfb.log').open('wb')as stream:x=subprocess.Popen(['Xvfb','-displayfd','1','-screen','0','1600x1200x24','-nolisten','tcp','-noreset'],stdout=display,stderr=stream)
 children.append(x);wait_for(lambda:bool((p/'display').read_text().strip()),x);os.environ['DISPLAY']=':'+(p/'display').read_text().strip()
 (p/'weston.ini').write_text('[shell]\npanel-position=none\nlocking=false\n')
 weston=spawn(['gdb','-batch','-ex','set debuginfod enabled off','-ex','run','-ex','thread apply all bt','--args','weston','--backend=x11','--renderer=pixman','--width=1400','--height=1000','--socket=stock-popup','--idle-time=0','--config=/probe/weston.ini','--log=/probe/weston.log'],'weston-gdb.log')
 wait_for(lambda:Path(runtime+'/stock-popup').is_socket(),weston)
 owner=spawn(['build/StockTooltip','--tooltip'],'owner.log');wait_for(lambda:(p/'stock-tooltip-ready.json').exists(),owner)
 assert json.loads((p/'stock-tooltip-ready.json').read_text())['stockQtTooltipVisible']is True
 subprocess.run(['import','-window','root','/probe/stock-tooltip.png'],check=True)
 other=spawn(['build/StockTooltip'],'second.log')
 end=time.monotonic()+4
 while weston.poll()is None and time.monotonic()<end:time.sleep(.05)
 raw=(p/'weston-gdb.log').read_text();crash='Program received signal SIGSEGV' in raw
 result=dict(accepted=False,avelinoLibraryLoaded=False,stockQt='6.8.3',weston=subprocess.check_output(['weston','--version'],text=True).strip(),stockTooltipVisible=True,stockTooltipReproducesCrash=crash,westonGdbExit=weston.poll(),ownerExit=owner.poll(),otherExit=other.poll(),helperSha256=hashlib.sha256((p/'build/StockTooltip').read_bytes()).hexdigest())
 (p/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
finally:
 for child in reversed(children):
  if child.poll()is None:
   child.terminate()
   try:child.wait(timeout=3)
   except subprocess.TimeoutExpired:child.kill();child.wait()
