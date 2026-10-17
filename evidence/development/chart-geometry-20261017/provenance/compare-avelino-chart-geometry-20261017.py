from pathlib import Path
import hashlib,json,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016'
for name,script,prior in [('charts-geometry-comparison-v1','compare-chart-captures.py','charts-geometry-package-final-v1'),('charts-geometry-supplement-comparison-v1','compare-chart-geometry-captures.py','charts-geometry-supplement-v1')]:
 assert json.loads((B/prior/'result.json').read_text())['exitCode']==0
 P=B/name;assert not P.exists();P.mkdir();command=['/private/tmp/avelino-resume-visuals-20261015/bin/python','scripts/'+script,str(B/prior/'captures'),str(P/'results')];start=time.monotonic()
 with (P/'run.log').open('w') as log:r=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 (P/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(name,r.returncode,flush=True);print((P/'run.log').read_text()[-1800:]);assert r.returncode==1
