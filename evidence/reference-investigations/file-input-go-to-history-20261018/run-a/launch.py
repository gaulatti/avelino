from pathlib import Path
import json,hashlib,subprocess,time
p=Path(__file__).resolve().parent
binary=Path('/Users/gaulatti/.codex/tmp/avelino-file-input-location-harness-20261017-v1/FileInputLocationA.app/Contents/MacOS/NativeFileInputUI')
digest=hashlib.sha256(binary.read_bytes()).hexdigest();assert digest=='974408b4e601503878562482be61f605d12bd82f0b8d8f2e005c1576f57fc025'
command=[str(binary),str(p/'output'),str(p/'fixtures'),str(p/'fixture.json')]
start=time.time()
with(p/'output/helper.log').open('wb')as log:
 child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
 (p/'launch.json').write_text(json.dumps(dict(command=command,executableSha256=digest,startedAt=start,pid=child.pid),indent=2)+'\n')
 print('Native GoTo probe',child.pid,flush=True);exit_code=child.wait()
(p/'result.json').write_text(json.dumps(dict(exitCode=exit_code,finishedAt=time.time()),indent=2)+'\n');raise SystemExit(exit_code)
