from pathlib import Path
import json,subprocess,sys,time
p=Path(__file__).resolve().parent;producer=p.parent/'date-literal-qt-v2'
while not (producer/'result.json').exists():
 (p/'phase.json').write_text(json.dumps(dict(phase='waiting for Qt producer',observedAt=time.time()))+'\n');time.sleep(10)
assert json.loads((producer/'result.json').read_text())['exitCode']==0
diagnostic=p.parent/'date-literal-gl-fixed-v1/result.json'
while not diagnostic.exists():time.sleep(5)
assert json.loads(diagnostic.read_text())['exitCode']==0
(p/'phase.json').write_text(json.dumps(dict(phase='building independent consumer150'))+'\n')
raise SystemExit(subprocess.call([sys.executable,str(p/'package.py'),producer.name]))
