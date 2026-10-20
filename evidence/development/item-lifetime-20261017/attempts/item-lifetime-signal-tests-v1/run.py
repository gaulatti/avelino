from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work','-w','/work/'+str(p.relative_to(r)),'--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','avelino-toolchain:data-metrics-qt6.8.3'];steps=[]
for name,command in [('configure',['cmake','-S','.','-B','build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug']),('build',['cmake','--build','build','--parallel','2'])]+[('tests-dpr'+str(dpr),['env','QT_SCALE_FACTOR='+str(dpr),'./build/LifetimeTests'])for dpr in [1,2]]:
 start=time.monotonic()
 with(p/(name+'.log')).open('wb')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+chr(10));print(name,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0),indent=2)+chr(10))
