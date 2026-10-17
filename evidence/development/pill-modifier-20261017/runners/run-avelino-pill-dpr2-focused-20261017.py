from pathlib import Path
import json,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016')
p=root/'pill-dpr2-focused-v1';assert not p.exists();p.mkdir()
b=root/'pill-build-v12'
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-pill-dpr2-focused-v1',
 '-v',str(b/'source')+':/work:ro','-v',str(b)+':/result:rw','-v',str(b/'qt-artifacts')+':/work/artifacts:rw',
 '-w','/work','avelino-toolchain:data-metrics-qt6.8.3','bash','-lc','QT_SCALE_FACTOR=2 QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /result/build/tests/components/AvelinoComponentTests -input /work/tests/components/tst_pill_modifier.qml -import /result/build/qml']
start=time.monotonic()
with (p/'run.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n')
print('Full pill regression',r.returncode);print((p/'run.log').read_text()[-3000:]);raise SystemExit(r.returncode)
