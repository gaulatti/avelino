from pathlib import Path
import subprocess,time,json
p=Path(__file__).resolve().parent;r=p.parents[2];tag='avelino-toolchain:weston13-popup-parent-v1-20261018-qt6.8.3'
command=['docker','--context','colima-avelino-verify','build','--progress=plain','-f',str(p/'Dockerfile'),'-t',tag,str(r)]
start=time.monotonic()
with(p/'build.log').open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
record=dict(accepted=False,command=command,exitCode=result.returncode,seconds=time.monotonic()-start,image=tag)
if result.returncode==0:record['imageId']=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',tag,'--format','{{.Id}}'],text=True).strip()
(p/'result.json').write_text(json.dumps(record,indent=2)+'\n');print('Patched toolchain image',result.returncode)
raise SystemExit(result.returncode)
