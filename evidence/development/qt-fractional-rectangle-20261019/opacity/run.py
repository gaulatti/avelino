from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;inputs=json.loads((p/'inputs.json').read_text())
assert json.loads((p.parent/'qt-rectangle-mobile-runtime-v1/result.json').read_text())['exitCode']==0
for name,value in inputs['files'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==value
command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(p)+':/result',inputs['imageId'],'bash','/result/check-qt-software-opacity.sh','/result/output']
start=time.monotonic()
with(p/'run.log').open('x')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
record=dict(command=command,exitCode=result.returncode,seconds=time.monotonic()-start,experimentalOnly=True,productSdkChanged=False,accepted=False)
(p/'result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2));print('\n'.join((p/'run.log').read_text(errors='replace').splitlines()[-18:]));raise SystemExit(result.returncode)
