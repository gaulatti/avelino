from pathlib import Path
import hashlib,json,subprocess,time,shutil
p=Path(__file__).resolve().parent;prefix=p.parent/'navigation-cjk-package-v2/runtime/install'
image='avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3'
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/consumer-check','-v',str(prefix)+':/consumer-check/install:ro','-w','/consumer-check',image]
steps=[]
def run(name,command):
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=command,exitCode=r.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,r.returncode,flush=True)
 return r.returncode
for name,args in [('configure',['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/consumer-check/install;/opt/qt']),('build',['cmake','--build','consumer-build','--parallel','2'])]:
 if run(name,base+args):raise SystemExit(1)
(p/'runtime/consumer-build').mkdir();shutil.copy2(p/'consumer-build/InstalledConsumer',p/'runtime/consumer-build/InstalledConsumer')
inputs=json.loads((p/'inputs.json').read_text());inputs['consumerSha256']=hashlib.sha256((p/'runtime/consumer-build/InstalledConsumer').read_bytes()).hexdigest();(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p/'runtime')+':/display-check','-v',str(prefix)+':/display-check/install:ro','-w','/display-check',image,'bash','check.sh','/display-check/output']
result=run('case',command);(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result,profile='file-input-wayland-opengl-scaled',diagnosticOnly=True),indent=2)+'\n')
raise SystemExit(result)
