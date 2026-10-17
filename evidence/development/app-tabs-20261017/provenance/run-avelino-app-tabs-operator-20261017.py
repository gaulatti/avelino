from pathlib import Path
from PIL import Image,ImageChops
import copy,hashlib,json,shutil,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016';p=base/'app-tabs-operator-v1';assert not p.exists();p.mkdir();package=base/'app-tabs-build-v8'
shutil.copytree(package/'install',p/'install');(p/'references').mkdir()
tabs=[dict(value=v,label=l,systemImage=i,**({'badge':'7'}if v=='b'else{}))for v,l,i in [('a','Home','house'),('b','Inbox','tray'),('c','Settings','gearshape')]]
configuration=dict(id='default',tabs=tabs,selection='a',valueKind='string',width=300,height=None,rtl=False,disabled=False,parentFont=False,parentRed=False,owner='echo')
phases=[];dark=False;scale=1;selection='a';pending=None
reversed_tabs=list(reversed(tabs));badges=[dict(t,badge='100')for t in reversed_tabs]
updates=[('initial',None,{},None),('inbox','tab-b',{},'b'),('observe','owner-observe',dict(owner='observe'),None),('observe-home','tab-a',{},'a'),('delayed','owner-delayed',dict(owner='delayed'),None),('delayed-settings','tab-c',{},'c'),('flush','flush',{},None),('redirect','owner-redirect',dict(owner='redirect'),None),('redirect-inbox','tab-b',{},'b'),('external','external',{},None),('echo','owner-echo',dict(owner='echo'),None),('echo-inbox','tab-b',{},'b'),('reverse','reorder',dict(tabs=reversed_tabs),None),('badges','badges',dict(tabs=badges),None),('narrow','width',dict(width=30),None),('rtl','rtl',dict(rtl=True),None),('dark','theme',{},None),('scaled','scale',{},None),('disabled','disabled',dict(disabled=True),None),('disabled-home','tab-a',{},'a'),('enabled','disabled',dict(disabled=False),None),('empty','empty',dict(tabs=[]),None),('restore','empty',dict(tabs=tabs),None),('width150','width',dict(width=150),None),('width300','width',dict(width=300),None),('ltr','rtl',dict(rtl=False),None),('light','theme',{},None),('scale-restored','scale',{},None)]
for name,control,update,requested in updates:
 oldscale=scale;configuration.update(update)
 if control=='theme':dark=not dark
 if control=='scale':scale=1.5 if scale==1 else 1
 if requested is not None and not configuration['disabled']:
  if configuration['owner']=='echo':selection=requested
  elif configuration['owner']=='delayed':pending=requested
  elif configuration['owner']=='redirect':selection=configuration['tabs'][0]['value']
 if control=='flush'and pending is not None:selection=pending;pending=None
 if control=='external':selection='c'
 definition=dict(configuration,id='operator-'+name,fixture='app-tabs-operator-'+name,api='BleeckerAppTabBar',source='fe8a1d462fbd793d883fb92086a16aa2947e32c9',tabWidth=configuration['width'],tabHeight=configuration['height'],width=640,height=400,selection=selection)
 phases.append(dict(name=name,control=control,scaleBefore=oldscale,dark=dark,textScale=scale,selection=selection,pending=pending,definition=copy.deepcopy(definition)))
