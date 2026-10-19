from pathlib import Path
import ctypes,hashlib,json,os,shutil,subprocess,time
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent;ROOT=P.parents[2];BASE=P.parent
BUILD=BASE/'mobile-shell-compiled-v5';SOURCE=ROOT/'evidence/reference-investigations/mobile-shell-slots-20261019/run-v2/output'
IMAGE='sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'
DOCKER=['docker','--context','colima-avelino-verify'];RUNTIME=P/'runtime';commands=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def run(n,c):
 write('phase.json',dict(phase=n,startedAt=time.time()));start=time.monotonic()
 with (P/(n+'.log')).open('x') as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT)
 commands.append(dict(name=n,command=c,exitCode=r.returncode,seconds=time.monotonic()-start));write('commands.json',commands)
 print(n,r.returncode,flush=True);assert r.returncode==0,(n,r.returncode)
def clone_tree(src,dst):
 clone=ctypes.CDLL(None,use_errno=True).clonefile;clone.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int];dst.mkdir()
 for parent,dirs,files in os.walk(src,followlinks=False):
  relative=Path(parent).relative_to(src)
  for n in dirs[:]:
   a,b=Path(parent)/n,dst/relative/n
   if a.is_symlink():b.symlink_to(os.readlink(a));dirs.remove(n)
   else:b.mkdir()
  for n in files:
   a,b=Path(parent)/n,dst/relative/n
   if a.is_symlink():b.symlink_to(os.readlink(a))
   elif clone(os.fsencode(a),os.fsencode(b),0):raise OSError(ctypes.get_errno(),str(a))
def difference(a,b):
 with Image.open(a) as x,Image.open(b) as y:
  x=x.convert('RGBA');y=y.convert('RGBA');
  if x.size!=y.size:return dict(dimensionsMatch=False,sourceSize=list(x.size),candidateSize=list(y.size),changedPixels=None,differenceBounds=None)
  delta=ImageChops.difference(x,y);mask=delta.getchannel('R')
  for channel in ['G','B','A']:mask=ImageChops.lighter(mask,delta.getchannel(channel))
  return dict(dimensionsMatch=True,changedPixels=x.width*x.height-mask.histogram()[0],differenceBounds=mask.getbbox())
try:
 assert json.loads((BUILD/'result.json').read_text())['exitCode']==0
 inputs=json.loads((BUILD/'inputs.json').read_text());frozen=inputs['sourceFiles']
 assert all(sha(ROOT/n)==h for n,h in frozen.items())
 RUNTIME.mkdir();clone_tree(BUILD/'output/package/install',RUNTIME/'install');(RUNTIME/'consumer-build').mkdir()
 shutil.copy2(BUILD/'output/package/consumer-build/InstalledConsumer',RUNTIME/'consumer-build/InstalledConsumer')
 (RUNTIME/'offscreen').mkdir()
 write('inputs.json',dict(inputs,driverSha256=sha(P/'run.py'),producer=str(BUILD),runtimePackageFiles={str(f.relative_to(RUNTIME)):sha(f) for f in sorted(RUNTIME.rglob('*')) if f.is_file()},sourceFreeRuntime=True))
 runtime=DOCKER+['run','--init','--rm','--ulimit','core=0','-v',str(RUNTIME)+':/package','-w','/package',IMAGE]
 run('source-absence',runtime+['python3','-c','from pathlib import Path; assert not Path("/work").exists() or not any(Path("/work").iterdir()); assert not any(Path(n).exists() for n in ["/package/consumer","/package/src","/package/build","/package/consumer-build/CMakeCache.txt"]); print("Project and producer sources absent")'])
 source={r['name']:r for r in json.loads((SOURCE/'measurements.json').read_text())['profiles']};comparisons=[]
 for dark in [False,True]:
  for scale in [1,1.5]:
   for dpr in [1,2]:
    name=('dark' if dark else 'light')+'-text'+str(scale)+'-dpr'+str(dpr)
    args=['env','QT_QPA_PLATFORM=offscreen','QT_QUICK_BACKEND=software','QT_SCALE_FACTOR='+str(dpr),'./consumer-build/InstalledConsumer','--mobile-shell','--mobile-shell-report','/package/offscreen/'+name,'--text-scale',str(scale)]
    if dark:args.append('--dark')
    run('mobile-shell-'+name,runtime+args)
    report=json.loads((RUNTIME/'offscreen'/(name+'.json')).read_text());assert report['geometryPassed']==18
    for row in report['layouts']:
     native=source[row['name']];capture=RUNTIME/'offscreen'/row['capture'];reference=SOURCE/(row['name']+'.png')
     comparisons.append(dict(context=name,profile=row['name'],source=row['name']+'.png',capture=row['capture'],sha256=sha(capture),sourceSha256=sha(reference),geometryPassed=row['geometryPassed'],**difference(reference,capture),accepted=False))
    write('comparison.json',dict(rows=comparisons,rawPixels=True,pixelTolerance=0,accepted=False))
 original=(ROOT/'scripts/check-display-sessions.sh').read_text();loop=next(line for line in original.splitlines() if line.strip().startswith('for fixture in '));focused=original.replace(loop,'    for fixture in mobile-shell; do',1)
 (RUNTIME/'check-mobile-shell-display.sh').write_text(focused)
 environment=json.loads((BASE/'qt-software-final-image-v2/output/artifacts/linux/environment.json').read_text());environment.update(candidateSourceFiles=frozen,sourceBase=inputs['sourceBase'],uncommittedCandidate=True)
 (RUNTIME/'environment.json').write_text(json.dumps(environment,indent=2)+'\n')
 write('display-harness.json',dict(source='scripts/check-display-sessions.sh',sourceSha256=sha(ROOT/'scripts/check-display-sessions.sh'),focusedSha256=sha(RUNTIME/'check-mobile-shell-display.sh'),originalLoop=loop,replacementLoop='    for fixture in mobile-shell; do',otherChanges=False))
 run('mobile-shell-display',runtime+['bash','check-mobile-shell-display.sh'])
 assert all(sha(ROOT/n)==h for n,h in frozen.items())
 write('result.json',dict(exitCode=0,sourceFreeContexts=8,bodyCaptures=len(comparisons),bodyGeometryPassed=sum(r['geometryPassed'] for r in comparisons),exactPixels=sum(r['changedPixels']==0 for r in comparisons),pixelDimensionFailures=sum(not r['dimensionsMatch'] for r in comparisons),virtualDisplayContexts=8,physicalDisplay=False,readerAcceptance=False,accepted=False,fullMirrorAccepted=False))
 write('phase.json',dict(phase='complete',finishedAt=time.time()))
except BaseException as e:
 write('result.json',dict(exitCode=1,error=repr(e),accepted=False));raise
