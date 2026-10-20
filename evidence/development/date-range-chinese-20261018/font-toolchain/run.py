from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent
parent=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect','avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3','--format','{{.Id}}'],text=True).strip()
assert parent=='sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8'
tag='avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3'
cmd=['docker','--context','colima-avelino-verify','build','--progress=plain','-t',tag,str(p)]
start=time.monotonic()
with(p/'build.log').open('w')as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
(p/'commands.json').write_text(json.dumps([dict(command=cmd,exitCode=r.returncode,seconds=time.monotonic()-start)],indent=2)+'\n');print('CJK toolchain build',r.returncode,flush=True)
if r.returncode:raise SystemExit(r.returncode)
identity=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',tag,'--format','{{.Id}}'],text=True).strip()
(p/'result.json').write_text(json.dumps(dict(accepted=False,parentImageId=parent,image=tag,imageId=identity,exitCode=0,dockerfileSha256=hashlib.sha256((p/'Dockerfile').read_bytes()).hexdigest()),indent=2)+'\n')
