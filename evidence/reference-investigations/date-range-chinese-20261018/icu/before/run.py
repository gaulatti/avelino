from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent
image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3'
image_id=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
assert image_id=='sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8'
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/probe','-w','/probe',image]
steps=[]
for name,args in [('build',['g++','-std=c++17','main.cpp','-licui18n','-licuuc','-licudata','-o','probe']),('format',['./probe'])]:
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:r=subprocess.run(base+args,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+args,exitCode=r.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
(p/'inputs.json').write_text(json.dumps(dict(accepted=False,imageId=image_id,sourceSha256=hashlib.sha256((p/'main.cpp').read_bytes()).hexdigest()),indent=2)+'\n')
