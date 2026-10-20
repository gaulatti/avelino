from pathlib import Path
import json,sys,subprocess,time
p=Path(__file__).resolve().parent
with (p/"matrix.log").open("x") as log:
 for platform in ["xcb","wayland"]:
  for backend in ["software","opengl"]:
   for scale in ["1","2"]:
    name=platform+"-"+backend+"-dpr"+scale
    (p/"phase.json").write_text(json.dumps({"context":name,"startedAt":time.time()},indent=2)+"\n")
    r=subprocess.run([sys.executable,str(p/"run-context.py"),scale,platform,backend],stdout=log,stderr=subprocess.STDOUT)
    print(name,r.returncode,flush=True)
    if r.returncode:
     (p/"result.json").write_text(json.dumps({"exitCode":r.returncode,"failedContext":name,"accepted":False},indent=2)+"\n");sys.exit(r.returncode)
(p/"result.json").write_text(json.dumps({"exitCode":0,"contexts":8,"moduleSourceRevision":"7253695c3e94b0626bcb0612fbc8467fe94445b5","testHarnessStagedTree":'5afbd19abc9f7697dafe6f06bf02fd5fba6edea2',"accepted":False},indent=2)+"\n")
