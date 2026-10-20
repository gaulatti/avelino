from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;b=p.parent;qt=b/'date-literal-qt-v2';diagnostic=b/'date-literal-gl-diagnostic-v1';runtime=diagnostic/'runtime'
while not (qt/'result.json').exists():time.sleep(5)
assert json.loads((qt/'result.json').read_text())['exitCode']==0
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/display-check','-v',str(qt/'install')+':/display-check/install:ro','-w','/display-check','avelino-toolchain:weston13-popup-parent-v2-20261018-qt6.8.3','bash','check.sh','/display-check/fixed-output']
(p/'inputs.json').write_text(json.dumps(dict(accepted=False,consumerSha256=hashlib.sha256((runtime/'consumer-build/InstalledConsumer').read_bytes()).hexdigest(),priorFailedProducer=diagnostic.name,newModuleProducer=qt.name,sameDiagnosticElf=True),indent=2)+'\n')
t=time.monotonic()
with(p/'case.log').open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(accepted=False,command=command,exitCode=r.returncode,seconds=time.monotonic()-t),indent=2)+'\n');print('Same-ELF scaled X11/GL after selected-caret fix',r.returncode);raise SystemExit(r.returncode)
