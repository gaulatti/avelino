from pathlib import Path
import subprocess,sys,json
p=Path(__file__).resolve().parent
for platform in ["xcb","wayland"]:
 for backend in ["software","opengl"]:
  for scale in ["1","2"]:
   r=subprocess.run([sys.executable,str(p/"run-context.py"),scale,platform,backend])
   if r.returncode:sys.exit(r.returncode)
(p/"matrix-result.json").write_text(json.dumps({"exitCode":0,"contexts":8,"normalInstalledModuleImport":True,"sourceProjectsMounted":False,"productBuildMounted":False,"librarySourceOverlayProvided":False,"physicalInput":False,"readerAcceptance":False,"accepted":False},indent=2)+"\n")
