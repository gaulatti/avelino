from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work','-w','/work/'+str(p.relative_to(r))+'/source','avelino-toolchain:data-metrics-qt6.8.3','cmake','--build','../build','--target','Avelino','--parallel','2'];start=time.monotonic()
with(p/'module-build.log').open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'module-command.json').write_text(json.dumps(dict(command=command,exitCode=result.returncode,seconds=time.monotonic()-start),indent=2)+'\n');(p/'module-result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode),indent=2)+'\n');print('module-build',result.returncode)
