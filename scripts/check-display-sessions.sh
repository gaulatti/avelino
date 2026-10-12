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
Xvfb -displayfd 3 -screen 0 1280x1024x24 -nolisten tcp 3>"$runtime/display" >"$evidence/xvfb.log" 2>&1 &
xpid=$!
for ((i=0;i<100;i++)); do
  if [[ -s "$runtime/display" ]]; then break; fi
  kill -0 "$xpid"
  sleep 0.1
done
export DISPLAY=":$(cat "$runtime/display")"
xdpyinfo >"$evidence/x11-server.txt"
weston --version >"$evidence/weston-version.txt"
import -version >"$evidence/capture-tool-version.txt"
for protocol in xcb wayland; do
  if [[ "$protocol" == wayland ]]; then
    cat >"$runtime/weston.ini" <<'INI'
[shell]
panel-position=none
background-color=0xffdbe1e7
locking=false
INI
    weston --backend=x11 --renderer=pixman --width=1200 --height=900 --socket=avelino-wayland \
      --idle-time=0 --config="$runtime/weston.ini" --log="$evidence/weston.log" >"$evidence/weston-client.log" 2>&1 &
    wpid=$!
    for ((i=0;i<100;i++)); do
      if [[ -S "$runtime/avelino-wayland" ]]; then break; fi
      kill -0 "$wpid"
      sleep 0.1
    done
    [[ -S "$runtime/avelino-wayland" ]]
    export WAYLAND_DISPLAY=avelino-wayland
  fi
  for backend in software opengl; do
    for configuration in standard scaled; do
      prefix="$evidence/$protocol-$backend-$configuration"
      args=(--evidence "$prefix")
      export QT_SCALE_FACTOR=1
      if [[ "$configuration" == scaled ]]; then
        export QT_SCALE_FACTOR=2
        args+=(--dark --text-scale 1.5)
      fi
      if [[ "$backend" == software ]]; then
        export QT_QUICK_BACKEND=software
        unset QSG_RHI_BACKEND
      else
        unset QT_QUICK_BACKEND
        export QSG_RHI_BACKEND=opengl
      fi
      QT_QPA_PLATFORM="$protocol" consumer-build/InstalledConsumer "${args[@]}" >"$prefix.log" 2>&1 &
      client=$!
      for ((i=0;i<100;i++)); do
        if [[ -f "$prefix.json" ]]; then break; fi
        kill -0 "$client"
        sleep 0.1
      done
      [[ -f "$prefix.json" ]]
      # Capture the entire displayed output, including independent surfaces.
      # Wayland surfaces are composited by Weston into this X11 output.
      import -window root "$prefix-session.png"
      python3 - "$prefix" "$protocol" "$backend" "$configuration" <<'PY'
import hashlib, json, struct, sys
from pathlib import Path
prefix, protocol, backend, configuration = sys.argv[1:]
path = Path(prefix+'.json')
record = json.loads(path.read_text())
assert record['platform'] == protocol, record
assert record['graphicsApi'] == (1 if backend == 'software' else 3), record
assert record['dpr'] == (1 if configuration == 'standard' else 2), record
assert record['textScale'] == (1 if configuration == 'standard' else 1.5), record
assert record['appearance'] == ('light' if configuration == 'standard' else 'dark'), record
window_bytes = Path(prefix+'.png').read_bytes()
assert window_bytes[:8] == b'\x89PNG\r\n\x1a\n'
physical = struct.unpack('>II', window_bytes[16:24])
assert physical == (record['width']*record['dpr'], record['height']*record['dpr']), record
record.update({
    'environmentRecord': 'environment.json',
    'session': 'Xvfb X11' if protocol == 'xcb' else 'Weston Wayland nested on Xvfb X11',
    'sessionCaptureMethod': 'ImageMagick import -window root (full X11 output)',
    'physicalDisplay': False,
    'hardwareAcceleration': False,
    'sessionCapture': Path(prefix+'-session.png').name,
    'sessionCaptureSha256': hashlib.sha256(Path(prefix+'-session.png').read_bytes()).hexdigest(),
    'windowCaptureSha256': hashlib.sha256(Path(prefix+'.png').read_bytes()).hexdigest(),
})
path.write_text(json.dumps(record, indent=2)+'\n')
PY
      touch "$prefix.captured"
      wait "$client"
      client=
    done
  done
done
echo 'Installed consumer exercised X11 and nested Wayland with software and OpenGL renderers; mirror, overlays, physical input and accessibility remain pending.'
