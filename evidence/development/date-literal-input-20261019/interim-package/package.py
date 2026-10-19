from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
p=Path(__file__).resolve().parent;r=p.parents[2];producer=p.parent/sys.argv[1]
ready=json.loads((producer/'commands.json').read_text());assert [row['name']for row in ready[:4]]==['activate-inputs','configure','build','install'] and all(row['exitCode']==0 for row in ready[:4])
image='avelino-toolchain:weston13-popup-parent-v2-20261018-qt6.8.3'
image_id=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
assert image_id=='sha256:b970d61e5315d9c1a3ffb56b57ecae08922acdcdccf321c99e705984b30ae437'
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
for name,command in [('source-absence',['python3','-c',"from pathlib import Path; assert not Path('/work/src/Avelino').exists(); assert not Path('/work/CMakeLists.txt').exists(); assert not Path('/work/build').exists(); assert not Path('/Users/gaulatti/source/gaulatti/avelino').exists(); print('Library source and producer build absent')"]),('consumer-configure',['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/consumer-check/install;/opt/qt']),('consumer-build',['cmake','--build','consumer-build','--parallel','2'])]:run(name,base+[image]+command)
# Runtime receives no project or build sources; only the installed prefix and ELF.
runtime=p/'runtime';runtime.mkdir();shutil.copytree(p/'install',runtime/'install');(runtime/'consumer-build').mkdir();shutil.copy2(p/'consumer-build/InstalledConsumer',runtime/'consumer-build/InstalledConsumer');(runtime/'output').mkdir()
inputs['consumerSha256']=sha(runtime/'consumer-build/InstalledConsumer');(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
for dark in [False,True]:
 for scale in [1,1.5]:
  for dpr in [1,2]:
   name=f'{"dark"if dark else"light"}-text{scale:g}-dpr{dpr}'
   prefix='/relocated-check/output/'+name
   args=['./consumer-build/InstalledConsumer','--navigation','--text-scale',str(scale),'--evidence',prefix]+(['--dark']if dark else[])
   startup="""from pathlib import Path
import json,subprocess,time
assert not Path('/work/src/Avelino').exists() and not Path('/work/build').exists() and not Path('/consumer-check').exists() and not Path('/relocated-check/consumer').exists()
args=ARGS
prefix=Path(PREFIX)
child=subprocess.Popen(args)
while child.poll()is None and not Path(str(prefix)+'.json').exists():time.sleep(0.02)
if Path(str(prefix)+'.json').exists():
 json.loads(Path(str(prefix)+'.json').read_text());assert Path(str(prefix)+'.png').exists();Path(str(prefix)+'.captured').touch()
raise SystemExit(child.wait())
""".replace('ARGS',repr(args)).replace('PREFIX',repr(prefix))
   command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/relocated-check','-w','/relocated-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','QT_SCALE_FACTOR='+str(dpr),image,'python3','-c',startup]
   run(name,command)
# Replay every source-absent consumer invocation from the unchanged Linux driver.
import shlex
needle='"$stage/build/InstalledConsumer"'
smoke=[]
for line in (r/'scripts/check-linux.sh').read_text().splitlines():
 if line.startswith('(cd "$stage" &&') and needle in line:
  suffix=line.split(needle,1)[1];assert suffix.endswith(')')
  smoke.append([token.replace('$stage','/relocated-check/output/smoke')for token in shlex.split(suffix[:-1])])
(runtime/'output/smoke').mkdir()
inputs['smokeDriverSha256']=sha(r/'scripts/check-linux.sh');inputs['smokeArguments']=smoke;(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
for index,args in enumerate(smoke):
 arguments=['./consumer-build/InstalledConsumer']+args
 startup="from pathlib import Path;import os;assert not Path('/work/src/Avelino').exists() and not Path('/consumer-check').exists() and not Path('/relocated-check/consumer').exists();os.execv('./consumer-build/InstalledConsumer',"+repr(arguments)+")"
 run('smoke-'+str(index),['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/relocated-check','-w','/relocated-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software',image,'python3','-c',startup])
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,contexts=8,smokeInvocations=len(smoke),libraryAndConsumerProjectSourcesAbsentAtRuntime=True,freshConsumerBuild=True,nativeAcceptance='pending'),indent=2)+'\n')
