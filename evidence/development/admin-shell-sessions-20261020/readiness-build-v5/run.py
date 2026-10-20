from pathlib import Path
import subprocess,json,time,hashlib,sys
P=Path(__file__).resolve().parent;ROOT=Path('/Users/gaulatti/source/gaulatti/avelino')
OUT=ROOT/'artifacts/resumed-avelino-20261016/admin-shell-compiled-v1/output'
IMAGE='sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assert head==sys.argv[1]
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
files=['tests/consumer/adminshellchecks.h','tests/consumer/main.cpp','tests/consumer/AdminShell.qml','tests/consumer/AdminShellCase.qml','tests/consumer/CMakeLists.txt']
inputs={n:sha(ROOT/n) for n in files}
libs={str(f.relative_to(OUT/'build/linux')):sha(f) for f in [OUT/'build/linux/src/Avelino/libAvelino.so',OUT/'build/linux/qml/Avelino/libAvelinoplugin.so']}
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
write('inputs.json',dict(sourceRevision=head,sourceFiles=inputs,inheritedCoreLibraryHashes=libs,previousAttempt='/Users/gaulatti/.codex/tmp/avelino-admin-compiled-20261020-v1',coreLibraryChanged=False,accepted=False))
command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(ROOT)+':/work:ro','-v',str(OUT/'package')+':/package','-w','/work',IMAGE,'cmake','--build','/package/consumer-build','--parallel','2']
write('phase.json',dict(phase='consumer-build',startedAt=time.time()));start=time.monotonic()
with (P/'consumer-build.log').open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
write('command.json',dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start))
assert all(sha(ROOT/n)==h for n,h in inputs.items())
assert all(sha(OUT/'build/linux'/n)==h for n,h in libs.items())
write('artifacts.json',dict(consumerSha256=sha(OUT/'package/consumer-build/InstalledConsumer'),librarySha256=sha(OUT/'package/install/lib/qml/Avelino/libAvelino.so'),accepted=False))
write('result.json',dict(exitCode=r.returncode,sourceRevision=head,sourceInputsUnchanged=True,coreLibrariesUnchanged=True,consumerBuildPassed=r.returncode==0,installedConsumerExecuted=False,accepted=False))
print('consumer-build',r.returncode,flush=True);sys.exit(r.returncode)
