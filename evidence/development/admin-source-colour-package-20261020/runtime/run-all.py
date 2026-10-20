from pathlib import Path
import subprocess,sys,json
p=Path(__file__).resolve().parent
for name,dpr,dark in [("light-dpr1","1",False),("dark-dpr1","1",True),("light-dpr2","2",False),("dark-dpr2","2",True)]:
 r=subprocess.run([sys.executable,str(p/"run.py"),name,dpr]+(["dark"] if dark else []))
 if r.returncode:sys.exit(r.returncode)
(p/"result.json").write_text(json.dumps({"exitCode":0,"contexts":4,"installedConsumerExecuted":True,"sourceProjectsMounted":False,"productBuildMounted":False,"accepted":False},indent=2)+"\n")
