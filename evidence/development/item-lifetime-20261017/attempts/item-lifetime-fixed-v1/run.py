from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work']
for name in ['evidence','reference','scripts','tools','tokens','docs']:base+=['-v',str(r/name)+':/work/'+str((p/'source'/name).relative_to(r))+':ro']
base+=['-w','/work/'+str(p.relative_to(r)),'--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-item-lifetime','avelino-toolchain:data-metrics-qt6.8.3'];steps=[]
commands=[('configure',['cmake','-S','source','-B','build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug','-DBUILD_TESTING=ON','-DCMAKE_INSTALL_PREFIX=/work/'+str(p.relative_to(r))+'/install']),('build',['cmake','--build','build','--target','AvelinoItemLifetimeTests','AvelinoComponentTests','Avelinoplugin','AvelinoCatalog','--parallel','2']),('lifetime-tests',['ctest','--test-dir','build','-R','^item-lifetime(-dpr2)?$','--output-on-failure'])]
for dpr in [1,2]:commands.append(('qml-tests-dpr'+str(dpr),['env','QT_SCALE_FACTOR='+str(dpr),'./build/tests/components/AvelinoComponentTests','-import','/work/'+str((p/'build/qml').relative_to(r)),'-input','/work/'+str((p/'source/tests/components/tst_control_lifetime.qml').relative_to(r))]))
commands.append(('install',['cmake','--install','build']))
for name,command in commands:
 start=time.monotonic()
 with(p/(name+'.log')).open('wb')as log:result=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+chr(10));print(name,result.returncode,flush=True)
 if result.returncode:(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+chr(10));raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0),indent=2)+chr(10))
