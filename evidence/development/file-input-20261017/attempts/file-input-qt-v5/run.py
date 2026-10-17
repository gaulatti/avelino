from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];src=p/'source';assert not src.exists();src.mkdir()
for name in ['CMakeLists.txt','src','samples','tests','assets','cmake']:
 f=r/name
 if f.is_dir():shutil.copytree(f,src/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 else:shutil.copy2(f,src/name)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'inputs.json').write_text(json.dumps(dict(accepted=False,baseGit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),files={str(f.relative_to(src)):sha(f)for f in sorted(src.rglob('*'))if f.is_file()}),indent=2)+'\n')
steps=[];base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work','-w','/work/'+str(src.relative_to(r)),'avelino-toolchain:data-metrics-qt6.8.3']
for name,command in [('configure',['cmake','-S','.','-B','../build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug','-DBUILD_TESTING=ON']),('build',['cmake','--build','../build','--target','AvelinoFileChooserTests','AvelinoFileBrowserTests','AvelinoFileInputUiTests','--parallel','2']),('filesystem-tests',['ctest','--test-dir','../build','-R','^(file-chooser-filesystem|file-chooser-columns|file-input-owned-ui)$','--output-on-failure'])]:
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0),indent=2)+'\n')
