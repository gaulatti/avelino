from pathlib import Path
import json,subprocess,time,shutil
root=Path.cwd();d=root/'evidence/development/file-input-views-20261017';p=root/'artifacts/resumed-avelino-20261016/file-input-views-restored-v1'
subprocess.run(['python3',str(d/'tools/reconstruct.py'),'--output',str(p),'--source','--package'],check=True)
q=d/'portable';q.mkdir()
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p/'package')+':/consumer-check','-w','/consumer-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-restored-views','avelino-toolchain:recovered-20261017-qt6.8.3','python3','-c',"from pathlib import Path;import os;assert not Path('/work/src/Avelino').exists();assert not Path('/consumer-check/source').exists();assert not Path('/consumer-check/consumer').exists();os.execv('./consumer-build/InstalledConsumer',['./consumer-build/InstalledConsumer','--file-input','--file-input-observe','--file-input-report','/consumer-check/output/light-text1-dpr1'])"]
start=time.monotonic()
with(q/'runtime.log').open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(q/'runtime-result.json').write_text(json.dumps(dict(command=command,exitCode=result.returncode,seconds=time.monotonic()-start,libraryAndConsumerSourceAbsent=True,accepted=False),indent=2)+'\n');assert result.returncode==0
f=p/'package/output/light-text1-dpr1.json';row=json.loads(f.read_text());old=json.loads((d/'captures'/f.name).read_text());assert row['closed']==old['closed']and row['sizing']==old['sizing']
assert(row['images'],len(row['actions']),row['pointerEvents'],row['keyEvents'])==(42,20,38,38)
for case in row['closed']:
 name=f.stem+'-'+case['configuration']['id']+'.png';assert(f.parent/name).read_bytes()==(d/'captures'/name).read_bytes(),name
shutil.copy2(f,q/f.name);(q/'comparison.json').write_text(json.dumps(dict(accepted=False,unchangedClosedImages=32,closedAndSizingMetadataUnchanged=True,images=42,ownerInputTraces=20),indent=2)+'\n')
print('Restored package: source-free runtime passed, 20 traces, 32 byte-identical closed images')
