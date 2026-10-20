from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];package=p.parent/'date-literal-package-v2'
inputs=json.loads((package/'inputs.json').read_text())
assert inputs['freshConsumerBuild']
assert inputs['consumerSha256']==hashlib.sha256((package/'runtime/consumer-build/InstalledConsumer').read_bytes()).hexdigest()
assert all(step['exitCode']==0 for step in json.loads((package/'commands.json').read_text())[:3])
for name,value in inputs['packageFiles'].items():assert hashlib.sha256((package/'runtime/install'/name).read_bytes()).hexdigest()==value,name
runtime=p/'runtime';runtime.mkdir();shutil.copytree(package/'runtime/install',runtime/'install');(runtime/'consumer-build').mkdir();shutil.copy2(package/'runtime/consumer-build/InstalledConsumer',runtime/'consumer-build/InstalledConsumer')
shutil.copy2(r/'scripts/check-display-sessions-date-range.sh',runtime/'check.sh')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
image='avelino-toolchain:weston13-popup-parent-v2-20261018-qt6.8.3'
imageId=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
assert imageId=='sha256:b970d61e5315d9c1a3ffb56b57ecae08922acdcdccf321c99e705984b30ae437'
environment=dict(accepted=False,package=package.name,consumerSha256=sha(runtime/'consumer-build/InstalledConsumer'),scriptSha256=sha(runtime/'check.sh'),imageId=imageId,physicalDisplay=False,hardwareAcceleration=False)
(runtime/'environment.json').write_text(json.dumps(environment,indent=2)+'\n');(p/'inputs.json').write_text(json.dumps(environment,indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/display-check','-w','/display-check',image,'bash','check.sh','/display-check/output']
start=time.monotonic()
with(p/'display.log').open('w')as log: result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'commands.json').write_text(json.dumps([dict(name='display-sessions',command=command,exitCode=result.returncode,seconds=time.monotonic()-start)],indent=2)+'\n')
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,profiles=8 if result.returncode==0 else None),indent=2)+'\n');print('display',result.returncode)
raise SystemExit(result.returncode)
