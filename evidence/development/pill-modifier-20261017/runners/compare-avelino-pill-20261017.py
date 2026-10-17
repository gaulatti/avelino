from pathlib import Path
import json,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016';p=base/'pill-comparison-v1';assert not p.exists();p.mkdir()
command=['/private/tmp/avelino-resume-visuals-20261015/bin/python','scripts/compare-pill-modifier-captures.py',str(base/'pill-package-final-v1/captures'),str(p/'comparison')]
start=time.monotonic()
with (p/'run.log').open('w') as log:r=subprocess.run(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n')
print(p.name,r.returncode);print((p/'run.log').read_text()[-3000:]);raise SystemExit(r.returncode)
