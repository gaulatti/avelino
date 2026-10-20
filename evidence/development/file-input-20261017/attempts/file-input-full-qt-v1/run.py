from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];work=p.parent/'file-input-build';producer=p.parent/'file-input-qt-v11';assert json.loads((producer/'result.json').read_text())['exitCode']==0
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work']
for name in ['evidence','reference','scripts','tools','tokens','docs']:
 base+=['-v',str(r/name)+':/work/'+str((work/'source'/name).relative_to(r))+':ro']
base+=['-w','/work/'+str((work/'source').relative_to(r)),'--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-file-input-runtime','avelino-toolchain:data-metrics-qt6.8.3']
(p/'inputs.json').write_text(json.dumps(dict(accepted=False,producer=str(producer),immutableCodeSource=str(producer/'source'),readOnlyOracleFolders=['evidence','reference','scripts','tools','tokens','docs'],steps='full module build and all Qt CTest targets'),indent=2)+'\n');steps=[]
for name,command in [('configure',['cmake','-S','.','-B','../build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug','-DBUILD_TESTING=ON','-DAVELINO_FILE_INPUT_EVIDENCE_DIR=/work/'+str(p.relative_to(r))+'/ui-output']),('build',['cmake','--build','../build','--parallel','2']),('all-qt-tests',['ctest','--test-dir','../build','--output-on-failure'])]:
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0),indent=2)+'\n')
