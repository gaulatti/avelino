from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];
previous=json.loads((p.parent/'date-range-qt-v32/result.json').read_text());assert previous['exitCode']==0
image_id=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect','avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3','--format','{{.Id}}'],text=True).strip()
assert image_id=='sha256:05ed336701790c156dc6f59b48c195d6ac36144205c0eb75696001e9c9893fc6'
running=subprocess.check_output(['docker','--context','colima-avelino-verify','ps','--format','{{.ID}}'],text=True).split()
for cid in running:
    directory=subprocess.check_output(['docker','--context','colima-avelino-verify','inspect',cid,'--format','{{.Config.WorkingDir}}'],text=True).strip()
    assert 'file-input-qt-v21/fresh-build'not in directory

src=p/'source';assert not src.exists();src.mkdir();work=p.parent/'file-input-qt-v21/fresh-build';(work/'source').mkdir(parents=True,exist_ok=True)
for name in ['CMakeLists.txt','src','samples','tests','assets','cmake']:
 f=r/name
 if f.is_dir():shutil.copytree(f,src/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 else:shutil.copy2(f,src/name)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files={str(f.relative_to(src)):sha(f)for f in sorted(src.rglob('*'))if f.is_file()};(p/'inputs.json').write_text(json.dumps(dict(accepted=False,baseGit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),files=files,buildWorkDirectory=str(work)),indent=2)+'\n')
for f in src.rglob('*'):
 if f.is_file():
  dest=work/'source'/f.relative_to(src);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists() or dest.read_bytes()!=f.read_bytes():shutil.copy2(f,dest)
steps=[];base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work','-w','/work/'+str((work/'source').relative_to(r))]
for name in ['evidence','reference','scripts','tools','tokens','docs']:base+=['-v',str(r/name)+':/work/'+str((work/'source'/name).relative_to(r))+':ro']
base+=['avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3']
for name,command in [('configure',['cmake','-S','.','-B','../build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug','-DBUILD_TESTING=ON','-DCMAKE_INSTALL_PREFIX=/work/'+str(p.relative_to(r))+'/install']),('date-build',['cmake','--build','../build','--target','AvelinoDateRangeToolsTests','AvelinoDateRangeUiTests','AvelinoCatalog','--parallel','4']),('install',['cmake','--install','../build']),('date-tests',['ctest','--test-dir','../build','-R','^date-range-(calendar-components|owned-input(-dpr2)?)$','--output-on-failure'])]:
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if name=='date-tests':shutil.copy2(work/'build/Testing/Temporary/LastTest.log',p/'ctest-last-test.log')
 if result.returncode:(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)

(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0),indent=2)+'\n')
