from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
p=Path(__file__).resolve().parent;r=p.parents[2];producer=p.parent/sys.argv[1]
assert json.loads((producer/'result.json').read_text())['exitCode']==0
image='avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3'
image_id=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
assert image_id=='sha256:05ed336701790c156dc6f59b48c195d6ac36144205c0eb75696001e9c9893fc6'
shutil.copytree(producer/'install',p/'install');shutil.copytree(producer/'source/tests/consumer',p/'consumer')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
inputs=dict(accepted=False,producer=producer.name,image=image,imageId=image_id,freshConsumerBuild=True,packageFiles={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()},consumerFiles={str(f.relative_to(p/'consumer')):sha(f)for f in sorted((p/'consumer').rglob('*'))if f.is_file()})
(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n');steps=[]
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/consumer-check','-w','/consumer-check']
def run(name,command):
 start=time.monotonic()
 with(p/(name+'.log')).open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:
  (p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
for name,command in [('source-absence',['python3','-c',"from pathlib import Path; assert not Path('/work/src/Avelino').exists(); assert not Path('/work/CMakeLists.txt').exists(); assert not Path('/work/build').exists(); assert not Path('/Users/gaulatti/source/gaulatti/avelino').exists(); print('Library source and producer build absent')"]),('consumer-configure',['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/consumer-check/install;/opt/qt']),('consumer-build',['cmake','--build','consumer-build','--parallel','4'])]:run(name,base+[image]+command)
# Runtime receives no project or build sources; only the installed prefix and ELF.
runtime=p/'runtime';runtime.mkdir();shutil.copytree(p/'install',runtime/'install');(runtime/'consumer-build').mkdir();shutil.copy2(p/'consumer-build/InstalledConsumer',runtime/'consumer-build/InstalledConsumer');(runtime/'output').mkdir()
inputs['consumerSha256']=sha(runtime/'consumer-build/InstalledConsumer');(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
for dark in [False,True]:
 for scale in [1,1.5]:
  for dpr in [1,2]:
   name=f'{"dark"if dark else"light"}-text{scale:g}-dpr{dpr}'
   args=['./consumer-build/InstalledConsumer','--date-range','--date-range-observe','--text-scale',str(scale),'--date-range-report','/relocated-check/output/'+name]+(['--dark']if dark else[])
   startup="from pathlib import Path; import os; assert not Path('/work/src/Avelino').exists(); assert not Path('/work/CMakeLists.txt').exists(); assert not Path('/work/build').exists(); assert not Path('/consumer-check').exists(); assert not Path('/relocated-check/consumer').exists(); assert not Path('/relocated-check/src').exists(); os.execv('./consumer-build/InstalledConsumer',"+repr(args)+")"
   command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/relocated-check','-w','/relocated-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','QT_SCALE_FACTOR='+str(dpr),'--env','XDG_RUNTIME_DIR=/tmp/avelino-date-range',image,'python3','-c',startup]
   run(name,command)
for dark in [False,True]:
 for scale in [1,1.5]:
  for dpr in [1,2]:
   name=f'gallery-{"dark"if dark else"light"}-text{scale:g}-dpr{dpr}'
   args=['./consumer-build/InstalledConsumer','--date-range','--date-range-gallery','--text-scale',str(scale),'--date-range-report','/relocated-check/output/'+name]+(['--dark']if dark else[])
   startup="from pathlib import Path; import os; assert not Path('/work/src/Avelino').exists(); assert not Path('/work/CMakeLists.txt').exists(); assert not Path('/work/build').exists(); assert not Path('/consumer-check').exists(); assert not Path('/relocated-check/consumer').exists(); assert not Path('/relocated-check/src').exists(); os.execv('./consumer-build/InstalledConsumer',"+repr(args)+")"
   command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/relocated-check','-w','/relocated-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','QT_SCALE_FACTOR='+str(dpr),'--env','XDG_RUNTIME_DIR=/tmp/avelino-date-range',image,'python3','-c',startup]
   run(name,command)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,contexts=8,galleryContexts=8,libraryAndConsumerProjectSourcesAbsentAtRuntime=True,freshConsumerBuild=True,nativeAcceptance='pending'),indent=2)+'\n')
