from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import time

root=Path(__file__).resolve().parent
artifact=Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/atomic-token-document-v1')
artifact.mkdir()
source=artifact/'source';output=artifact/'output'
source.mkdir();output.mkdir()
for name in ['CMakeLists.txt','main.cpp','run-inside.sh']:shutil.copy2(root/name,source/name)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
hashes={p.name:sha(p) for p in source.iterdir() if p.is_file()}
command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0',
    '--mount',f'type=bind,source={source},target=/prototype,readonly',
    '--mount',f'type=bind,source={output},target=/output',
    '-e','QT_QPA_PLATFORM=offscreen','-e','QT_QUICK_BACKEND=software',
    'sha256:c32e246cda73ab6992d808ceb551fa569fdf8ee85308f82d2bf1b15a96e69b14',
    'bash','/prototype/run-inside.sh']
(root/'inputs.json').write_text(json.dumps({'command':command,'sourceFiles':hashes,'source':str(source),
    'output':str(output),'productionLibraryMounted':False,'productionConsumerMounted':False,
    'registeredInAvelino':False,'accepted':False},indent=2)+'\n')
started=time.monotonic()
with (root/'run.log').open('w') as log:process=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
runtime=json.loads((output/'runtime.json').read_text()) if (output/'runtime.json').exists() else None
result={'recordedAt':datetime.now(timezone.utc).isoformat(),'exitCode':process.returncode,
    'seconds':time.monotonic()-started,'sourceUnchanged':all(sha(source/name)==checksum for name,checksum in hashes.items()),
    'runtime':runtime,'productionImplementationChanged':False,'accepted':False}
(root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
raise SystemExit(process.returncode)
