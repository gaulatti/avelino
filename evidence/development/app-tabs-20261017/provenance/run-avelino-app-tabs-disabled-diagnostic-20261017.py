from pathlib import Path
import hashlib,json,shutil,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016';p=base/'app-tabs-disabled-diagnostic-v1';assert not p.exists();p.mkdir();prior=base/'app-tabs-operator-v1';shutil.copytree(prior/'install',p/'install');shutil.copy2(prior/'fixture-inputs.json',p/'fixture-inputs.json')
(p/'run.sh').write_text('''set -euo pipefail
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>/package/display >/package/xvfb.log 2>&1 &
xpid=$!;trap 'kill "$xpid";wait "$xpid" || true' EXIT
while [[ ! -s /package/display ]]; do kill -0 "$xpid";sleep .1;done
export DISPLAY=":$(cat /package/display)"
xdotool mousemove --sync 2559 1919
for protocol in offscreen xcb;do
 for phase in scaled disabled disabled-home enabled;do
  QT_QPA_PLATFORM="$protocol" QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 install/bin/AvelinoCatalog --fixture reference-case --case "app-tabs-operator-$phase" --case-definitions /package/fixture-inputs.json --dark --text-scale 1.5 --capture "/package/$protocol-$phase.png" >"/package/$protocol-$phase.log" 2>&1
 done
done
''')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();(p/'inputs.json').write_text(json.dumps({str(f.relative_to(p)):sha(f)for f in p.rglob('*')if f.is_file()},indent=2)+'\n')
c=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-app-tabs-disabled-diagnostic-v1','-v',str(p)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','bash','run.sh'];start=time.monotonic()
with (p/'run.log').open('w')as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=c,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(p.name,r.returncode);raise SystemExit(r.returncode)
