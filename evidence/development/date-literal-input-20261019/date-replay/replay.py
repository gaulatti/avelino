from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];source=p.parent/'date-literal-package-v2';inputs=json.loads((source/'inputs.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert inputs['freshConsumerBuild'] and inputs['consumerSha256']==sha(source/'runtime/consumer-build/InstalledConsumer')
assert all(sha(r/'tests/consumer'/name)==value for name,value in inputs['consumerFiles'].items())
assert all(row['exitCode']==0 for row in json.loads((source/'commands.json').read_text())[:3])
runtime=p/'runtime';runtime.mkdir();shutil.copytree(source/'runtime/install',runtime/'install');(runtime/'consumer-build').mkdir();shutil.copy2(source/'runtime/consumer-build/InstalledConsumer',runtime/'consumer-build/InstalledConsumer');(runtime/'output').mkdir()
inputs=dict(inputs,freshConsumerBuild=False,consumerCompilationProducer='date-literal-package-v2');(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n');image=inputs['image'];steps=[]
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
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,contexts=8,galleryContexts=8,libraryAndConsumerProjectSourcesAbsentAtRuntime=True,freshConsumerBuild=False,consumerCompilationProducer="date-literal-package-v2",nativeAcceptance='pending'),indent=2)+'\n')

parent=r/'evidence/development/date-range-fields-20261018'
expected=[]
for row in json.loads((parent/'strict/comparison.json').read_text())['results']:expected.append((row['fixture'],row['candidateSHA256']))
for row in json.loads((parent/'chinese-comparison.json').read_text())['results']:expected.append((row['candidateName'],row['candidateSHA256']))
assert len(expected)==437
changed=[dict(path=name,expected=value,actual=sha(runtime/'output'/name))for name,value in expected if sha(runtime/'output'/name)!=value]
comparison=dict(count=437,identical=437-len(changed),differences=changed,parentManifestSHA256=sha(parent/'files.json'))
(p/'raw-image-comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
assert not changed,changed[:3]
profiles=[]
for f in (runtime/'output').glob('*.json'):
 row=json.loads(f.read_text())
 if row.get('fixture')!='date-range' or not row.get('closed'):continue
 literals=row['literalInput'];assert len(literals)==16 and all(v['samePixels']and v['before']==v['after']for v in literals)
 assert sum(v['nativeValueCompared']for v in literals)==8
 profiles.append(dict(path=f.name,literalChecks=16,nativeValueComparisons=8,sha256=sha(f)))
assert len(profiles)==8
(p/'literal-validation.json').write_text(json.dumps(dict(accepted=False,profiles=profiles,checks=128,nativeValueComparisons=64,scope='Four native histories extended across Qt caller direction, both endpoints and package contexts; no initial-field or glyph acceptance'),indent=2)+'\n')
print('Date replay:437 raw candidates unchanged;128 literal checks and64 source-value comparisons')
