from pathlib import Path
import hashlib,json
from PIL import Image,ImageChops
p=Path(__file__).resolve().parent;root=p.parents[2];base=p.parent
old=base/'mobile-shell-runtime-v3';native=root/'evidence/reference-investigations/mobile-shell-slots-20261019/run-v2/output'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def changed(a,b):
 with Image.open(a)as x,Image.open(b)as y:
  x=x.convert('RGBA');y=y.convert('RGBA')
  assert x.size==y.size,(a,b,x.size,y.size)
  delta=ImageChops.difference(x,y);mask=delta.getchannel('R')
  for channel in ['G','B','A']:mask=ImageChops.lighter(mask,delta.getchannel(channel))
  return dict(changedPixels=x.width*x.height-mask.histogram()[0],bounds=mask.getbbox())
new_inputs=json.loads((p/'inputs.json').read_text());old_inputs=json.loads((old/'inputs.json').read_text())
assert new_inputs['sourceFiles']==old_inputs['sourceFiles']
assert new_inputs['runtimePackageFiles']==old_inputs['runtimePackageFiles']
assert sha(p/'runtime/consumer-build/InstalledConsumer')==sha(old/'runtime/consumer-build/InstalledConsumer')
before={(r['context'],r['profile']):r for r in json.loads((old/'comparison.json').read_text())['rows']}
rows=[]
for row in json.loads((p/'comparison.json').read_text())['rows']:
 previous=before[(row['context'],row['profile'])]
 source=native/row['source'];a=old/'runtime/offscreen'/previous['capture'];b=p/'runtime/offscreen'/row['capture']
 assert sha(source)==row['sourceSha256']==previous['sourceSha256']
 assert sha(a)==previous['sha256'] and sha(b)==row['sha256']
 x=changed(source,a);y=changed(source,b);ab=changed(a,b)
 assert x['changedPixels']==previous['changedPixels'] and y['changedPixels']==row['changedPixels']
 rows.append(dict(context=row['context'],profile=row['profile'],source=row['source'],capture=row['capture'],sourceSha256=sha(source),beforeSha256=sha(a),afterSha256=sha(b),beforeNative=x,afterNative=y,betweenCandidates=ab,byteIdentical=sha(a)==sha(b),accepted=False))
assert len(rows)==144
result=dict(profiles=len(rows),previousExact=sum(r['beforeNative']['changedPixels']==0 for r in rows),experimentalExact=sum(r['afterNative']['changedPixels']==0 for r in rows),improved=sum(r['afterNative']['changedPixels']<r['beforeNative']['changedPixels']for r in rows),regressed=sum(r['afterNative']['changedPixels']>r['beforeNative']['changedPixels']for r in rows),equalMismatchCounts=sum(r['afterNative']['changedPixels']==r['beforeNative']['changedPixels']for r in rows),byteIdenticalToPrevious=sum(r['byteIdentical']for r in rows),sameApplicationPackage=True,independentDecode=True,pixelTolerance=0,comparisonTransforms=False,productSdkChanged=False,accepted=False,rows=rows)
(p/'independent-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k!='rows'},indent=2))
