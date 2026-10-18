from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;package=p.parent/'file-input-go-to-package-v2'
assert json.loads((package/'result.json').read_text())['exitCode']==0
inputs=json.loads((package/'inputs.json').read_text());(p/'inputs.json').write_text(json.dumps(dict(accepted=False,package=package.name,consumerSha256=inputs['consumerSha256'],packageFiles=inputs['packageFiles'],image=inputs['image'],imageId=inputs['imageId']),indent=2)+'\n')
# Only the installed prefix, independently built ELF and runtime records are mounted.
(package/'runtime/environment.json').write_text(json.dumps(dict(accepted=False,qt='6.8.3',producer='file-input-qt-v60',image=inputs['image'],imageId=inputs['imageId'],physicalDisplay=False,physicalInput=False),indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(package/'runtime')+':/consumer-check','-v',str(p)+':/display-driver','-w','/consumer-check',inputs['image'],'python3','-c',"from pathlib import Path; import os; assert not Path('/work/src/Avelino').exists(); assert not Path('/consumer-check/consumer').exists(); assert not Path('/consumer-check/consumer-build/CMakeCache.txt').exists(); os.execv('/bin/bash',['bash','/display-driver/check-display-sessions-file-input.sh','/display-driver/output'])"]
start=time.monotonic()
with(p/'run.log').open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(accepted=False,command=command,exitCode=result.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print('Final FileInput display profiles',result.returncode,flush=True);raise SystemExit(result.returncode)
