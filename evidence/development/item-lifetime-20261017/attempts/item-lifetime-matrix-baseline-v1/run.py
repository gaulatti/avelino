from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2]
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work','-w','/work/'+str(p.relative_to(r)),'--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','avelino-toolchain:data-metrics-qt6.8.3'];steps=[]
commands=[('configure',['cmake','-S','.','-B','build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug']),('build',['cmake','--build','build','--parallel','2'])]+[('repro-'+name+'-'+str(i),['./build/Repro',name,str(i)])for name in ['inherited','radio','row','column','overlay','tabs','charts','spotlight','media','mask']for i in range(4)]
for name,command in commands:
 with(p/(name+'.log')).open('wb')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+command,exitCode=result.returncode));(p/'commands.json').write_text(json.dumps(steps,indent=2)+chr(10));print(name,result.returncode,flush=True)
 if name in ['configure','build']and result.returncode:raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,repros={s['name']:s['exitCode']for s in steps if s['name'].startswith('repro-')}),indent=2)+chr(10))
