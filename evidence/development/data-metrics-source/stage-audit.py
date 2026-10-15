from pathlib import Path
import hashlib,json,subprocess
root=Path('evidence/development/data-metrics-source');value=json.loads((root/'candidate.json').read_text())
assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}==set(value['files'])|{'candidate.json'}
for name,h in value['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,name
for name,h in value['inputFiles'].items():assert hashlib.sha256(subprocess.check_output(['git','show',':'+name])).hexdigest()==h,name
source=Path('evidence/reference-investigations/data-metrics-20261015');manifest=json.loads((source/'investigation.json').read_text())
for name,h in manifest['files'].items():assert hashlib.sha256(subprocess.check_output(['git','show',':'+str(source/name)])).hexdigest()==h,name
print('All',len(value['files']),'development evidence files,',len(value['inputFiles']),'verifier/test/CI inputs and',len(manifest['files']),'native evidence files match staged bytes')
