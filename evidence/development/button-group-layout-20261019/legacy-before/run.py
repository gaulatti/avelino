from pathlib import Path
import hashlib,json,subprocess,time
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent;ROOT=P.parents[2];BASE=P.parent
OLD=BASE/'qt-software-final-image-v2/output/artifacts/package/install'
NEW=BASE/'button-group-compiled-v6/output/artifacts'
SOURCE=ROOT/'evidence/reference-investigations/button-group-slots-20261019/canonical'
IMAGE='sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def pixels(a,b):
 with Image.open(a) as x,Image.open(b) as y:
  x=x.convert('RGBA');y=y.convert('RGBA');assert x.size==y.size
  diff=ImageChops.difference(x,y);mask=diff.getchannel('R')
  for c in ['G','B','A']:mask=ImageChops.lighter(mask,diff.getchannel(c))
  return x.width*x.height-mask.histogram()[0]
commands=[];rows=[]
try:
 assert json.loads((BASE/'button-group-continuation-v3/result.json').read_text())['exitCode']==0
 output=P/'output';output.mkdir()
 fixture=ROOT/'evidence/reference-proposals/desktop-20261012/fixtures.json'
 (output/'fixtures.json').write_bytes(fixture.read_bytes())
 frozen={str(p.relative_to(OLD)):sha(p) for p in sorted(OLD.rglob('*')) if p.is_file()}
 write('inputs.json',dict(imageId=IMAGE,installedBaselineFiles=frozen,sourceFree=True,fixtureSha256=sha(fixture),accepted=False))
 for dark in [False,True]:
  for scale in [1,1.5]:
   for dpr in [1,2]:
    context=('dark' if dark else 'light')+'-text'+str(scale)+'-dpr'+str(dpr)
    name='button-group-'+('dark' if dark else 'light')+'-text'+format(scale,'.1f')+'-offscreen-dpr'+format(dpr,'.1f')+'.png'
    command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(OLD)+':/package/install:ro','-v',str(output)+':/probe','-w','/package','-e','QT_QPA_PLATFORM=offscreen','-e','QT_QUICK_BACKEND=software','-e','QT_SCALE_FACTOR='+str(dpr),IMAGE,'./install/bin/AvelinoCatalog','--fixture','reference-case','--case','button-group','--case-definitions','/probe/fixtures.json','--text-scale',str(scale),'--capture','/probe/'+name]
    if dark:command.append('--dark')
    with (P/(context+'.log')).open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
    commands.append(dict(context=context,command=command,exitCode=r.returncode));write('commands.json',commands)
    assert r.returncode==0,(context,r.returncode)
    before=pixels(SOURCE/name,output/name);after=pixels(SOURCE/name,NEW/(context+'.png'))
    rows.append(dict(context=context,source=name,before=name,after=context+'.png',beforeSha256=sha(output/name),afterSha256=sha(NEW/(context+'.png')),beforeChangedPixels=before,afterChangedPixels=after,worse=after>before,accepted=False))
 write('comparison.json',dict(rows=rows,pixelTolerance=0,accepted=False))
 assert all(sha(OLD/n)==h for n,h in frozen.items())
 write('result.json',dict(exitCode=0,contexts=8,improved=sum(r['afterChangedPixels']<r['beforeChangedPixels'] for r in rows),worse=sum(r['worse'] for r in rows),oldExact=sum(r['beforeChangedPixels']==0 for r in rows),newExact=sum(r['afterChangedPixels']==0 for r in rows),installedBaselineUnchanged=True,accepted=False,fullMirrorAccepted=False))
except BaseException as e:
 write('result.json',dict(exitCode=1,error=repr(e),accepted=False));raise
