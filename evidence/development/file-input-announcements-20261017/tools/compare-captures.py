from pathlib import Path
import hashlib,json
r=Path.cwd();p=r/'artifacts/resumed-avelino-20261016/file-input-announcement-package-v3'
assert json.loads((p/'result.json').read_text())['exitCode']==0
baseline=r/'evidence/development/file-input-20261017/captures'
images=[]
contexts=list((p/'output').glob('*.json'));assert len(contexts)==8
for f in contexts:
 actual=json.loads(f.read_text());expected=json.loads((baseline/f.name).read_text())
 assert actual['closed']==expected['closed'],f.name
 assert actual['sizing']==expected['sizing'],f.name
 for row in actual['closed']:
  name=f.stem+'-'+row['configuration']['id']+'.png'
  current=p/'output'/name
  assert current.read_bytes()==(baseline/name).read_bytes(),name
  images.append(dict(path=name,sha256=hashlib.sha256(current.read_bytes()).hexdigest()))
assert len(images)==256
(p/'visual-binding.json').write_text(json.dumps(dict(accepted=False,baseline=str(baseline.relative_to(r)),pairs=256,byteIdenticalClosedImages=256,closedAndSizingMetadataUnchanged=True,expectedImagesChanged=False,approvedExceptions=[],tolerance='none',records=images),indent=2)+'\n')
print('All 256 closed PNGs and complete closed/sizing metadata unchanged')
