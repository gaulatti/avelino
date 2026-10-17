#!/usr/bin/env bash
set -euo pipefail
python3 reference-driver.py
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>/package/display >/package/xvfb.log 2>&1 &
xpid=$!
client=
cleanup(){ if [[ -n "$client" ]]; then kill "$client" 2>/dev/null || true;wait "$client" 2>/dev/null || true;fi;kill "$xpid" 2>/dev/null || true;wait "$xpid" 2>/dev/null || true; }
trap cleanup EXIT
while [[ ! -s /package/display ]]; do kill -0 "$xpid";sleep .1;done
export DISPLAY=":$(cat /package/display)"
xdotool mousemove --sync 2559 1919
QT_QPA_PLATFORM=xcb QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 install/bin/AvelinoCatalog --fixture media-library >/package/client.log 2>&1 &
client=$!
touch /package/display-ready
while [[ ! -f /package/finished ]]; do kill -0 "$client";sleep .1;done
