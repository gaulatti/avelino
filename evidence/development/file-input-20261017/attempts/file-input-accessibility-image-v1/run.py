from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parent;command=['docker','--context','colima-avelino-verify','build','-t','avelino-toolchain:file-input-a11y-v1-qt6.8.3','-f',str(p/'Dockerfile'),str(p)];start=time.monotonic()
with(p/'build.log').open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
record=dict(accepted=False,command=command,exitCode=result.returncode,seconds=time.monotonic()-start)
if result.returncode==0:record['imageId']=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect','avelino-toolchain:file-input-a11y-v1-qt6.8.3','--format','{{.Id}}'],text=True).strip()
(p/'result.json').write_text(json.dumps(record,indent=2)+chr(10));print(record,flush=True);raise SystemExit(result.returncode)
