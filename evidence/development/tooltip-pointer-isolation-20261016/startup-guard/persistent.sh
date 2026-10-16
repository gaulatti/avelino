#!/usr/bin/env bash
set -euo pipefail
# Execute in the installed-package-only container after check-installed.sh.
evidence="${1:-$PWD/display-evidence}"
# Refuse stale readiness markers or capture overwrites from an earlier run.
mkdir "$evidence"
cp environment.json "$evidence/environment.json"
runtime="$(mktemp -d)"
chmod 700 "$runtime"
export XDG_RUNTIME_DIR="$runtime"
export LIBGL_ALWAYS_SOFTWARE=1
export QSG_INFO=1
xpid= wpid= client=
cleanup() {
  for pid in "$client" "$wpid" "$xpid"; do
    if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fi
  done
  rm -rf "$runtime"
}
trap cleanup EXIT
# Keep the largest gallery (1100 x 850 logical units) within the output at DPR 2.
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>"$runtime/display" >"$evidence/xvfb.log" 2>&1 &
xpid=$!
for ((i=0;i<100;i++)); do
  if [[ -s "$runtime/display" ]]; then break; fi
  kill -0 "$xpid"
  sleep 0.1
done
export DISPLAY=":$(cat "$runtime/display")"
# These consumers drive Qt's synthetic pointer independently of the native
# cursor. Keep that cursor outside every client and the nested compositor so
# mapping a popup cannot inject an unrelated native Enter/Leave into the test.
# -noreset retains this position when the last X11 client disconnects.
xdotool mousemove --sync 2559 1919
xdotool getmouselocation --shell >"$evidence/native-pointer.txt"
python3 - "$evidence/native-pointer.txt" <<'PY'
from pathlib import Path
import sys
position = dict(line.split('=', 1) for line in Path(sys.argv[1]).read_text().splitlines())
assert (position['X'], position['Y'], position['SCREEN']) == ('2559', '1919', '0'), position
PY
