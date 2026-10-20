import json,subprocess,time
from pathlib import Path
p=Path(__file__).resolve().parent
assert (p/'applied-patch.json').is_file()
command=['docker','--context','colima-avelino-verify','exec','avelino-qt-rectangle-experiment-20261019-v1','cmake','--build','/qt-build','--target','Quick','--parallel','1']
start=time.time()
(p/'build-command.json').write_text(json.dumps(dict(command=command,startedAt=start,parallel=1,experimentalOnly=True,productSdkChanged=False,accepted=False),indent=2)+'\n')
print('Building isolated Qt Quick rectangle experiment serially',flush=True)
with (p/'build.log').open('wb') as log: result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'build-result.json').write_text(json.dumps(dict(command=command,exitCode=result.returncode,seconds=time.time()-start,experimentalOnly=True,productSdkChanged=False,accepted=False),indent=2)+'\n')
print('Build exit',result.returncode,flush=True)
print('\n'.join((p/'build.log').read_text(errors='replace').splitlines()[-15:]),flush=True)
raise SystemExit(result.returncode)
