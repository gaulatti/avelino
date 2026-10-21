#!/usr/bin/env bash
set -euo pipefail
# Run from an installed-consumer runtime directory with no project sources.
evidence="${1:?fresh output directory required}"
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
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>"$runtime/display" >"$evidence/xvfb.log" 2>&1 &
xpid=$!
for ((i=0;i<100;i++)); do
  if [[ -s "$runtime/display" ]]; then break; fi
  kill -0 "$xpid"
  sleep 0.1
done
export DISPLAY=":$(cat "$runtime/display")"
xdotool mousemove --sync 2559 1919
xdotool getmouselocation --shell >"$evidence/native-pointer.txt"
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
    weston --backend=x11 --renderer=pixman --width=2400 --height=1800 --socket=avelino-wayland \
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
      args=(--file-input --file-input-search --evidence "$prefix")
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
      QT_QPA_PLATFORM="$protocol" python3 run-file-search.py consumer-build/InstalledConsumer "${args[@]}" >"$prefix.log" 2>&1 &
      client=$!
      readiness_started=$SECONDS
      readiness_notice=$((SECONDS+30))
      while [[ ! -f "$prefix.json" ]]; do
        if ! kill -0 "$client" 2>/dev/null; then
          result=0
          wait "$client" || result=$?
          client=
          cat "$prefix.log" >&2
          echo "FileInput search consumer exited $result before producing $prefix.json" >&2
          exit 1
        fi
        if ((SECONDS>=readiness_notice)); then
          echo "Waiting $((SECONDS-readiness_started))s for live consumer $client: $prefix" >&2
          readiness_notice=$((SECONDS+30))
        fi
        sleep 0.1
      done
      import -window root "$prefix-session.png"
      python3 - "$prefix" "$protocol" "$backend" "$configuration" <<'PY'
import hashlib, json, struct, sys
from pathlib import Path
prefix, protocol, backend, configuration = sys.argv[1:]
path = Path(prefix + '.json')
record = json.loads(path.read_text())
assert record['fixture'] == 'file-input-search' and record['accepted'] is False
assert record['platform'] == protocol and record['graphicsApi'] == (1 if backend == 'software' else 3)
assert record['structuralChecks'] == 'passed' and record['providerUnavailable'] is False
standard = configuration == 'standard'
assert record['dpr'] == (1 if standard else 2) and record['textScale'] == (1 if standard else 1.5)
assert record['appearance'] == ('light' if standard else 'dark')
phases = record['phases']
expected = ['global','folder','filename','token-replacement','token-undo','token-redo','compound-mixed','compound-everything','compound-replacement','compound-undo','compound-redo','selected','owner-result','cancelled-query','session-selected']
assert [p['phase'] for p in phases] == expected
assert all(not p['busy'] and not p['error'] for p in phases)
rows = {phase['phase']: phase for phase in phases}
assert 'pine-only.txt' in rows['global']['names'] and 'pine-peer.txt' in rows['global']['names']
assert 'pine-peer.txt' not in rows['folder']['names'] and 'avelinoulnacerulean-child.txt' in rows['folder']['names']
assert rows['filename']['expression'] == [{'kind':'token','mode':'filename','query':'avelinoulnacerulean'}]
assert 'pine-only.txt' not in rows['filename']['names']
replacement = [{'kind':'text','text':'avelinoulnacerulean-name'}]
assert rows['token-replacement']['expression'] == rows['token-redo']['expression'] == replacement
assert rows['token-undo']['expression'] == rows['filename']['expression'] and rows['token-undo']['selectedText'] == '\ufffc'
compound = [{'kind':'token','mode':'everything','query':'avelinoulnacerulean'},{'kind':'token','mode':'filename','query':'pine'}]
assert rows['compound-mixed']['expression'] == compound
assert rows['compound-mixed']['names'] == rows['compound-everything']['names'] == ['pine-only.txt']
both = [compound[0], {'kind':'token','mode':'everything','query':'pine'}]
assert rows['compound-everything']['expression'] == rows['compound-undo']['expression'] == rows['selected']['expression'] == both
assert rows['compound-undo']['selectedText'] == '\ufffc'
assert rows['compound-replacement']['expression'] == rows['compound-redo']['expression'] == [{'kind':'text','text':'name'}, both[1]]
assert rows['session-selected']['expression'] == [compound[0]] and 'pine-only.txt' in rows['session-selected']['names']
assert rows['session-selected']['folderOnly'] is True
for key in ['nativeRasterAccepted','readerAcceptance','physicalInput']:
    assert record[key] is False
final_image = Path(prefix + '.png')
image_bytes = final_image.read_bytes()
assert image_bytes[:8] == b'\x89PNG\r\n\x1a\n'
physical = struct.unpack('>II', image_bytes[16:24])
assert physical[0] > 0 and physical[1] > 0
session_image = Path(prefix + '-session.png')
session_bytes = session_image.read_bytes()
session_size = struct.unpack('>II', session_bytes[16:24])
assert session_size == (2560, 1920)
client_output = (2560, 1920) if protocol == 'xcb' else (2400, 1800)
assert physical[0] + 40 <= client_output[0] and physical[1] + 60 <= client_output[1]
record['displaySession'] = dict(session='Xvfb X11' if protocol == 'xcb' else 'Weston Wayland nested on Xvfb X11',
    sessionCaptureMethod='ImageMagick import -window root (full X11 output)',
    physicalDisplay=False, hardwareAcceleration=False, physicalInput=False,
    nativePointerControl='parked outside clients; caller input is synthetic Qt input',
    sessionOutputSize=list(session_size), clientOutputSize=list(client_output),
    sessionCapture=session_image.name, sessionCaptureSha256=hashlib.sha256(session_bytes).hexdigest(),
    finalWindowCapture=final_image.name, finalWindowCaptureSha256=hashlib.sha256(image_bytes).hexdigest())
path.write_text(json.dumps(record, indent=2) + '\n')
PY
      touch "$prefix.captured"
      wait "$client"
      client=
    done
  done
done
echo 'FileInput search: eight virtual X11/Wayland and software/OpenGL profiles; parity and physical acceptance pending.'
