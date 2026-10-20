from pathlib import Path
import hashlib,json,os
p=Path('/result');sdk=Path('/opt/qt');expected=json.loads((p/'product-sdk-files.json').read_text());actual={}
for f in sorted(sdk.rglob('*')):
 if sdk/'share/avelino' in f.parents:continue
 name=str(f.relative_to(sdk))
 if f.is_symlink():actual[name]=dict(type='symlink',target=os.readlink(f))
 elif f.is_file():actual[name]=dict(type='file',bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest())
assert actual==expected,dict(changed=[n for n in expected if actual.get(n)!=expected[n]][:10],added=list(actual.keys()-expected.keys())[:10])
for name in ['provenance.json','features.json']:
 assert (sdk/'share/avelino/qt-software-opacity'/name).read_bytes()==(p/'product-opacity'/name).read_bytes()
record=dict(exitCode=0,sdkEntries=len(actual),exactProductSdkSeed=True,qtQuickSha256=actual['lib/libQt6Quick.so.6.8.3']['sha256'],accepted=False)
(p/'bootstrap-result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
