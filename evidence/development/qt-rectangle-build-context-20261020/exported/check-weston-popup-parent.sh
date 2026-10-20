#!/usr/bin/env bash
set -euo pipefail
# Check a legal parent commit between get_popup and the popup's first commit.
# The later mapped popup must remain visible, with exact opaque SHM colors.
source_dir="$(cd "$(dirname "$0")" && pwd)"
if [[ $# -gt 0 ]]; then output="$1"; mkdir "$output"; else output="$(mktemp -d)"; fi
output="$(cd "$output" && pwd)"
work="$(mktemp -d)"
wayland-scanner client-header /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml "$work/xdg-shell-client-protocol.h"
wayland-scanner private-code /usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml "$work/xdg-shell-protocol.c"
cc -std=c11 -Wall -Wextra -Werror -I"$work" "$source_dir/weston-popup-order.c" "$work/xdg-shell-protocol.c" $(pkg-config --cflags --libs wayland-client) -o "$work/client"
cp "$source_dir/weston-popup-order.c" "$output/client.c"

runtime="$(mktemp -d)";chmod 700 "$runtime";export XDG_RUNTIME_DIR="$runtime"
xpid= wpid= client=
cleanup(){ for pid in "$client" "$wpid" "$xpid"; do if [[ -n "$pid" ]];then kill "$pid" 2>/dev/null || true;wait "$pid" 2>/dev/null || true;fi;done;rm -rf "$runtime" "$work"; }
trap cleanup EXIT
Xvfb -displayfd 3 -screen 0 640x480x24 -nolisten tcp -noreset 3>"$runtime/display" >"$output/xvfb.log" 2>&1 & xpid=$!
for ((i=0;i<100;i++));do [[ -s "$runtime/display" ]]&&break;kill -0 "$xpid";sleep 0.1;done
export DISPLAY=":$(cat "$runtime/display")";xdotool mousemove --sync 639 479
cat >"$runtime/weston.ini" <<'INI'
[shell]
panel-position=none
background-color=0xffdbe1e7
locking=false
startup-animation=none
close-animation=none
INI
env ASAN_OPTIONS=detect_leaks=0:abort_on_error=1 UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 LD_LIBRARY_PATH="${WESTON_LIB:-/opt/weston-13.0.4/lib}:${WESTON_LIB:-/opt/weston-13.0.4/lib}/weston:/opt/qt/lib" "${WESTON_BIN:-/opt/weston-13.0.4/bin/weston}" --backend=x11 --renderer=pixman --width=480 --height=360 --socket=avelino-order --idle-time=0 --config="$runtime/weston.ini" --log="$output/weston.log" >"$output/weston-client.log" 2>&1 & wpid=$!
for ((i=0;i<100;i++));do [[ -S "$runtime/avelino-order" ]]&&break;kill -0 "$wpid";sleep 0.1;done
export WAYLAND_DISPLAY=avelino-order
"$work/client" "$output/ready.json" "$output/captured" >"$output/client.log" 2>&1 & client=$!
while [[ ! -f "$output/ready.json" ]];do
 if ! kill -0 "$client" 2>/dev/null;then code=0;wait "$client"||code=$?;client=;cat "$output/client.log";exit "$code";fi
 sleep 0.05
done
import -window root "$output/session.png"
touch "$output/captured"
wait "$client";client=
convert "$output/session.png" -alpha off -depth 8 -format %c "histogram:info:$output/colors.txt"
python3 - "$output" <<'PYVERIFY'
import hashlib,json,re,sys
from pathlib import Path
p=Path(sys.argv[1]);ready=json.loads((p/'ready.json').read_text())
assert ready['parentCommitsBeforeFirstPopupCommit']==1 and ready['popupConfigured'] and ready['popupFrame']
colors={m.group(2).upper():int(m.group(1))for line in (p/'colors.txt').read_text().splitlines()if (m:=re.match(r'\s*(\d+):.*#([A-Fa-f0-9]{6})\b',line))}
assert colors.get('D32F2F')==400,colors
assert colors.get('1976D2')==9600,colors
trace=(p/'weston-client.log').read_text()
assert 'runtime error:' not in trace and 'ERROR: AddressSanitizer' not in trace
result=dict(accepted=False,status='passed',parentCommitsBeforeFirstPopupCommit=1,popupConfigured=True,popupFrame=True,popupPixels=400,parentPixels=9600,sessionCaptureSha256=hashlib.sha256((p/'session.png').read_bytes()).hexdigest(),clientSourceSha256=hashlib.sha256((p/'client.c').read_bytes()).hexdigest(),scope='Weston protocol-order regression; no mirror acceptance')
(p/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print('Weston popup parent-order regression: parent commit survived; popup400 and parent9600 exact pixels')
PYVERIFY
