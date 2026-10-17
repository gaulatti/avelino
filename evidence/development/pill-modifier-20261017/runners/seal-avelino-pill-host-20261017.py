from pathlib import Path
import gzip,hashlib,io,json,re,shutil,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');H=R/'artifacts/resumed-avelino-20261016/pill-host-v1';D=R/'evidence/development/pill-modifier-20261017'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((H/'results.json').read_text());assert rows and all(r['exitCode']==0 for r in rows)
inputs=json.loads((H/'inputs.json').read_text());assert all(sha(R/n)==v for n,v in inputs.items())
contract=next(r for r in rows if 'unittest' in r['command']);text=(H/contract['log']).read_text();assert re.search(r'Ran 518 tests in .*\n\nOK',text),text[-500:]
files={p.name:p for p in H.iterdir() if p.is_file()};files['runner.py']=Path('/Users/gaulatti/.codex/tmp/validate-avelino-pill-20261017.py')
assert sum(p.stat().st_size for p in files.values())<60*1024*1024
manifest={};out=D/'host-validation.tar.gz'
with out.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as gz,tarfile.open(fileobj=gz,mode='w') as archive:
 for name,p in sorted(files.items()):
  data=p.read_bytes();info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;info.mtime=0;archive.addfile(info,io.BytesIO(data));manifest[name]=dict(sha256=sha(p),bytes=len(data),mode=info.mode)
(D/'host-validation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(D/'host').mkdir();shutil.copy2(H/'inputs.json',D/'host/inputs.json');shutil.copy2(H/'results.json',D/'host/results.json')
p=D/'candidate.json';report=json.loads(p.read_text());report['archives']['hostValidation']=dict(archive=out.name,manifest='host-validation-manifest.json',files=len(manifest));report['validation']['hostCommands']=len(rows);report['validation']['hostContractTests']=518
report['files']={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ['README.md','candidate.json']};(D/'candidate.json').write_text(json.dumps(report,indent=2)+'\n')
print('Sealed',len(rows),'host commands and 518 contract tests')
