#!/usr/bin/env bash
set -euo pipefail

output="${1:?fresh evidence directory required}"
qt_prefix="${2:-/opt/qt}"
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
cp "$script_directory/qt-software-opacity.cpp" "$work/source/main.cpp"
cat >"$work/source/CMakeLists.txt" <<'CMAKE'
cmake_minimum_required(VERSION 3.24)
project(QtSoftwareOpacity LANGUAGES CXX)
find_package(Qt6 6.8.3 EXACT REQUIRED COMPONENTS Quick Test)
qt_standard_project_setup(REQUIRES 6.8)
qt_add_executable(QtSoftwareOpacity main.cpp)
target_link_libraries(QtSoftwareOpacity PRIVATE Qt6::Quick Qt6::Test)
CMAKE
cmake -S "$work/source" -B "$work/build" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$qt_prefix" >"$output/configure.log" 2>&1
cmake --build "$work/build" --parallel 2 >"$output/build.log" 2>&1

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
            --socket=avelino-opacity --idle-time=0 --config="$work/weston.ini" \
            --log="$output/weston.log" >"$output/weston-client.log" 2>&1 &
        wpid=$!
        for ((attempt=0;attempt<100;attempt++)); do
            [[ -S "$XDG_RUNTIME_DIR/avelino-opacity" ]] && break
            kill -0 "$wpid"
            sleep 0.1
        done
        [[ -S "$XDG_RUNTIME_DIR/avelino-opacity" ]]
        export WAYLAND_DISPLAY=avelino-opacity
    fi
    for dpr in 1 2; do
        QT_QPA_PLATFORM="$platform" QT_SCALE_FACTOR="$dpr" \
            "$work/build/QtSoftwareOpacity" "$output/$platform-dpr$dpr" \
            >"$output/$platform-dpr$dpr.log" 2>&1
    done
done
python3 - "$output" "$script_directory/qt-software-opacity.cpp" <<'PY'
from pathlib import Path
import hashlib,json,struct,sys
root=Path(sys.argv[1]);profiles=[]
for platform in ['xcb','wayland']:
    for dpr in [1,2]:
        path=root/f'{platform}-dpr{dpr}'
        record=json.loads((path/'result.json').read_text())
        assert record['qt']=='6.8.3' and record['platform']==platform
        assert record['graphicsApi']==1 and record['dpr']==dpr
        assert record['windowColor']=='#ff102030' and not record['physicalDisplay']
        assert len(record['frames'])==30 and record['failedFrames']==0
        assert record['canvasRuntimeChecksPassed'] and len(record['canvasFrames'])==3
        assert {(r['clipped'],r['shift'],r['sample'])for r in record['frames']}=={
            (clip,shift,sample)for clip in [False,True]for shift in [0,0.25,0.5,0.75,1]for sample in range(3)}
        for row in record['frames']:
            assert row['nonOpaquePixels']==0 and row['paintedPixels']>0 and row['stable']
            data=(path/row['capture']).read_bytes()
            assert hashlib.sha256(data).hexdigest()==row['sha256']
            assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(160*dpr,100*dpr)
        assert {r['sample'] for r in record['canvasFrames']}=={0,1,2}
        for row in record['canvasFrames']:
            assert row['passed'] and row['stable'] and row['paintedPixels']==64*40*dpr*dpr
            data=(path/row['capture']).read_bytes()
            assert hashlib.sha256(data).hexdigest()==row['sha256']
            assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(64*dpr,40*dpr)
        profiles.append(dict(platform=platform,dpr=dpr,frames=30))
result=dict(qt='6.8.3',profiles=profiles,frames=120,canvasFrames=12,
            sourceSha256=hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),
            physicalDisplay=False,nativeAcceptance=False)
(root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print('Qt software opacity:120 opaque stable raw frames across X11/Wayland and DPR1/2')
PY
