from pathlib import Path
import json,hashlib,subprocess,time
p=Path(__file__).resolve().parent;runtime=p/'runtime';pkg=p.parent/'navigation-cjk-package-v2/runtime';inputs=json.loads((p/'inputs.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(pkg/'consumer-build/InstalledConsumer')==inputs['consumerSha256']
assert all(sha(pkg/'install'/n)==v for n,v in inputs['packageFiles'].items())
base=['docker','--context','colima-avelino-verify'];assert subprocess.check_output(base+['image','inspect',inputs['image'],'--format','{{.Id}}'],text=True).strip()==inputs['imageId']
command=base+['run','--rm','--name','avelino-weston-popup-display-v1-20261018','--ulimit','core=268435456:268435456','-v',str(runtime)+':/display-check','-v',str(pkg/'install')+':/display-check/install:ro','-v',str(pkg/'consumer-build/InstalledConsumer')+':/display-check/consumer-build/InstalledConsumer:ro','-w','/display-check',inputs['image'],'python3','-c',"from pathlib import Path;import os;assert not Path('/work/src/Avelino').exists() and not Path('/consumer-check').exists() and not Path('/display-check/consumer').exists();os.execv('/bin/bash',['bash','check.sh','/display-check/output'])"]
(p/'running-command.json').write_text(json.dumps(dict(command=command,startedAt=time.time()),indent=2)+'\n')
start=time.monotonic()
with(p/'display.log').open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
cores=[f for f in runtime.glob('core*')if f.is_file()]
(p/'commands.json').write_text(json.dumps([dict(name='complete-display',command=command,exitCode=r.returncode,seconds=time.monotonic()-start)],indent=2)+'\n')
result=dict(accepted=False,exitCode=r.returncode or int(bool(cores)),scriptExitCode=r.returncode,unexpectedCores=[dict(path=f.name,bytes=f.stat().st_size,sha256=sha(f))for f in cores],libraryAndConsumerProjectSourcesAbsentAtRuntime=True)
(p/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('Complete patched-compositor display gate',result['exitCode']);raise SystemExit(result['exitCode'])
