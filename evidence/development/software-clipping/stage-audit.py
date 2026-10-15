import hashlib,json,subprocess
from pathlib import Path
root=Path('evidence/development/software-clipping');value=json.loads((root/'candidate.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in value['files'].items():assert sha(root/name)==digest,name
current=json.loads((root/'build-environment.json').read_text())['sourceInputs']
for path,digest in current.items():assert sha(Path(path))==digest,path
for path in [str(root/'candidate.json')]+[str(root/name) for name in value['files']]+list(current):
 staged=subprocess.check_output(['git','show',':'+path]);assert hashlib.sha256(staged).hexdigest()==sha(Path(path)),path
print('Verified',len(value['files']),'sealed evidence files and',len(current),'source inputs against working tree and staged index')
