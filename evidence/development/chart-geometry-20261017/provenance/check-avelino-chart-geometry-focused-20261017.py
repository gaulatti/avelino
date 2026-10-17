from pathlib import Path
import json,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';P=B/'charts-geometry-focused-v1';assert not P.exists();P.mkdir();build=B/'charts-geometry-build-v5'
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-charts-geometry-focused-v1','-v',str(build/'source')+':/work:ro','-v',str(build)+':/result:rw','-v',str(build/'qt-artifacts')+':/work/artifacts:rw','-w','/work','avelino-toolchain:data-metrics-qt6.8.3','bash','-lc','QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR=2 /result/build/tests/components/AvelinoComponentTests -input /work/tests/components/tst_charts.qml -import /result/build/qml && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software ctest --test-dir /result/build -R "^charts-" --output-on-failure']
start=time.monotonic()
with (P/'run.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(P.name,r.returncode);print((P/'run.log').read_text()[-2300:]);raise SystemExit(r.returncode)
