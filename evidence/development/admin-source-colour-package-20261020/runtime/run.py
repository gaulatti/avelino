from pathlib import Path
import subprocess,json,time,hashlib,sys
P=Path(__file__).resolve().parent
PACKAGE=Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-source-colour-compiled-v1/output/package')
IMAGE='sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7'
build=json.loads(Path('/Users/gaulatti/.codex/tmp/avelino-admin-source-colour-compiled-20261020-v1/result.json').read_text())
assert build['exitCode']==0 and build['freshConsumerBuild']
assert (PACKAGE/'consumer-build/InstalledConsumer').is_file()
name=sys.argv[1];scale=sys.argv[2] if len(sys.argv)>2 else '1';dark=len(sys.argv)>3 and sys.argv[3]=='dark'
assert not (P/(name+'.json')).exists()
(PACKAGE/'reports').mkdir(exist_ok=True)
args=['--admin-shell','--admin-shell-report','/package/reports/'+name]+(['--dark'] if dark else [])
script='test ! -e /work/src; test ! -e /work/CMakeLists.txt; exec /package/consumer-build/InstalledConsumer "$@"'
command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(PACKAGE)+':/package','-w','/package','-e','QT_QPA_PLATFORM=offscreen','-e','QT_QUICK_BACKEND=software','-e','QT_SCALE_FACTOR='+scale,IMAGE,'bash','-euc',script,'admin-runtime',*args]
start=time.monotonic()
with (P/(name+'.log')).open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
result=dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,sourceProjectsMounted=False,productBuildMounted=False,consumerSha256=hashlib.sha256((PACKAGE/'consumer-build/InstalledConsumer').read_bytes()).hexdigest(),librarySha256=hashlib.sha256((PACKAGE/'install/lib/qml/Avelino/libAvelino.so').read_bytes()).hexdigest(),sourceRevision=build['sourceRevision'],accepted=False)
(P/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(name,r.returncode,flush=True)
sys.exit(r.returncode)
