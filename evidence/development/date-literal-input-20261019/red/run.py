from pathlib import Path
import json,hashlib,subprocess,time
p=Path(__file__).resolve().parent;prefix=p.parent/'navigation-cjk-package-v2/runtime/install';image='avelino-toolchain:weston13-popup-parent-v2-20261018-qt6.8.3';steps=[]
for dpr in [1,2]:
 command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/tests:ro','-v',str(prefix)+':/runtime/install:ro','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','QT_SCALE_FACTOR='+str(dpr),image,'/opt/qt/bin/qmltestrunner','-input','/tests/tst_literal_hits.qml','-import','/runtime/install/lib/qml']
 start=time.monotonic()
 with(p/f'dpr{dpr}.log').open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(dpr=dpr,command=command,exitCode=r.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print('Literal hit red DPR',dpr,r.returncode,flush=True)
(p/'result.json').write_text(json.dumps(dict(accepted=False,steps=steps,testSha256=hashlib.sha256((p/'tst_literal_hits.qml').read_bytes()).hexdigest(),scope='New synthetic pointer contract on the unchanged installed module; red witness only'),indent=2)+'\n')
