from pathlib import Path
import json,subprocess,time,shutil
p=Path(__file__).resolve().parent;prefix=p.parent/'date-literal-package-v1/runtime/install';image='avelino-toolchain:weston13-popup-parent-v2-20261018-qt6.8.3';steps=[]
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/consumer-check','-v',str(prefix)+':/consumer-check/install:ro','-w','/consumer-check',image]
def run(name,command):
 t=time.monotonic()
 with(p/(name+'.log')).open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=command,exitCode=r.returncode,seconds=time.monotonic()-t));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,r.returncode,flush=True)
 return r.returncode
if run('build',base+['bash','-c','touch consumer/daterangechecks.h && cmake --build consumer-build --parallel 2']):raise SystemExit(1)
shutil.copy2(p/'consumer-build/InstalledConsumer',p/'runtime/consumer-build/InstalledConsumer')
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p/'runtime')+':/display-check','-v',str(prefix)+':/display-check/install:ro','-w','/display-check',image,'bash','check.sh','/display-check/output']
code=run('case',command);(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=code,diagnosticOnly=True),indent=2)+'\n')
