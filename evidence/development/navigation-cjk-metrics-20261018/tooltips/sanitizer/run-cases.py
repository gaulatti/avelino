from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;b=p.parent
assert json.loads((p/'result.json').read_text())['exitCode']==0
source=b/'tooltip-remount-green-v1/runtime'
output=p/'runtime';assert not output.exists();output.mkdir()
script=(source/'check.sh').read_text()
before='weston --backend=x11'
after='env ASAN_OPTIONS=detect_leaks=0:abort_on_error=1 UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 LD_LIBRARY_PATH=/probe/install/lib:/opt/qt/lib /probe/install/bin/weston --backend=x11'
assert script.count(before)==1;script=script.replace(before,after)
(output/'check.sh').write_text(script)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'runtime-inputs.json').write_text(json.dumps(dict(accepted=False,
    clientSha256=sha(source/'consumer-build/InstalledConsumer'),
    driverSha256=sha(output/'check.sh'),instrumentedServerOnly=True,
    installedFiles={str(f.relative_to(p/'install')):sha(f)for f in (p/'install').rglob('*')if f.is_file()}),indent=2)+'\n')
steps=[];detected=False
for attempt in range(1,41):
    command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0',
             '-v',str(source)+':/display-check:ro','-v',str(p/'install')+':/probe/install:ro',
             '-v',str(output)+':/diagnostic','-w','/display-check',
             'avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3',
             'bash','/diagnostic/check.sh','/diagnostic/attempt'+str(attempt)]
    started=time.monotonic()
    with(p/f'case{attempt}.log').open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
    trace=output/f'attempt{attempt}/weston-client.log'
    text=trace.read_text(errors='replace')if trace.exists()else''
    detected=any(marker in text for marker in ['ERROR: AddressSanitizer','runtime error:'])
    steps.append(dict(attempt=attempt,command=command,exitCode=result.returncode,seconds=time.monotonic()-started,sanitizerError=detected))
    (p/'runtime-commands.json').write_text(json.dumps(steps,indent=2)+'\n')
    print('sanitizer case',attempt,result.returncode,'memory error',detected,flush=True)
    if detected:break
(p/'runtime-result.json').write_text(json.dumps(dict(accepted=False,steps=steps,sanitizerError=detected,
    scope='Instrumented compositor diagnostic only; no full display or mirror acceptance'),indent=2)+'\n')
