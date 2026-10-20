from pathlib import Path
import json,subprocess,sys,time
p=Path(__file__).resolve().parent;producer=p.parent/'date-literal-date-replay-v1'
while not (producer/'literal-validation.json').exists():
 if (producer/'result.json').exists() and json.loads((producer/'result.json').read_text())['exitCode']!=0:raise SystemExit('Date replay failed; display not started')
 (p/'phase.json').write_text(json.dumps(dict(phase='waiting for verified package/date replay',observedAt=time.time()))+'\n');time.sleep(10)
assert json.loads((producer/'literal-validation.json').read_text())['checks']==128
(p/'phase.json').write_text(json.dumps(dict(phase='complete eight-profile date display gate'))+'\n')
raise SystemExit(subprocess.call([sys.executable,str(p/'display.py')]))
