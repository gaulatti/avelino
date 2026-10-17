from pathlib import Path
import hashlib,json,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016';prior=base/'charts-package-final-v1'
while not (prior/'result.json').exists():time.sleep(.25)
assert json.loads((prior/'result.json').read_text())['exitCode']==0
p=base/'charts-comparison-v1';assert not p.exists();p.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(p/'inputs.json').write_text(json.dumps(dict(scripts={n:sha(root/n) for n in ['scripts/capture-charts.py','scripts/compare-chart-captures.py','scripts/compare-captures.py']},capturesSha256=sha(prior/'captures/capture-results.json')),indent=2)+'\n')
command=['/private/tmp/avelino-resume-visuals-20261015/bin/python','scripts/compare-chart-captures.py',str(prior/'captures'),str(p/'results')];start=time.monotonic()
with (p/'run.log').open('w') as log:r=subprocess.run(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n')
print('Chart strict comparison:',r.returncode);print((p/'run.log').read_text()[-2200:]);raise SystemExit(r.returncode)
