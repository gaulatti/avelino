#!/usr/bin/env bash
set -euo pipefail

output="${1:?fresh evidence directory required}"
expected_exit="${2:?expected exit status required}"
[[ "$expected_exit" == 0 || "$expected_exit" == 1 ]]
qt_prefix="${3:-/opt/qt}"
script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mkdir "$output"
output="$(cd -- "$output" && pwd)"
[[ -z "${LD_PRELOAD-}" ]]
work="$(mktemp -d)"
export XDG_RUNTIME_DIR="$work/runtime"
mkdir -m 700 "$XDG_RUNTIME_DIR"
xpid= wpid=
cleanup() {
    for pid in "$wpid" "$xpid"; do
        if [[ -n "$pid" ]]; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
    done
    rm -rf "$work"
}
trap cleanup EXIT
mkdir "$work/source"
cp "$script_directory/qt-software-rectangle.cpp" "$work/source/main.cpp"
cat >"$work/source/CMakeLists.txt" <<'CMAKE'
cmake_minimum_required(VERSION 3.24)
project(QtSoftwareRectangle LANGUAGES CXX)
find_package(Qt6 6.8.3 EXACT REQUIRED COMPONENTS Quick Test)
qt_standard_project_setup(REQUIRES 6.8)
qt_add_executable(QtSoftwareRectangle main.cpp)
target_link_libraries(QtSoftwareRectangle PRIVATE Qt6::Quick Qt6::Test)
CMAKE
cmake -S "$work/source" -B "$work/build" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$qt_prefix" >"$output/configure.log" 2>&1
cmake --build "$work/build" --parallel 2 >"$output/build.log" 2>&1

python3 - "$work/build/QtSoftwareRectangle" "$output" "$qt_prefix" <<'PY_BINARY'
import hashlib,json,sys
from pathlib import Path
binary,out,prefix=map(Path,sys.argv[1:])
record=dict(binarySha256=hashlib.sha256(binary.read_bytes()).hexdigest(),qtQuickSha256=hashlib.sha256((prefix/'lib/libQt6Quick.so.6.8.3').read_bytes()).hexdigest(),qtGuiSha256=hashlib.sha256((prefix/'lib/libQt6Gui.so.6.8.3').read_bytes()).hexdigest())
(out/'binary.json').write_text(json.dumps(record,indent=2)+'\n')
PY_BINARY

Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset \
    3>"$work/display" >"$output/xvfb.log" 2>&1 &
xpid=$!
for ((attempt=0;attempt<100;attempt++)); do
    [[ -s "$work/display" ]] && break
    kill -0 "$xpid"
    sleep 0.1
done
export DISPLAY=":$(cat "$work/display")"
export QT_QUICK_BACKEND=software LIBGL_ALWAYS_SOFTWARE=1
unset QSG_RHI_BACKEND
for platform in xcb wayland; do
    if [[ "$platform" == wayland ]]; then
        cat >"$work/weston.ini" <<'INI'
[shell]
panel-position=none
background-color=0xffdbe1e7
locking=false
INI
        weston --backend=x11 --renderer=pixman --width=2400 --height=1800 \
            --socket=avelino-rectangle --idle-time=0 --config="$work/weston.ini" \
            --log="$output/weston.log" >"$output/weston-client.log" 2>&1 &
        wpid=$!
        for ((attempt=0;attempt<100;attempt++)); do
            [[ -S "$XDG_RUNTIME_DIR/avelino-rectangle" ]] && break
            kill -0 "$wpid"
            sleep 0.1
        done
        [[ -S "$XDG_RUNTIME_DIR/avelino-rectangle" ]]
        export WAYLAND_DISPLAY=avelino-rectangle
    fi
    for dpr in 1 2; do
        status=0
        QT_QPA_PLATFORM="$platform" QT_SCALE_FACTOR="$dpr" \
            "$work/build/QtSoftwareRectangle" "$output/$platform-dpr$dpr" \
            >"$output/$platform-dpr$dpr.log" 2>&1 || status=$?
        [[ "$status" == "$expected_exit" ]]
    done
done
python3 - "$output" "$expected_exit" <<'PY_CHECK'
from pathlib import Path
import hashlib,json,sys
p=Path(sys.argv[1]);expected=int(sys.argv[2]);profiles=[]
for platform in ['xcb','wayland']:
 for dpr in [1,2]:
  q=p/f'{platform}-dpr{dpr}';r=json.loads((q/'result.json').read_text())
  assert r['qt']=='6.8.3' and r['platform']==platform and r['dpr']==dpr and r['graphicsApi']==1
  assert len(r['frames'])==120 and r['stabilityFailures']==r['alphaFailures']==0
  assert (r['floatingGeometryFailures']>0)==bool(expected)
  for f in r['frames']:
   assert f['stable'] and f['paintedPixels']>0 and f['nonOpaquePixels']==0
   assert hashlib.sha256((q/f['capture']).read_bytes()).hexdigest()==f['sha256']
   assert f['actualRect']==[7+f['shift'],8.5,30.5,f['height']]
   if f['kind']==0:
    assert hashlib.sha256((q/f['reference']).read_bytes()).hexdigest()==f['referenceSha256']
    if expected==0:assert f['changedPixels']==0
  profiles.append(dict(platform=platform,dpr=dpr,frames=120,geometryFailures=r['floatingGeometryFailures']))
(p/'result.json').write_text(json.dumps(dict(profiles=profiles,frames=480,floatingReferences=120,legacyFrames=360,expectedExit=expected,accepted=False),indent=2)+'\n')
print('Qt rectangle controls:480 captures,120 floating references,360 legacy-path controls')
PY_CHECK
