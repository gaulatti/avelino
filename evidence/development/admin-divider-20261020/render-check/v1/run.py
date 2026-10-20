from pathlib import Path
import subprocess,json,time
P=Path(__file__).resolve().parent
PROBE=Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-source-colours-prototype-v1')
PACKAGE=Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-shell-compiled-v1/output/package')
base=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(PACKAGE)+':/package:ro','-v',str(PROBE)+':/probe','-w','/probe','-e','LD_LIBRARY_PATH=/package/install/lib/qml/Avelino:/opt/qt/lib','sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7']
steps=[('configure',['cmake','-S','/probe','-B','/probe/build','-GNinja','-DCMAKE_BUILD_TYPE=Debug']),('build',['cmake','--build','/probe/build','--parallel','2']),('capture',['env','QT_QPA_PLATFORM=offscreen','QT_QUICK_BACKEND=software','QT_SCALE_FACTOR=2','/opt/qt/bin/qmltestrunner','-import','/package/install/lib/qml','-input','/probe/tests','-o','-,txt']),('profile',['/probe/build/profile'])]
results=[]
for name,args in steps:
 command=base+args;start=time.monotonic()
 with (P/(name+'.log')).open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 results.append(dict(step=name,command=command,exitCode=r.returncode,seconds=time.monotonic()-start))
 (P/'commands.json').write_text(json.dumps(results,indent=2)+'\n')
 print(name,r.returncode,flush=True)
 if r.returncode:
  print((P/(name+'.log')).read_text()[-4500:],flush=True)
  break
(P/'result.json').write_text(json.dumps(dict(exitCode=results[-1]['exitCode'],steps=results,freshModuleCompilation=False,interpretedCallerFixture=True,physicalInput=False,accepted=False),indent=2)+'\n')
raise SystemExit(results[-1]['exitCode'])