(p/'phases.json').write_text(json.dumps(phases,indent=2)+'\n');(p/'fixture-inputs.json').write_text(json.dumps({'fixtures':[r['definition'] for r in phases]},indent=2)+'\n')
(p/'reference-driver.py').write_text("""from pathlib import Path
import json,os,subprocess
p=Path('/package');environment=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1',LANG='C.UTF-8')
for row in json.loads((p/'phases.json').read_text()):
 command=['install/bin/AvelinoCatalog','--fixture','reference-case','--case',row['definition']['fixture'],'--case-definitions','/package/fixture-inputs.json','--text-scale',str(row['textScale']),'--capture','/package/references/'+row['name']+'.png']
 if row['dark']:command.append('--dark')
 with (p/'references'/(row['name']+'.log')).open('w') as log:r=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,(row['name'],r.returncode)
for scale in [1,1.5]:
 command=['install/bin/AvelinoCatalog','--fixture','app-tabs','--text-scale',str(scale),'--capture','/package/references/gallery-text'+str(scale)+'.png']
 with (p/'references'/('gallery-text'+str(scale)+'.log')).open('w') as log:r=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,scale
""")
(p/'start.sh').write_text("""#!/usr/bin/env bash
set -euo pipefail
python3 reference-driver.py
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>/package/display >/package/xvfb.log 2>&1 &
xpid=$!
client=
cleanup(){ if [[ -n "$client" ]]; then kill "$client" 2>/dev/null || true;wait "$client" 2>/dev/null || true;fi;kill "$xpid" 2>/dev/null || true;wait "$xpid" 2>/dev/null || true; }
trap cleanup EXIT
while [[ ! -s /package/display ]]; do kill -0 "$xpid";sleep .1;done
export DISPLAY=":$(cat /package/display)"
xdotool mousemove --sync 2559 1919
QT_QPA_PLATFORM=xcb QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 install/bin/AvelinoCatalog --fixture app-tabs >/package/client.log 2>&1 &
client=$!
touch /package/display-ready
while [[ ! -f /package/finished ]]; do kill -0 "$client";sleep .1;done
""")
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-app-tabs-operator-v1','-v',str(p)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','bash','start.sh']
start=time.monotonic();log=(p/'run.log').open('w');process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);records=[];receipt={}
try:
 while not (p/'display-ready').exists():
  if process.poll() is not None:raise RuntimeError(('Operator startup failed',process.returncode,(p/'run.log').read_text()))
  time.sleep(.1)
 number=(p/'display').read_text().strip();assert number.isdigit()
 def execute(*args):return subprocess.check_output(['docker','--context','colima-avelino-verify','exec','-e','DISPLAY=:'+number,'avelino-app-tabs-operator-v1',*args],stderr=subprocess.STDOUT)
 controls={}
 from collections import Counter
 captionRows=[(24,['owner-'+s for s in ['echo','observe','delayed','redirect']]+['flush','external','reorder','empty']),(80,['width','badges','disabled','rtl','theme','scale'])]
 for scale in [1,1.5]:
  image=Image.open(p/'references'/('gallery-text'+str(scale)+'.png')).convert('RGB');background=image.getpixel((0,0))
  fill=Counter(c for c in image.crop((0,0,700,180)).getdata() if c!=background).most_common(1)[0][0];controls[scale]={}
  for top,names in captionRows:
   spans=[]
   for x in range(1000):
    if image.getpixel((x,top+4))!=background:
     if spans and spans[-1][-1]+1==x:spans[-1].append(x)
     else:spans.append([x])
   spans=[span for span in spans if len(span)>10];assert len(spans)==len(names),(scale,top,spans)
   for name,span in zip(names,spans):controls[scale][name]=dict(x=span[0],y=top,width=span[-1]-span[0]+1,height=28)
  assert len(controls[scale])==14
 (p/'observed-controls.json').write_text(json.dumps(controls,indent=2)+'\n')
 wid=execute('xdotool','search','--sync','--onlyvisible','--name','^Avelino app tabs$').decode().strip().splitlines();assert len(wid)==1,wid;wid=wid[0]
 geometry=execute('xdotool','getwindowgeometry','--shell',wid).decode();(p/'window-geometry.txt').write_text(geometry);g=dict(line.split('=',1) for line in geometry.splitlines() if '=' in line)
 for index,row in enumerate(phases):
  click=None
  if row['control']:
   if row['control'].startswith('tab-'):
    previous=phases[index-1];value=row['control'][4:];i=next(i for i,t in enumerate(previous['definition']['tabs'])if t['value']==value)
    meta=json.loads((p/'references'/(previous['name']+'.png.json')).read_text());frame=meta['appTabFrame']['button-'+str(i)]
    target=dict(x=frame['x'],y=frame['y']+180,width=frame['width'],height=frame['height'])
   else:target=controls[row['scaleBefore']][row['control']]
   click=[round(float(g['X'])+target['x']+target['width']/2),round(float(g['Y'])+target['y']+target['height']/2)]
   execute('xdotool','mousemove','--sync',str(click[0]),str(click[1]),'click','1');execute('xdotool','mousemove','--sync','2559','1919')
  expected=Image.open(p/'references'/(row['name']+'.png')).convert('RGBA');attempts=[];passed=False
  for n in range(30):
   path=p/(row['name']+f'-observation-{n}.png');execute('import','-window',wid,'/package/'+path.name)
   with Image.open(path) as full:
    assert full.size==(1120,820),full.size
    actual=full.convert('RGBA').crop((0,180,640,580))
   passed=actual.tobytes()==expected.tobytes();delta=ImageChops.difference(actual,expected).convert('RGB').getbbox()
   attempts.append(dict(path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),exactViewportMatch=passed,differenceBounds=delta))
   if passed:break
   time.sleep(.2)
  records.append(dict(phase=row['name'],click=click,reference='references/'+row['name']+'.png',viewport=[0,180,640,400],passed=passed,attempts=attempts))
  print('AppTabs operator:',row['name'],'exact viewport' if passed else 'strict viewport difference retained',flush=True)
 (p/'finished').touch();code=process.wait();assert code==0,code
 receipt=dict(status='passed' if all(r['passed'] for r in records) else 'failed',exitCode=0 if all(r['passed'] for r in records) else 1,accepted=False,controls=14,phases=len(records),clicks=len(records)-1,records=records,command=command,seconds=time.monotonic()-start,sourceAndConsumerSourcesAbsent=True,producerBuildAbsent=True,physicalDisplay=False,delivery='XTest through Xvfb/X11 to installed catalog toolbar controls; exact full caller viewport against separate installed isolated fixtures')
except BaseException as error:
 receipt=dict(status='failed',accepted=False,error=repr(error),records=records,command=command,seconds=time.monotonic()-start)
 subprocess.run(['docker','--context','colima-avelino-verify','stop','--time','5','avelino-app-tabs-operator-v1'],stdout=log,stderr=subprocess.STDOUT);process.wait();raise
finally:
 log.close();(p/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['records','command']},indent=2))

raise SystemExit(receipt['exitCode'])
