from pathlib import Path
import hashlib, json, shutil, subprocess, time

p=Path(__file__).resolve().parent
root=p.parents[2]
producer=p.parent/'file-input-qt-v17'
assert json.loads((producer/'result.json').read_text())['exitCode']==0
shutil.copytree(producer/'source',p/'source')
files={str(f.relative_to(p/'source')):hashlib.sha256(f.read_bytes()).hexdigest()for f in sorted((p/'source').rglob('*'))if f.is_file()}
assert files==json.loads((producer/'inputs.json').read_text())['files']
(p/'source-files.json').write_text(json.dumps(files,indent=2)+'\n')
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/replay','-w','/replay/source']
for name in ['evidence','reference','scripts','tools','tokens','docs']:
    base+=['-v',str(root/name)+':/replay/source/'+name+':ro']
base+=['avelino-toolchain:data-metrics-qt6.8.3']
steps=[]
for name,command in [
    ('source-isolation',['python3','-c',"from pathlib import Path; assert not any(Path('/work').iterdir()); assert not Path('/replay/build').exists(); assert not Path('/consumer-check').exists(); print('Fresh build and no original library/build checkout')"]),
    ('configure',['cmake','-S','.','-B','../build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug','-DBUILD_TESTING=ON','-DAVELINO_FILE_INPUT_EVIDENCE_DIR=/replay/ui-output']),
    ('build',['cmake','--build','../build','--target','AvelinoFileChooserTests','AvelinoFileBrowserTests','AvelinoFileInputUiTests','AvelinoCatalog','--parallel','2']),
    ('tests',['ctest','--test-dir','../build','-R','^file-(chooser-(filesystem|columns)|input-owned-ui(-dpr2)?)$','--output-on-failure'])]:
    start=time.monotonic()
    with(p/(name+'.log')).open('wb')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
    steps.append(dict(name=name,command=base+command,exitCode=result.returncode,seconds=time.monotonic()-start))
    (p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n')
    print(name,result.returncode,flush=True)
    if result.returncode:
        (p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n')
        raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,freshBuild=True,sourceFiles=len(files),testTargets=4,physicalAcceptance=False),indent=2)+'\n')
