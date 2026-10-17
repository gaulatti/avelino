#!/usr/bin/env bash
set -euo pipefail
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>/package/display >/package/xvfb.log 2>&1 &
xpid=$!
trap 'kill "$xpid" 2>/dev/null || true; wait "$xpid" 2>/dev/null || true' EXIT
while [[ ! -s /package/display ]]; do kill -0 "$xpid";sleep 0.1;done
export DISPLAY=":$(cat /package/display)"
xdotool mousemove --sync 2559 1919
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 install/bin/AvelinoCatalog --fixture reference-case --case surface-operator-radius48 --case-definitions /package/extra-input.json --capture /package/references/radius48.png >/package/reference.log 2>&1
export QT_QPA_PLATFORM=xcb QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1
consumer-build/InstalledConsumer --surface-modifier --evidence /package/client >/package/client.log 2>&1
