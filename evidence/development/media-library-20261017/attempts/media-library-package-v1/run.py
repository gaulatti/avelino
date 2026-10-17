from pathlib import Path
import json,os,subprocess,time
p=Path('/package');rows=[]
commands=[['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'],
 ['cmake','--build','consumer-build','--parallel','2'],
 ['consumer-build/InstalledConsumer','--media-library','--media-library-observe','--media-library-report','/package/results/media-library'],
 ['consumer-build/InstalledConsumer','--radio-group'],
 ['consumer-build/InstalledConsumer','--selection']]
for i,c in enumerate(commands):
 start=time.monotonic()
 with (p/f'{i}.log').open('w') as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'))
 rows.append(dict(command=c,exitCode=r.returncode,seconds=time.monotonic()-start,log=f'{i}.log'))
 (p/'steps.json').write_text(json.dumps(rows,indent=2)+'\n');print(i,r.returncode,flush=True)
 if i<2 and r.returncode:raise SystemExit(r.returncode)
raise SystemExit(1 if any(r['exitCode'] for r in rows) else 0)
