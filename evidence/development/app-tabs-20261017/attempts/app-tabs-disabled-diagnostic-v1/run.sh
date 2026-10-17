set -euo pipefail
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
