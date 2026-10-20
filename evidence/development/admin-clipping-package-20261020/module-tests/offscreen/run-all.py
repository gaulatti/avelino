from pathlib import Path
import subprocess,sys,json
p=Path(__file__).resolve().parent
for scale in ["1","2"]:
 r=subprocess.run([sys.executable,str(p/"run.py"),scale])
 if r.returncode:sys.exit(r.returncode)
(p/"result.json").write_text(json.dumps({"exitCode":0,"scales":[1,2],"normalInstalledModuleImport":True,"sourceProjectsMounted":False,"productBuildMounted":False,"librarySourceOverlayProvided":False,"accepted":False},indent=2)+"\n")
