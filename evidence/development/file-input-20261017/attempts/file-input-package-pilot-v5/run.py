from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];producer=p.parent/'file-input-qt-v13';assert json.loads((producer/'result.json').read_text())['exitCode']==0
shutil.copytree(producer/'install',p/'install');shutil.copytree(producer/'source/tests/consumer',p/'consumer');(p/'output').mkdir()
for name in ['check-installed.sh','check-installed-catalog.sh','check-display-sessions.sh']:shutil.copy2(r/'scripts'/name,p/name)
(p/'environment.json').write_text(json.dumps(dict(accepted=False,qt='6.8.3',producerInputs=json.loads((producer/'inputs.json').read_text()),runtimeImage='avelino-toolchain:clipping-qt6.8.3',runtimeImageId='sha256:7aeb42dabe57ff3e38392d95b92f7f54c43faef5723e90da088c9023bfcf2802'),indent=2)+'\n')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'inputs.json').write_text(json.dumps(dict(accepted=False,producer=str(producer),packageFiles={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()},consumerFiles={str(f.relative_to(p/'consumer')):sha(f)for f in sorted((p/'consumer').rglob('*'))if f.is_file()}),indent=2)+'\n')
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/consumer-check','-w','/consumer-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-file-input-runtime','avelino-toolchain:clipping-qt6.8.3'];steps=[]
for name,command in [('source-absence',['python3','-c',"from pathlib import Path; assert not Path('/work/src/Avelino').exists(); assert not Path('/work/CMakeLists.txt').exists(); assert not Path('/work/build').exists(); assert not Path('/Users/gaulatti/source/gaulatti/avelino').exists(); print('Library source and build absent')"]),('installed-suite',['bash','check-installed.sh']),('file-input',['./consumer-build/InstalledConsumer','--file-input','--file-input-observe','--file-input-report','/consumer-check/output/light-text1-dpr1'])]:
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
for appearance in ['light','dark']:
 for scale in [1,1.5]:
  for dpr in [1,2]:
   if (appearance,scale,dpr)==('light',1,1):continue
   name=f'{appearance}-text{scale:g}-dpr{dpr}'
   command=base[:-1]+['--env','QT_SCALE_FACTOR='+str(dpr)]+[base[-1],'./consumer-build/InstalledConsumer','--file-input','--file-input-observe','--text-scale',str(scale),'--file-input-report','/consumer-check/output/'+name]
   if appearance=='dark':command.append('--dark')
   start=time.monotonic()
   with(p/(name+'.log')).open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
   steps.append(dict(name=name,command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
   if result.returncode:(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0),indent=2)+'\n')
