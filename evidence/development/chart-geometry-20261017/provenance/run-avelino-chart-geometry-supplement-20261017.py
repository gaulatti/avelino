from pathlib import Path
import hashlib,json,shutil,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';P=B/'charts-geometry-supplement-v1';assert not P.exists();P.mkdir();shutil.copytree(B/'charts-geometry-build-v5/install',P/'install')
for name in ['capture-chart-geometry-cases.py','verify-chart-geometry-source.py','capture-charts.py']:
 p=P/'driver/scripts'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'scripts'/name,p)
shutil.copytree(R/'evidence/reference-investigations/chart-geometry-20261017',P/'driver/evidence/reference-investigations/chart-geometry-20261017')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(P/'inputs.json').write_text(json.dumps({str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file()},indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-charts-geometry-supplement-v1','-v',str(P)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','python3','driver/scripts/capture-chart-geometry-cases.py','install/bin/AvelinoCatalog','captures','--jobs','3'];start=time.monotonic()
with (P/'run.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(P.name,r.returncode);print((P/'run.log').read_text()[-2200:]);raise SystemExit(r.returncode)
