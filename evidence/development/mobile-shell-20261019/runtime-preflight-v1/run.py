from pathlib import Path
import subprocess,json,hashlib,time
P=Path(__file__).resolve().parent;ROOT=P.parents[2];BASE=P.parent
IMAGE='sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'
commands=[]
for dpr in [1,2]:
 command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(ROOT)+':/work:ro','-v',str(P)+':/probe:ro','-v',str(P/'output')+':/output','-v',str(BASE/'mobile-shell-library-v1/output/build')+':/work/build:ro','-e','QML_IMPORT_PATH=/work/build/linux/qml','-e','QT_QPA_PLATFORM=offscreen','-e','QT_QUICK_BACKEND=software','-e','QT_SCALE_FACTOR='+str(dpr),IMAGE,'qml','/probe/probe.qml']
 start=time.monotonic();result=subprocess.run(command,capture_output=True,text=True);(P/f'dpr{dpr}.log').write_text(result.stdout+result.stderr);commands.append(dict(command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(P/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');print('DPR',dpr,'exit',result.returncode,flush=True)
 if result.returncode:print((result.stdout+result.stderr)[-5000:],flush=True);raise SystemExit(result.returncode)
