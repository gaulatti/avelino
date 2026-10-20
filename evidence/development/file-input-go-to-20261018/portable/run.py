from pathlib import Path
import json,subprocess,time
p=Path(__file__).resolve().parent
image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3'
assert subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()=='sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8'
startup="from pathlib import Path; import os; assert not Path('/work/src/Avelino').exists(); assert not Path('/consumer-check/source').exists(); assert not Path('/consumer-check/consumer').exists(); assert not Path('/consumer-check/consumer-build/CMakeCache.txt').exists(); os.execv('./consumer-build/InstalledConsumer',['./consumer-build/InstalledConsumer','--file-input','--file-input-observe','--file-input-report','/consumer-check/output/light-text1-dpr1'])"
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p/'restored/runtime')+':/consumer-check','-w','/consumer-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-go-to-portable',image,'python3','-c',startup]
start=time.monotonic()
with(p/'run.log').open('wb')as log:done=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(accepted=False,command=command,exitCode=done.returncode,seconds=time.monotonic()-start,libraryAndConsumerSourcesAbsentAtRuntime=True),indent=2)+'\n')
print('Reconstructed runtime replay',done.returncode,flush=True);raise SystemExit(done.returncode)
