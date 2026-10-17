from pathlib import Path
import json,os,subprocess,time
p=Path('/package');rows=[]
commands=[(['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'],0),(['cmake','--build','consumer-build','--parallel','2'],0),(['python3','driver/scripts/capture-app-tabs.py','consumer-build/InstalledConsumer','captures','--jobs','2'],0),(['consumer-build/InstalledConsumer','--app-tabs','--app-tabs-report','/package/strict'],1),(['install/bin/AvelinoCatalog','--fixture','app-tabs','--capture','/package/gallery.png'],0)]
for i,(c,expected)in enumerate(commands):
 start=time.monotonic()
 with (p/(str(i)+'.log')).open('w')as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'))
 rows.append(dict(command=c,exitCode=r.returncode,expectedExitCode=expected,seconds=time.monotonic()-start,log=str(i)+'.log'));(p/'steps.json').write_text(json.dumps(rows,indent=2)+'\n');print(i,r.returncode,flush=True)
 if r.returncode!=expected:raise SystemExit(1)
