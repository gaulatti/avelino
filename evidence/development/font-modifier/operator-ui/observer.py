from pathlib import Path
from PIL import Image,ImageChops
from collections import Counter
import hashlib,json,os,shutil,subprocess,time,sys
root=Path('/Users/gaulatti/source/gaulatti/avelino');run=root/'artifacts/resumed-avelino-20261016/font-modifier-integration-v5'
output=run/'ui-operator';output.mkdir(exist_ok=False)
runtime=run/'runtime-only'
shutil.copytree(runtime/'install',output/'install');(output/'consumer-build').mkdir();shutil.copy2(runtime/'consumer-build/InstalledConsumer',output/'consumer-build/InstalledConsumer')
script='''#!/usr/bin/env bash
set -euo pipefail
Xvfb -displayfd 3 -screen 0 1600x1200x24 -nolisten tcp 3>/package/display >/package/xvfb.log 2>&1 &
xpid=$!
trap 'kill "$xpid" 2>/dev/null || true; wait "$xpid" 2>/dev/null || true' EXIT
while [[ ! -s /package/display ]]; do kill -0 "$xpid";sleep 0.1;done
export DISPLAY=":$(cat /package/display)"
export QT_QPA_PLATFORM=xcb QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1
consumer-build/InstalledConsumer --font-modifier --evidence /package/client >/package/client.log 2>&1
'''
(output/'start.sh').write_text(script)
name='avelino-font-v5-ui-operator'
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name',name,'-v',str(output)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','bash','start.sh']
start=time.monotonic();log=(output/'run.log').open('w');process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
records=[];result={}
def execute(args):return subprocess.check_output(['docker','--context','colima-avelino-verify','exec',name,*args],text=True).strip()
try:
 deadline=time.monotonic()+90
 while not (output/'client.json').exists():
  if process.poll() is not None:raise RuntimeError('UI client exited before readiness; preserve logs')
  assert time.monotonic()<deadline,'UI client readiness deadline; process and artifacts preserved'
  time.sleep(.1)
 display=':'+ (output/'display').read_text().strip()
 def xdo(*args):return execute(['env','DISPLAY='+display,'xdotool',*args])
 window=xdo('search','--onlyvisible','--name','^Avelino inherited caller fonts$').splitlines()
 assert len(window)==1,window
 window=window[0]
 geometry=xdo('getwindowgeometry','--shell',window);(output/'window-geometry.txt').write_text(geometry+'\n')
 def observe(phase,reference,point=None):
  if point is not None:xdo('mousemove','--window',window,str(point[0]),str(point[1]),'click','1')
  expected=Image.open(run/'captures'/reference).convert('RGBA');assert expected.size==(640,400)
  attempts=[];deadline=time.monotonic()+8
  for index in range(100):
   path=output/(phase+f'-observation-{index}.png')
   execute(['env','DISPLAY='+display,'import','-window',window,'/package/'+path.name])
   with Image.open(path) as image:
    assert image.size==(1100,820),image.size
    viewport=image.convert('RGBA').crop((24,202,664,602))
   matches=viewport.tobytes()==expected.tobytes()
   delta=ImageChops.difference(viewport.convert('RGB'),expected.convert('RGB'))
   attempts.append(dict(path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),exactViewportMatch=matches,differenceBounds=delta.getbbox()))
   if matches:break
   if time.monotonic()>deadline:raise AssertionError((phase,attempts))
   time.sleep(.05)
  else:raise AssertionError((phase,attempts))
  records.append(dict(phase=phase,click=point,reference=reference,referenceSha256=hashlib.sha256((run/'captures'/reference).read_bytes()).hexdigest(),
   viewport=[24,202,640,400],attempts=attempts,passed=True))
  print('Operator UI:',phase,'exact caller viewport',flush=True)
  return path
 observe('initial','caller-primary-regular-light-text1.0-dpr1.0-mode0.png')
 observe('secondary','caller-secondary-regular-light-text1.0-dpr1.0-mode0.png',(158,42))
 observe('bold','caller-secondary-bold-light-text1.0-dpr1.0-mode0.png',(393,42))
 observe('regular-restored','caller-secondary-regular-light-text1.0-dpr1.0-mode0.png',(393,42))
 observe('larger','caller-size-secondary-24.0-light-text1.0-dpr1.0-mode0.png',(313,42))
 observe('size-restored','caller-secondary-regular-light-text1.0-dpr1.0-mode0.png',(313,42))
 observe('baseline','baseline-secondary-regular-light-text1.0-dpr1.0-mode0.png',(477,42))
 scaled=observe('scaled','baseline-secondary-regular-light-text1.5-dpr1.0-mode0.png',(240,156))
 with Image.open(scaled) as im:
  im=im.convert('RGB');background=im.getpixel((0,0));colors=[im.getpixel((x,145)) for x in range(700)]
  fill=Counter(c for c in colors if c!=background).most_common(1)[0][0]
  spans=[]
  for x,c in enumerate(colors):
   if c==fill:
    if spans and spans[-1][-1]+1==x:spans[-1].append(x)
    else:spans.append([x])
  spans=[s for s in spans if len(s)>10];assert len(spans)>=4,spans
  target=((spans[-1][0]+spans[-1][-1])//2,158)
 observe('dark','baseline-secondary-regular-dark-text1.5-dpr1.0-mode0.png',target)
 (output/'client.captured').touch();code=process.wait(timeout=20);assert code==0,code
 result=dict(status='passed',exitCode=0,accepted=False,sourceAndConsumerSourcesAbsent=True,producerBuildAbsent=True,
  delivery='xdotool XTest mouse events delivered through Xvfb X11 to real gallery controls',
  scope='Actual family, weight, size, baseline, scaling and theme toolbar callbacks; complete 640x400 caller viewport compared exactly with independently captured Qt closed fixtures. Full window PNGs retained. Native strict/physical/reader acceptance remains separate.',
  controls=6,clicks=8,phases=len(records),records=records,physicalDisplay=False,command=command,seconds=time.monotonic()-start)
except BaseException as error:
 result=dict(status='failed',accepted=False,error=repr(error),records=records,command=command,seconds=time.monotonic()-start)
 # End only this diagnostic container after preserving the failure; do not restart it.
 subprocess.run(['docker','--context','colima-avelino-verify','stop','--time','5',name],stdout=log,stderr=subprocess.STDOUT)
 process.wait(timeout=20)
 raise
finally:
 log.close();(output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
