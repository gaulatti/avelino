from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];source=p.parent/'file-input-qt-v11/source/tests/consumer/native-file-input-witnesses.json';defs=json.loads(source.read_text())['fixtures'];base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(r)+':/work','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-file-input-runtime','--env','QML_IMPORT_PATH=/work/artifacts/resumed-avelino-20261016/file-input-build/build/qml','avelino-toolchain:data-metrics-qt6.8.3','/work/artifacts/resumed-avelino-20261016/file-input-build/build/samples/AvelinoCatalog/AvelinoCatalog'];steps=[]
for d in defs:
 name=d['fixture'];command=base+['--fixture','reference-case','--case',name,'--case-definitions','/work/'+str(source.relative_to(r)),'--capture','/work/'+str((p/(name+'.png')).relative_to(r))];start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n')
 if result.returncode:(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
print('catalog',len(steps),'cases',flush=True);(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,cases=len(steps)),indent=2)+'\n')
