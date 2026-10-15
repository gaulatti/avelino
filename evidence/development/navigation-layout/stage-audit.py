from pathlib import Path
import hashlib,json,subprocess
root=Path('evidence/development/navigation-layout')
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
