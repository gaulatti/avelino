from pathlib import Path
import json,subprocess,sys,time
p=Path(__file__).resolve().parent;source=p.parent/'date-literal-package-v2'
while not (source/'result.json').exists():time.sleep(5)
assert json.loads((source/'result.json').read_text())['exitCode']==0
raise SystemExit(subprocess.call([sys.executable,str(p/'replay.py')]))
