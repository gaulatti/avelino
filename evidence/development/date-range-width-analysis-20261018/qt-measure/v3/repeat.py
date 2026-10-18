from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3'
imageId=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip();assert imageId=='sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8'
command=['docker','--context','colima-avelino-verify','run','--rm','-v',str(p)+':/measure-check','-w','/measure-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-date-widths',image,'./build/DateWidthMeasure','input.json','output-repeat.json'];start=time.monotonic()
with(p/'measure-repeat.log').open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'measure-repeat-commands.json').write_text(json.dumps([dict(command=command,exitCode=result.returncode,seconds=time.monotonic()-start)],indent=2)+'\n');assert result.returncode==0
assert (p/'output-repeat.json').read_bytes()==(p/'output.json').read_bytes()
rows=json.loads((p/'output.json').read_text());assert len(rows)==1848
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'measure-result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,measuredDates=1848,repeatedOutputExact=True,imageId=imageId,consumerSha256=sha(p/'build/DateWidthMeasure'),inputSha256=sha(p/'input.json'),outputSha256=sha(p/'output.json'),geometryAcceptance='pending',fontAcceptance='pending'),indent=2)+'\n');print('Qt installed-module metrics: 1848 rows, exact repeat, no geometry/font acceptance')
