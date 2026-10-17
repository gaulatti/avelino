from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];src=p/'source';assert not src.exists();src.mkdir();work=p.parent/'file-input-build';(work/'source').mkdir(parents=True,exist_ok=True)
for name in ['CMakeLists.txt','src','samples','tests','assets','cmake']:
 f=r/name
 if f.is_dir():shutil.copytree(f,src/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 else:shutil.copy2(f,src/name)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files={str(f.relative_to(src)):sha(f)for f in sorted(src.rglob('*'))if f.is_file()};(p/'inputs.json').write_text(json.dumps(dict(accepted=False,baseGit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),files=files,buildWorkDirectory=str(work)),indent=2)+'\n')
for f in src.rglob('*'):
 if f.is_file():dest=work/'source'/f.relative_to(src);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
steps=[];base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work','-w','/work/'+str((work/'source').relative_to(r))]
for name in ['evidence','reference','scripts','tools','tokens','docs']:base+=['-v',str(r/name)+':/work/'+str((work/'source'/name).relative_to(r))+':ro']
base+=['avelino-toolchain:data-metrics-qt6.8.3']
for name,command in [('configure',['cmake','-S','.','-B','../build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug','-DBUILD_TESTING=ON','-DCMAKE_INSTALL_PREFIX=/work/'+str(p.relative_to(r))+'/install','-DAVELINO_FILE_INPUT_EVIDENCE_DIR=/work/'+str(p.relative_to(r))+'/ui-output']),('foundation-build',['cmake','--build','../build','--target','AvelinoItemLifetimeTests','--parallel','2']),('foundation-tests',['ctest','--test-dir','../build','-R','^item-lifetime(-dpr2)?$','--output-on-failure']),('backend-build',['cmake','--build','../build','--target','AvelinoFileChooserTests','AvelinoFileBrowserTests','--parallel','2']),('backend-tests',['ctest','--test-dir','../build','-R','^file-chooser-(filesystem|columns)$','--output-on-failure']),('ui-build',['cmake','--build','../build','--target','AvelinoFileInputUiTests','AvelinoCatalog','--parallel','2']),('ui-tests',['ctest','--test-dir','../build','-R','^file-input-owned-ui(-dpr2)?$','--output-on-failure']),('full-build',['cmake','--build','../build','--parallel','2']),('all-qt-tests',['ctest','--test-dir','../build','--output-on-failure']),('install',['cmake','--install','../build'])]:
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0),indent=2)+'\n')
