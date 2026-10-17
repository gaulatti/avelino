from pathlib import Path
import gzip,hashlib,io,json,shutil,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/pill-modifier-20261017'
assert json.loads((B/'pill-sealed-preflight-v2/result.json').read_text())['exitCode']==0
assert not (D/'verification').exists()
for n in [1,2]:
 p=B/f'pill-sealed-preflight-v{n}';q=D/'verification'/p.name;q.mkdir(parents=True)
 for f in p.iterdir():
  if f.is_file():shutil.copy2(f,q/('original-report.json' if f.name=='candidate.json' else f.name))
archive=D/'implementation.tar.gz';data=[]
with tarfile.open(archive) as stream:
 for member in stream.getmembers():
  body=(R/member.name).read_bytes() if member.name=='scripts/verify-pill-modifier-candidate.py' else stream.extractfile(member).read()
  data.append((member.name,body,member.mode))
manifest={};temporary=D/'implementation.updated'
with temporary.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as gz,tarfile.open(fileobj=gz,mode='w') as stream:
 for name,body,mode in data:
  member=tarfile.TarInfo(name);member.size=len(body);member.mode=mode;member.mtime=0;stream.addfile(member,io.BytesIO(body));manifest[name]=dict(sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),mode=mode)
temporary.replace(archive);(D/'implementation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for name in ['check-avelino-pill-sealed-20261017.py','refresh-avelino-pill-verifier-20261017.py']:shutil.copy2(Path('/Users/gaulatti/.codex/tmp')/name,D/'runners'/name)
p=D/'candidate.json';v=json.loads(p.read_text());v['notes'].append('The first sealed-bundle preflight failed because environment install/ prefixes were compared to relative installed paths. The original implementation archive, report, verifier and failure receipt remain under verification/. Preflight two passes after exact path normalization; hashes are unchanged. The implementation archive then records the corrected verifier.')
v['files']={str(f.relative_to(D)):hashlib.sha256(f.read_bytes()).hexdigest() for f in D.rglob('*') if f.is_file() and f.name not in ['candidate.json','README.md']};p.write_text(json.dumps(v,indent=2)+'\n');print('Updated verifier snapshot and preserved both sealed preflights')
