from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];producer=p.parent/'item-lifetime-fixed-v1';assert json.loads((producer/'result.json').read_text())['exitCode']==0
shutil.copytree(producer/'install',p/'install');shutil.copytree(producer/'source/tests/consumer',p/'consumer')
for name in ['check-installed.sh','check-installed-catalog.sh']:(p/name).write_bytes(subprocess.check_output(['git','show','a411c51b58810bf7df84eb72ae3271637c1274ab:scripts/'+name],cwd=r))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'inputs.json').write_text(json.dumps(dict(accepted=False,producerInputs=json.loads((producer/'inputs.json').read_text()),installedFiles={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()}),indent=2)+chr(10))
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/package','-w','/package','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-item-lifetime','avelino-toolchain:clipping-qt6.8.3'];steps=[]
for name,command in [('source-absence',['python3','-c',"from pathlib import Path; assert not Path('/work/src/Avelino').exists(); assert not Path('/work/build').exists(); assert not Path('/Users/gaulatti/source/gaulatti/avelino').exists(); print('Library source and build absent')"]),('installed-suite',['bash','check-installed.sh'])]:
 start=time.monotonic()
 with(p/(name+'.log')).open('wb')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+chr(10));print(name,result.returncode,flush=True)
 if result.returncode:(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+chr(10));raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0),indent=2)+chr(10))
