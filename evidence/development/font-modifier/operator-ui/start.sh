#!/usr/bin/env bash
set -euo pipefail
Xvfb -displayfd 3 -screen 0 1600x1200x24 -nolisten tcp 3>/package/display >/package/xvfb.log 2>&1 &
xpid=$!
trap 'kill "$xpid" 2>/dev/null || true; wait "$xpid" 2>/dev/null || true' EXIT
while [[ ! -s /package/display ]]; do kill -0 "$xpid";sleep 0.1;done
export DISPLAY=":$(cat /package/display)"
export QT_QPA_PLATFORM=xcb QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1
consumer-build/InstalledConsumer --font-modifier --evidence /package/client >/package/client.log 2>&1
