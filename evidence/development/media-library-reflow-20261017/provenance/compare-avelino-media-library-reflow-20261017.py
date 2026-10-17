from pathlib import Path
import json,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';P=B/'media-library-reflow-package-final-v1';D=B/'media-library-reflow-comparison-v1';assert not D.exists();D.mkdir()
while not (P/'result.json').exists():time.sleep(.25)
assert json.loads((P/'result.json').read_text())['exitCode']==0
command=['/private/tmp/avelino-resume-visuals-20261015/bin/python',str(R/'scripts/compare-media-library-captures.py'),str(P/'captures'),str(D/'results')]
start=time.monotonic()
with (D/'run.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(D/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(r.returncode);print((D/'run.log').read_text()[-2500:]);raise SystemExit(r.returncode)
