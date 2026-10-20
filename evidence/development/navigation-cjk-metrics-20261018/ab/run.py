from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];work=p.parent/'file-input-qt-v21/fresh-build';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for cid in subprocess.check_output(['docker','--context','colima-avelino-verify','ps','-q'],text=True).split():
    wd=subprocess.check_output(['docker','--context','colima-avelino-verify','inspect',cid,'--format','{{.Config.WorkingDir}}'],text=True).strip();assert 'file-input-qt-v21/fresh-build'not in wd
files=json.loads((p.parent/'date-range-qt-v35/inputs.json').read_text())['files']
assert all(sha(r/name)==value and sha(work/'source'/name)==value for name,value in files.items())
images=[('with-cjk','avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3','sha256:05ed336701790c156dc6f59b48c195d6ac36144205c0eb75696001e9c9893fc6'),('without-cjk','avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3','sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8')]
for _,image,expected in images:assert subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()==expected
(p/'inputs.json').write_text(json.dumps(dict(accepted=False,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),sourceFiles=files,previousValidatedProducer='date-range-qt-v35',activated=['tests/components/main.cpp'],images=images),indent=2)+'\n')
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work','-w','/work/'+str((work/'source').relative_to(r))]
for name in ['evidence','reference','scripts','tools','tokens','docs']:base+=['-v',str(r/name)+':/work/'+str((work/'source'/name).relative_to(r))+':ro']
steps=[]
def run(name,image,command):
    start=time.monotonic()
    with(p/(name+'.log')).open('w')as log:result=subprocess.run(base+[image]+command,stdout=log,stderr=subprocess.STDOUT)
    steps.append(dict(name=name,command=base+[image]+command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True);return result.returncode
assert run('activate',images[0][1],['python3','-c',"from pathlib import Path; Path('tests/components/main.cpp').touch()"])==0
assert run('build',images[0][1],['cmake','--build','../build','--target','AvelinoComponentTests','--parallel','4'])==0
for name,image,_ in images:
    run(name,image,['env','QT_QPA_PLATFORM=offscreen','QT_QUICK_BACKEND=software','QT_SCALE_FACTOR=1','../build/tests/components/AvelinoComponentTests','-input','tests/components/tst_navigation.qml','-import','../build/qml','NavigationContract::test_native_geometry'])
(p/'result.json').write_text(json.dumps(dict(accepted=False,steps=steps,scope='Same test binary, module and source inputs; only immutable toolchain font layer differs. Does not grant glyph, pixel or native acceptance.'),indent=2)+'\n')
