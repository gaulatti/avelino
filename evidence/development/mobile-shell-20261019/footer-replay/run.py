from pathlib import Path
import hashlib,json,subprocess,time
P=Path(__file__).resolve().parent;BASE=P.parent;ROOT=P.parents[2]
RUNTIME=BASE/'mobile-shell-runtime-v3/runtime';NATIVE=ROOT/'evidence/reference-investigations/footer-slots-20261019'
OLD=ROOT/'evidence/development/footer-layout-20261019/captures'
IMAGE='sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
commands=[];comparisons=[]
try:
 assert json.loads((BASE/'mobile-shell-runtime-v3/result.json').read_text())['exitCode']==0
 output=P/'output';output.mkdir();(output/'fixtures.json').write_bytes((NATIVE/'fixtures.json').read_bytes())
 inputs=json.loads((BASE/'mobile-shell-runtime-v3/inputs.json').read_text())
 assert all(sha(RUNTIME/n)==h for n,h in inputs['runtimePackageFiles'].items())
 write('inputs.json',dict(imageId=IMAGE,sourceFree=True,producer='mobile-shell-compiled-v7',sourcePackageFiles=inputs['runtimePackageFiles'],previousFooterManifestSha256=sha(ROOT/'evidence/development/footer-layout-20261019/files.json'),accepted=False))
 for i,row in enumerate(json.loads((NATIVE/'captures.json').read_text())['captures']):
  command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(RUNTIME)+':/package:ro','-v',str(output)+':/extra','-w','/package','-e','QT_QPA_PLATFORM=offscreen','-e','QT_QUICK_BACKEND=software','-e','QT_SCALE_FACTOR='+str(row['dpr']),IMAGE,'./install/bin/AvelinoCatalog','--fixture','reference-case','--case',row['fixture'],'--case-definitions','/extra/fixtures.json','--text-scale',str(row['textScale']),'--capture','/extra/'+row['path']]
  if row['appearance']=='dark':command.append('--dark')
  with (P/('catalog-'+str(i).zfill(3)+'.log')).open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  commands.append(dict(command=command,exitCode=r.returncode));write('commands.json',commands)
  assert r.returncode==0,(row['path'],r.returncode)
  capture=output/row['path'];identical=capture.read_bytes()==(OLD/row['path']).read_bytes()
  comparisons.append(dict(path=row['path'],expected=sha(OLD/row['path']),actual=sha(capture),byteIdentical=identical))
  write('comparison.json',dict(rows=comparisons,accepted=False))
  assert identical,row['path']
  if (i+1)%20==0:print('footer captures',i+1,flush=True)
 assert all(sha(RUNTIME/n)==h for n,h in inputs['runtimePackageFiles'].items())
 write('result.json',dict(exitCode=0,captures=120,byteIdentical=120,sourceFree=True,sourcePackageUnchanged=True,physicalDisplay=False,accepted=False,fullMirrorAccepted=False))
except BaseException as e:
 write('result.json',dict(exitCode=1,error=repr(e),accepted=False));raise
