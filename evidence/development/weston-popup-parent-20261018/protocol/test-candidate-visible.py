from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parent;prefix=p.parent/'weston-popup-guard-asan-v1/install'
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/probe','-v',str(prefix)+':/probe/install:ro','-w','/probe','--env','WESTON_BIN=/probe/install/bin/weston','--env','WESTON_LIB=/probe/install/lib','avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3','bash','probe.sh','/probe/candidate-sanitizer-visible-v2']
start=time.monotonic()
with(p/'candidate-sanitizer-visible-v2.log').open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'candidate-visible-result.json').write_text(json.dumps(dict(accepted=False,command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print('Candidate protocol-order regression',r.returncode)
raise SystemExit(r.returncode)
