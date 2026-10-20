from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parent;image='avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3';steps=[]
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/probe','-w','/probe']
def run(name,args):
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:r=subprocess.run(base+args,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+args,exitCode=r.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,r.returncode,flush=True)
 return r.returncode
if run('build',[image,'bash','build.sh']):raise SystemExit(1)
asan=p.parent/'tooltip-weston-asan-v2/install'
run('original-sanitizer',['-v',str(asan)+':/sanitizer:ro','--env','WESTON_BIN=/sanitizer/bin/weston','--env','WESTON_LIB=/sanitizer/lib',image,'bash','probe.sh','/probe/original-sanitizer'])
run('original-release',[image,'bash','probe.sh','/probe/original-release'])
(p/'result.json').write_text(json.dumps(dict(accepted=False,steps=steps,scope='Deterministic protocol-order reproducer; no product or toolchain changes'),indent=2)+'\n')
