from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
p=Path(__file__).resolve().parent;r=p.parents[2];producer=p.parent/sys.argv[1]
while not(producer/'result.json').exists():time.sleep(.2)
assert json.loads((producer/'result.json').read_text())['exitCode']==0
image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3'
image_id=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
assert image_id=='sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8'
prior=p.parent/'file-input-location-package-v1'
assert json.loads((prior/'result.json').read_text())['exitCode']==0
fresh=json.loads((prior/'inputs.json').read_text());source=json.loads((producer/'inputs.json').read_text())['files']
assert fresh['consumerFiles']=={name.removeprefix('tests/consumer/'):digest for name,digest in source.items() if name.startswith('tests/consumer/')}
shutil.copytree(producer/'install',p/'install');(p/'consumer-build').mkdir();shutil.copy2(prior/'runtime/consumer-build/InstalledConsumer',p/'consumer-build/InstalledConsumer')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
inputs=dict(accepted=False,producer=producer.name,image=image,imageId=image_id,freshConsumerBuild=False,consumerSourceIdenticalToFinal=True,consumerBinarySource=prior.name,consumerSourceProducer=fresh['producer'],packageFiles={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()},consumerFiles=fresh['consumerFiles'])
(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n');steps=[]
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/consumer-check','-w','/consumer-check']
def run(name,command):
 start=time.monotonic()
 with(p/(name+'.log')).open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:
  (p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
assert sha(p/'consumer-build/InstalledConsumer')==fresh['consumerSha256']
# Runtime receives no project or build sources; only the installed prefix and ELF.
runtime=p/'runtime';runtime.mkdir();shutil.copytree(p/'install',runtime/'install');(runtime/'consumer-build').mkdir();shutil.copy2(p/'consumer-build/InstalledConsumer',runtime/'consumer-build/InstalledConsumer');(runtime/'output').mkdir()
inputs['consumerSha256']=sha(runtime/'consumer-build/InstalledConsumer');(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
for dark in [False,True]:
 for scale in [1,1.5]:
  for dpr in [1,2]:
   name=f'{"dark"if dark else"light"}-text{scale:g}-dpr{dpr}'
   args=['./consumer-build/InstalledConsumer','--file-input','--file-input-observe','--text-scale',str(scale),'--file-input-report','/consumer-check/output/'+name]+(['--dark']if dark else[])
   startup="from pathlib import Path; import os; assert not Path('/work/src/Avelino').exists(); assert not Path('/work/CMakeLists.txt').exists(); assert not Path('/work/build').exists(); assert not Path('/consumer-check/consumer').exists(); assert not Path('/consumer-check/src').exists(); os.execv('./consumer-build/InstalledConsumer',"+repr(args)+")"
   command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/consumer-check','-w','/consumer-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','QT_SCALE_FACTOR='+str(dpr),'--env','XDG_RUNTIME_DIR=/tmp/avelino-navigation',image,'python3','-c',startup]
   run(name,command)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,contexts=8,libraryAndConsumerProjectSourcesAbsentAtRuntime=True,freshConsumerBuild=False,consumerSourceIdenticalToFinal=True,consumerBinarySource=prior.name,consumerSourceProducer=fresh['producer'],nativeAcceptance='pending'),indent=2)+'\n')
