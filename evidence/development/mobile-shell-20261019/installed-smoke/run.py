from pathlib import Path
import hashlib,json,subprocess,time
P=Path(__file__).resolve().parent;BASE=P.parent;ROOT=P.parents[2];RUNTIME=BASE/'mobile-shell-runtime-v3/runtime'
assert json.loads((BASE/'mobile-shell-runtime-v3/result.json').read_text())['exitCode']==0
OUTPUT=P/'output';OUTPUT.mkdir();source=ROOT/'scripts/check-installed.sh'
lines=[line for line in source.read_text().splitlines() if line.startswith('QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer')]
assert len(lines)==43,len(lines)
transformed=[line.replace('consumer-build/InstalledConsumer','/package/consumer-build/InstalledConsumer').replace('$date_checks_dir','/output/date').replace('$hero_checks_dir','/output/hero') for line in lines]
script='set -euo pipefail\nmkdir -p /output/date /output/hero\n'+ '\n'.join(transformed)+'\n'
(P/'commands.sh').write_text(script)
command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(RUNTIME)+':/package:ro','-v',str(OUTPUT)+':/output','-v',str(P/'commands.sh')+':/commands.sh:ro','-w','/package','sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3','bash','/commands.sh']
start=time.monotonic()
with (P/'smoke.log').open('x') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
result=dict(exitCode=r.returncode,seconds=time.monotonic()-start,source='scripts/check-installed.sh',sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),originalCommands=lines,executedCommands=transformed,command=command,sourceProjectsMounted=False,consumerSmokeCommands=len(lines),otherInstalledScriptStepsExecuted=False,accepted=False)
(P/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('installed smoke',r.returncode,len(lines));raise SystemExit(r.returncode)
