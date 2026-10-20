from pathlib import Path
import hashlib,json,subprocess,time
from PIL import Image,ImageChops
p=Path(__file__).resolve().parent;base=p.parent;commands=[]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def write(n,v):(p/n).write_text(json.dumps(v,indent=2)+'\n')
assert json.loads((base/'qt-rectangle-core-v1/result.json').read_text())['exitCode']==0
image=json.loads((base/'qt-rectangle-sdk-v2/image.json').read_text())['imageId']
write('inputs.json',dict(files={n:sha(p/n)for n in ['qt-software-rectangle.cpp','check-qt-software-rectangle.sh','run.py']},applicationSourcesUsed=False,reference='QPainter floating rectangles; no native mirror baseline replaced',accepted=False))
try:
 for label,sdk,expected in [('baseline','sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3',1),('patched',image,0)]:
  out=p/label;out.mkdir()
  command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(p)+':/probe:ro','-v',str(out)+':/result',sdk,'bash','/probe/check-qt-software-rectangle.sh','/result/captures',str(expected)]
  write('phase.json',dict(phase=label,startedAt=time.time()))
  start=time.monotonic()
  with(p/(label+'.log')).open('x')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  commands.append(dict(label=label,imageId=sdk,command=command,exitCode=r.returncode,seconds=time.monotonic()-start));write('commands.json',commands)
  print(label,r.returncode,flush=True);assert r.returncode==0,(label,r.returncode)
 rows=[]
 for platform in ['xcb','wayland']:
  for dpr in [1,2]:
   label=f'{platform}-dpr{dpr}';a=p/'baseline/captures'/label;b=p/'patched/captures'/label
   before=json.loads((a/'result.json').read_text());after=json.loads((b/'result.json').read_text())
   for x,y in zip(before['frames'],after['frames'],strict=True):
    assert all(x[k]==y[k]for k in ['index','kind','shift','height','actualRect'])
    assert sha(a/x['capture'])==x['sha256'] and sha(b/y['capture'])==y['sha256']
    if x['kind']==0:
     assert (a/x['reference']).read_bytes()==(b/y['reference']).read_bytes()
     def mismatch(directory,row):
      with Image.open(directory/row['capture'])as z,Image.open(directory/row['reference'])as ref:
       z=z.convert('RGBA');ref=ref.convert('RGBA');assert z.size==ref.size
       delta=ImageChops.difference(z,ref);mask=delta.getchannel('R')
       for channel in ['G','B','A']:mask=ImageChops.lighter(mask,delta.getchannel(channel))
       return z.width*z.height-mask.histogram()[0]
     old,new=mismatch(a,x),mismatch(b,y)
     assert old==x['changedPixels'] and new==y['changedPixels']==0
     rows.append(dict(profile=label,index=x['index'],kind=0,beforeMismatch=old,afterMismatch=new,referenceIdentical=True))
    else:
     assert (a/x['capture']).read_bytes()==(b/y['capture']).read_bytes()
     rows.append(dict(profile=label,index=x['index'],kind=x['kind'],byteIdentical=True))
 assert len(rows)==480
 result=dict(exitCode=0,rows=rows,frames=480,floatingReferences=120,baselineMismatches=sum(r.get('beforeMismatch',0)>0 for r in rows),patchedMismatches=0,legacyByteIdentical=sum(r.get('byteIdentical',False)for r in rows),productSdkChanged=False,nativeAcceptance=False,accepted=False)
 write('comparison.json',result);write('result.json',{k:v for k,v in result.items()if k!='rows'});print(json.dumps({k:v for k,v in result.items()if k!='rows'},indent=2))
except BaseException as e:
 write('result.json',dict(exitCode=1,error=repr(e),accepted=False));raise
