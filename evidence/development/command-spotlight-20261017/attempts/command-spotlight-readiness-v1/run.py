from pathlib import Path
import json,os,subprocess,time
p=Path('/package');steps=[]
for index,command in enumerate(json.loads((p/'commands.json').read_text())):
 start=time.monotonic()
 with (p/(str(index)+'.log')).open('w')as log:r=subprocess.run(command,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'),stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,log=str(index)+'.log'));(p/'steps.json').write_text(json.dumps(steps,indent=2)+'\n');print(index,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
