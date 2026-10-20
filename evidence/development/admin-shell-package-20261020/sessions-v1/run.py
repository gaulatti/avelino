from pathlib import Path
import subprocess,json,time
P=Path(__file__).resolve().parent
PACKAGE=Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-shell-compiled-v1/output/package')
command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(PACKAGE)+':/package','-w','/package','-e','LD_LIBRARY_PATH=/package/install/lib/qml/Avelino:/opt/weston-13.0.4/lib:/opt/qt/lib','sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7','bash','-euc','test ! -e /work/src; test ! -e /work/CMakeLists.txt; exec bash check-admin-sessions.sh /package/admin-sessions-v1']
start=time.monotonic()
with (P/'sessions.log').open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,sourceProjectsMounted=False,productBuildMounted=False,accepted=False),indent=2)+'\n')
print('installed Admin sessions',r.returncode,flush=True);raise SystemExit(r.returncode)
