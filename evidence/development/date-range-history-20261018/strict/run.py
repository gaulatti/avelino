import json,subprocess,time
from pathlib import Path
p=Path(__file__).resolve().parent;r=p.parents[2]
py=r/'artifacts/resumed-avelino-20261016/date-range-visual-venv/bin/python'
reports=sorted((p.parent/'date-range-package-v3/runtime/output').glob('*.json'));reports=[f for f in reports if not f.name.startswith('gallery-')];assert len(reports)==8
cmd=[str(py),str(r/'scripts/compare-date-range-captures.py'),'--output',str(p/'output')]
for f in reports:cmd+=['--report',str(f)]
start=time.monotonic()
with(p/'strict.log').open('w')as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
(p/'commands.json').write_text(json.dumps([dict(name='strict-original-captures',command=cmd,exitCode=result.returncode,seconds=time.monotonic()-start)],indent=2)+'\n')
print('Strict comparison exit',result.returncode,flush=True)
