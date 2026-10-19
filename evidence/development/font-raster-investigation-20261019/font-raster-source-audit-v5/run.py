from pathlib import Path
import hashlib,json
from collections import Counter
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent
NATIVE=Path('/Users/gaulatti/.codex/tmp/avelino-font-raster-native-20261019-v5/output')
CONTROL=Path('/Users/gaulatti/.codex/tmp/avelino-font-raster-native-20261019-v4/output')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def diff(a,b):
 with Image.open(a) as x,Image.open(b) as y:
  x=x.convert('RGBA');y=y.convert('RGBA');assert x.size==y.size
  d=ImageChops.difference(x,y);m=d.getchannel('R')
  for c in ['G','B','A']:m=ImageChops.lighter(m,d.getchannel(c))
  h=m.histogram();return dict(changedPixels=x.width*x.height-h[0],maxChannelError=max(i for i,n in enumerate(h) if n),errorHistogram={str(i):n for i,n in enumerate(h) if i>0 and n},bounds=m.getbbox())
data=json.loads((NATIVE/'measurements.json').read_text());records=[];controls=0;control_rows=[]
assert len(data['profiles'])==2016
for row in data['profiles']:
 assert (NATIVE/row['bare']).read_bytes()==(NATIVE/row['measured']).read_bytes()
 assert sha(NATIVE/row['bare'])==row['sourceSha256']
 if row['xOffset']==0:
  identical=(NATIVE/row['bare']).read_bytes()==(CONTROL/row['bare']).read_bytes();controls+=identical;control_rows.append(dict(profile=row['name'],byteIdentical=identical,**diff(NATIVE/row['bare'],CONTROL/row['bare'])))
 for variant in row['coreText']:
  assert sha(NATIVE/variant['path'])==variant['sha256']
  records.append(dict(profile=row['name'],mode=variant['mode'],xOffset=row['xOffset'],frame=row['frame'],dpr=row['dpr'],**diff(NATIVE/row['bare'],NATIVE/variant['path'])))
summary={}
for mode in [17,19,20]:
 rows=[r for r in records if r['mode']==mode];summary[str(mode)]=dict(profiles=len(rows),changedPixels=sum(r['changedPixels'] for r in rows),exact=sum(r['changedPixels']==0 for r in rows),profileMaximumErrors=dict(Counter(r['maxChannelError'] for r in rows)))
result=dict(exitCode=0,profiles=2016,transparentMeasurementPairs=2016,unchangedZeroOffsetControls=controls,comparisons=len(records),summary=summary,zeroOffsetControlFailures=288-controls,modelPromoted=False,accepted=False,productSourceChanged=False,existingExpectedImagesChanged=False,fullMirrorAccepted=False)
(P/'controls.json').write_text(json.dumps(dict(rows=control_rows,accepted=False),indent=2)+'\n');(P/'comparison.json').write_text(json.dumps(dict(rows=records,accepted=False),indent=2)+'\n');(P/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
