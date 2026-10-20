from pathlib import Path
import json,time,subprocess,sys
p=Path(__file__).resolve().parent
steps=[('installed-test-matrix', '/Users/gaulatti/.codex/tmp/avelino-admin-clipping-installed-tests-20261020-v1/run-matrix.py'), ('installed-consumer-display-matrix', '/Users/gaulatti/.codex/tmp/avelino-admin-clipping-installed-sessions-20261020-v1/run.py')]
receipts=[]
for name,script in steps:
 (p/"phase.json").write_text(json.dumps({"phase":name,"startedAt":time.time()},indent=2)+"\n")
 r=subprocess.run([sys.executable,script]);receipts.append({"name":name,"exitCode":r.returncode})
 (p/"commands.json").write_text(json.dumps(receipts,indent=2)+"\n")
 if r.returncode:
  (p/"result.json").write_text(json.dumps({"exitCode":r.returncode,"failedPhase":name,"accepted":False},indent=2)+"\n");sys.exit(r.returncode)
(p/"result.json").write_text(json.dumps({"exitCode":0,"accepted":False},indent=2)+"\n")
