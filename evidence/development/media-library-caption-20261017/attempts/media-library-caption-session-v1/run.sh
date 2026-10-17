set -euo pipefail
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>/package/display >/package/xvfb.log 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true' EXIT
while [[ ! -s /package/display ]]; do kill -0 "$pid";sleep .1;done
export DISPLAY=":$(cat /package/display)"
xdpyinfo >/package/display-info.txt
python3 driver.py
