from pathlib import Path
import io,tarfile,subprocess,json,hashlib,sys,time
P=Path(__file__).resolve().parent
ROOT=Path('/Users/gaulatti/.codex/tmp/avelino-reference-repair-20261020-v1')
attempt=int(sys.argv[1]);scale=sys.argv[2] if len(sys.argv)>2 else '1';platform=sys.argv[3] if len(sys.argv)>3 else 'offscreen'
assert platform in ['offscreen','xcb','wayland']
assert not (P/f'run-v{attempt}.json').exists()
files=['src/Avelino/BleeckerAdminShell.qml','src/Avelino/DesktopNavigationToolbar.qml','src/Avelino/DesktopSidebarGlyph.qml','tests/consumer/AdminShellCase.qml','tests/consumer/AdminShell.qml','tests/components/tst_admin_shell.qml','tests/consumer/native-admin-shell-witnesses.json','tests/components/native-admin-divider.js']
snapshot=P/f'inputs-v{attempt}';snapshot.mkdir()
original={n:(ROOT/n).read_bytes() for n in files}
for n,b in original.items():
 f=snapshot/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
payload=dict(original)
witnesses=original['tests/consumer/native-admin-shell-witnesses.json']
payload['tests/components/witnesses.js']=b'var data = '+witnesses+b';\n'
name='tests/components/tst_admin_shell.qml';raw=payload[name].decode();assert raw.count('    id: root')==1
raw=raw.replace('import QtTest','import QtTest\nimport "witnesses.js" as Native',1).replace('    id: root','    id: root\n    property var nativeAdminShellWitnesses: Native.data',1);payload[name]=raw.encode()
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w') as archive:
 for n,b in payload.items():
  info=tarfile.TarInfo(n);info.size=len(b);archive.addfile(info,io.BytesIO(b))
script="""set -e
mkdir -p /tmp/admin/overlay/Avelino
tar -xf - -C /tmp/admin
for f in /avelino/lib/qml/Avelino/*; do
  name=${f##*/}
  if [[ "$name" != qmldir && "$name" != BleeckerAdminShell.qml && "$name" != DesktopNavigationToolbar.qml && "$name" != DesktopSidebarGlyph.qml ]]; then ln -s "$f" "/tmp/admin/overlay/Avelino/$name"; fi
done
sed '/^prefer /d' /avelino/lib/qml/Avelino/qmldir > /tmp/admin/overlay/Avelino/qmldir
cp /tmp/admin/src/Avelino/*.qml /tmp/admin/overlay/Avelino/
/opt/qt/bin/qmltestrunner -import /tmp/admin/overlay -input /tmp/admin/tests/components -o -,txt
"""
if platform != 'offscreen':
 setup="""export XDG_RUNTIME_DIR=/tmp/admin/runtime
mkdir -m 700 "$XDG_RUNTIME_DIR"
export LIBGL_ALWAYS_SOFTWARE=1
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>"$XDG_RUNTIME_DIR/display" >/tmp/admin/xvfb.log 2>&1 &
xpid=$!
trap 'status=$?; cat /tmp/admin/xvfb.log 2>/dev/null || true; kill "$xpid" 2>/dev/null || true; exit "$status"' EXIT
for ((i=0;i<100;i++)); do if [[ -s "$XDG_RUNTIME_DIR/display" ]]; then break; fi; kill -0 "$xpid"; sleep 0.05; done
export DISPLAY=:"$(cat "$XDG_RUNTIME_DIR/display")"
xdotool mousemove --sync 2559 1919
xdpyinfo | head -n 12
"""
 if platform == 'wayland':
  setup+="""weston --backend=x11 --renderer=pixman --width=2400 --height=1800 --socket=admin-wayland --idle-time=0 --no-config --log=/tmp/admin/weston.log >/tmp/admin/weston-client.log 2>&1 &
wpid=$!
trap 'status=$?; cat /tmp/admin/weston.log /tmp/admin/weston-client.log /tmp/admin/xvfb.log 2>/dev/null || true; kill "$wpid" "$xpid" 2>/dev/null || true; exit "$status"' EXIT
for ((i=0;i<100;i++)); do if [[ -S "$XDG_RUNTIME_DIR/admin-wayland" ]]; then break; fi; kill -0 "$wpid"; sleep 0.05; done
[[ -S "$XDG_RUNTIME_DIR/admin-wayland" ]]
export WAYLAND_DISPLAY=admin-wayland
weston --version
"""
 script=script.replace('/opt/qt/bin/qmltestrunner',setup+'/opt/qt/bin/qmltestrunner',1)
command=['docker','--context','colima-avelino-verify','run','--rm','-i','--ulimit','core=0','-e','QT_QPA_PLATFORM='+platform,'-e','QT_QUICK_BACKEND=software','-e','QT_SCALE_FACTOR='+scale,'-e','LD_LIBRARY_PATH=/avelino/lib/qml/Avelino:/opt/qt/lib','-v','/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-shell-compiled-v1/output/package/install:/avelino:ro','sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7','bash','-euc',script]
start=time.monotonic();r=subprocess.run(command,input=buf.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(P/f'run-v{attempt}.log').write_bytes(r.stdout)
(P/f'run-v{attempt}.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,sourceInputHashes={n:hashlib.sha256(b).hexdigest() for n,b in original.items()},executedPayloadHashes={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},contextAdapter='Same witness JSON supplied as a QML property in place of the compiled test main context',freshCompilation=False,accepted=False),indent=2)+'\n')
print('\n'.join(line for line in r.stdout.decode(errors='replace').splitlines() if not line.startswith('PASS   :')))
sys.exit(r.returncode)
