from pathlib import Path
import json,subprocess,time
base=Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016');p=base/'app-tabs-full-v1';assert not p.exists();p.mkdir();b=base/'app-tabs-build-v6';assert json.loads((b/'result.json').read_text())['exitCode']==0
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-app-tabs-full-v1','-v',str(b/'source')+':/work:ro','-v',str(b)+':/result:rw','-v',str(b/'qt-artifacts')+':/work/artifacts:rw','-w','/work','avelino-toolchain:data-metrics-qt6.8.3','bash','-lc','QT_SCALE_FACTOR=2 QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /result/build/tests/components/AvelinoComponentTests -input /work/tests/components/tst_app_tabs.qml -import /result/build/qml && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software ctest --test-dir /result/build -R "^app-tabs-" --output-on-failure && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software ctest --test-dir /result/build --output-on-failure']
start=time.monotonic()
with (p/'run.log').open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(p.name,r.returncode);print((p/'run.log').read_text()[-3000:]);raise SystemExit(r.returncode)
