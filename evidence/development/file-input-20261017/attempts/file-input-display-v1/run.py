from pathlib import Path
import json,subprocess,time,hashlib
p=Path(__file__).resolve().parent;package=p.parent/'file-input-package-pilot-v6'
assert json.loads((package/'result.json').read_text())['exitCode']==0
binary=package/'consumer-build/InstalledConsumer'
(p/'inputs.json').write_text(json.dumps(dict(accepted=False,package=str(package),consumerSha256=hashlib.sha256(binary.read_bytes()).hexdigest()),indent=2)+chr(10))
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(package)+':/package','-v',str(p)+':/display-driver','-w','/package','avelino-toolchain:clipping-qt6.8.3','bash','/display-driver/check-display-sessions-file-input.sh','/display-driver/output']
start=time.monotonic()
with(p/'run.log').open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(accepted=False,command=command,exitCode=result.returncode,seconds=time.monotonic()-start),indent=2)+chr(10));print('FileInput display profiles',result.returncode,flush=True);raise SystemExit(result.returncode)
