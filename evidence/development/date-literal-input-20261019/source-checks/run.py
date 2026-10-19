from pathlib import Path
import json, subprocess, time
p=Path(__file__).resolve().parent
rows=[]
for task in json.loads((p/'requested-commands.json').read_text()):
 t=time.monotonic()
 with (p/(task['name']+'.log')).open('w')as out:
  r=subprocess.run(task['command'],stdout=out,stderr=subprocess.STDOUT)
 row=dict(name=task['name'],command=task['command'],exitCode=r.returncode,seconds=time.monotonic()-t)
 rows.append(row);(p/'commands.json').write_text(json.dumps(rows,indent=2)+'\n');print(row['name'],r.returncode,flush=True)
 if r.returncode:break
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=r.returncode,checks=len(rows)),indent=2)+'\n')
raise SystemExit(r.returncode)
