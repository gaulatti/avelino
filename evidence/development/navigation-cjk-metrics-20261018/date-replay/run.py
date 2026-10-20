from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];source=p.parent/'navigation-cjk-package-v2';inputs=json.loads((source/'inputs.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert inputs['freshConsumerBuild'] and inputs['consumerSha256']==sha(source/'runtime/consumer-build/InstalledConsumer')
assert all(sha(r/'tests/consumer'/name)==value for name,value in inputs['consumerFiles'].items())
assert all(row['exitCode']==0 for row in json.loads((source/'commands.json').read_text())[:3])
runtime=p/'runtime';runtime.mkdir();shutil.copytree(source/'runtime/install',runtime/'install');(runtime/'consumer-build').mkdir();shutil.copy2(source/'runtime/consumer-build/InstalledConsumer',runtime/'consumer-build/InstalledConsumer');(runtime/'output').mkdir()
inputs=dict(inputs,freshConsumerBuild=False,consumerCompilationProducer='navigation-cjk-package-v2');(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n');image=inputs['image'];steps=[]
def run(name,command):
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:
  (p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
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
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,contexts=8,galleryContexts=8,libraryAndConsumerProjectSourcesAbsentAtRuntime=True,freshConsumerBuild=False,consumerCompilationProducer="navigation-cjk-package-v2",nativeAcceptance='pending'),indent=2)+'\n')
