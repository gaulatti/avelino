from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
r=Path('/Users/gaulatti/source/gaulatti/avelino');p=r/'artifacts/resumed-avelino-20261016'/sys.argv[1];assert not p.exists();p.mkdir()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
shutil.copy2(r/'scripts/verify-pill-modifier-candidate.py',p/'verifier.py')
(p/'inputs.json').write_text(json.dumps(dict(verifierSha256=sha(p/'verifier.py'),candidateSha256=sha(r/'evidence/development/pill-modifier-20261017/candidate.json')),indent=2)+'\n')
command=['/private/tmp/avelino-resume-visuals-20261015/bin/python','scripts/verify-pill-modifier-candidate.py'];start=time.monotonic()
with (p/'run.log').open('w') as log:v=subprocess.run(command,cwd=r,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=command,exitCode=v.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(p.name,v.returncode);print((p/'run.log').read_text()[-3000:]);raise SystemExit(v.returncode)
