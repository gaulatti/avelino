from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parent
image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3'
command=['docker','--context','colima-avelino-verify','build','--pull=false','-t',image,str(p)]
start=time.monotonic()
with(p/'build.log').open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
x=dict(accepted=False,exitCode=result.returncode,command=command,seconds=time.monotonic()-start)
if result.returncode==0:x['imageId']=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
(p/'result.json').write_text(json.dumps(x,indent=2)+'\n');print('Weston13.0.4 image',result.returncode,flush=True);raise SystemExit(result.returncode)
