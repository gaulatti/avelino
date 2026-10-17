from pathlib import Path
import json,os,subprocess,time
p=Path('/package');rows=[]
commands=[(['bash','check-installed.sh'],0),(['python3','driver/scripts/capture-pill-modifier-cases.py','consumer-build/InstalledConsumer','captures','--jobs','2'],0),(['consumer-build/InstalledConsumer','--pill-modifier','--pill-report','/package/strict'],1)]
for i,(command,expected) in enumerate(commands):
 start=time.monotonic()
 with (p/f'{i}.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'))
 rows.append(dict(command=command,exitCode=r.returncode,expectedExitCode=expected,seconds=time.monotonic()-start,log=f'{i}.log'))
 (p/'steps.json').write_text(json.dumps(rows,indent=2)+'\n');print(i,r.returncode,flush=True)
 if r.returncode!=expected:raise SystemExit(1)
