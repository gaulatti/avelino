from pathlib import Path
import hashlib,json,subprocess
root=Path('evidence/development/data-metrics')
value=json.loads((root/'candidate.json').read_text())
files={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
assert files==set(value['files'])|{'candidate.json'}
for name,digest in value['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
frozen=json.loads((root/'frozen-inputs.json').read_text())
for name,digest in frozen.items():
 blob=subprocess.check_output(['git','show',':'+name]);assert hashlib.sha256(blob).hexdigest()==digest,name
for label in ['build-environment.json','captures/environment.json','sessions/environment.json','host-styles/environment.json','installed-catalog/environment.json','catalog/environment.json']:
 assert json.loads((root/label).read_text())['sourceInputs']==frozen,label
print('Index matches all',len(frozen),'frozen inputs;',len(value['files']),'sealed evidence files verified')

supplement=json.loads((root/'supplemental-test-inputs.json').read_text())
for name,digest in supplement['additionalTestInputs'].items():
 blob=subprocess.check_output(['git','show',':'+name]);assert hashlib.sha256(blob).hexdigest()==digest,name
assert len(supplement['currentInputSnapshot'])==len(frozen)+len(supplement['additionalTestInputs'])==294
assert set(supplement['currentInputSnapshot'])==set(frozen)|set(supplement['additionalTestInputs'])
print('Supplemental native oracle and all 294 current test inputs accounted for')
