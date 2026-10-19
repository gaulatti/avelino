#!/usr/bin/env bash
set -euo pipefail
output="$1"
mkdir "$output"
runtime="$(mktemp -d)";chmod 700 "$runtime";export XDG_RUNTIME_DIR="$runtime"
xpid= wpid= client=
cleanup(){ for pid in "$client" "$wpid" "$xpid"; do if [[ -n "$pid" ]];then kill "$pid" 2>/dev/null || true;wait "$pid" 2>/dev/null || true;fi;done;rm -rf "$runtime"; }
trap cleanup EXIT
Xvfb -displayfd 3 -screen 0 640x480x24 -nolisten tcp -noreset 3>"$runtime/display" >"$output/xvfb.log" 2>&1 & xpid=$!
for ((i=0;i<100;i++));do [[ -s "$runtime/display" ]]&&break;kill -0 "$xpid";sleep 0.1;done
export DISPLAY=":$(cat "$runtime/display")";xdotool mousemove --sync 639 479
cat >"$runtime/weston.ini" <<'INI'
[shell]
panel-position=none
background-color=0xffdbe1e7
locking=false
INI
env ASAN_OPTIONS=detect_leaks=0:abort_on_error=1 UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 LD_LIBRARY_PATH="${WESTON_LIB:-/opt/weston-13.0.4/lib}:${WESTON_LIB:-/opt/weston-13.0.4/lib}/weston:/opt/qt/lib" "${WESTON_BIN:-/opt/weston-13.0.4/bin/weston}" --backend=x11 --renderer=pixman --width=480 --height=360 --socket=avelino-order --idle-time=0 --config="$runtime/weston.ini" --log="$output/weston.log" >"$output/weston-client.log" 2>&1 & wpid=$!
for ((i=0;i<100;i++));do [[ -S "$runtime/avelino-order" ]]&&break;kill -0 "$wpid";sleep 0.1;done
export WAYLAND_DISPLAY=avelino-order
./client "$output/ready.json" "$output/captured" >"$output/client.log" 2>&1 & client=$!
while [[ ! -f "$output/ready.json" ]];do
 if ! kill -0 "$client" 2>/dev/null;then code=0;wait "$client"||code=$?;client=;cat "$output/client.log";exit "$code";fi
 sleep 0.05
done
import -window root "$output/session.png"
touch "$output/captured"
wait "$client";client=
echo "Parent commit and later visible popup completed"
