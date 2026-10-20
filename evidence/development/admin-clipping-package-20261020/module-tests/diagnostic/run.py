from pathlib import Path
import json,hashlib,io,tarfile,subprocess,time,sys
P=Path(__file__).resolve().parent
ROOT=Path('/Users/gaulatti/source/gaulatti/avelino')
PACKAGE=ROOT/'artifacts/resumed-avelino-20261016/admin-clipping-compiled-v1/output/package'
OUT=ROOT/'artifacts/resumed-avelino-20261016/admin-clipping-wayland-settle-diagnostic-v2'
BUILD=Path('/Users/gaulatti/.codex/tmp/avelino-admin-clipping-compiled-20261020-v1')
result=json.loads((BUILD/'result.json').read_text());inputs=json.loads((BUILD/'inputs.json').read_text());assert result['exitCode']==0
scale=sys.argv[1];platform=sys.argv[2];backend=sys.argv[3];name=platform+'-'+backend+'-dpr'+scale;assert scale in ['1','2'] and platform in ['xcb','wayland'] and backend in ['software','opengl'];assert not (P/(name+'.json')).exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=['tests/components/tst_admin_shell.qml','tests/components/native-admin-divider.js','tests/consumer/AdminShellCase.qml','tests/consumer/AdminShell.qml','tests/consumer/native-admin-shell-colours.js','tests/consumer/native-admin-shell-witnesses.json']
original={n:subprocess.check_output(['git','show',result['sourceRevision']+':'+n],cwd=ROOT) for n in files};assert all(hashlib.sha256(b).hexdigest()==inputs['sourceFiles'][n] for n,b in original.items())
payload=dict(original);payload['tests/components/witnesses.js']=b'var data = '+original['tests/consumer/native-admin-shell-witnesses.json']+b';\n'
f='tests/components/tst_admin_shell.qml';text=payload[f].decode()
needle='            verify(fixture); wait(30)'
assert text.count(needle)>0
probe='            verify(fixture); if (row.name === \"narrow-dark-True\") console.log(\"SETTLE_CREATED \" + JSON.stringify(fixture.snapshot())); wait(30)\n            if (row.name === "narrow-dark-True") {\n                console.log("SETTLE_FIRST " + JSON.stringify(fixture.snapshot()));\n                const polished = waitForPolish(fixture.Window.window);\n                console.log("SETTLE_POLISHED " + polished + " " + JSON.stringify(fixture.snapshot()));\n                wait(250);\n                console.log("SETTLE_LATER " + JSON.stringify(fixture.snapshot()));\n            }'
text=text.replace(needle,probe,1)
text=text.replace('import QtTest','import QtTest\nimport "witnesses.js" as Native',1).replace('    id: root','    id: root\n    property var nativeAdminShellWitnesses: Native.data',1)
text=text.replace('            const after = grabImage(host)','            const after = grabImage(host)\n            before.save("/evidence/'+name+'-before.png"); after.save("/evidence/'+name+'-after.png")',1);payload[f]=text.encode()
assert all(n.startswith('tests/') for n in payload)
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w') as archive:
 for n,b in payload.items():
  info=tarfile.TarInfo(n);info.size=len(b);archive.addfile(info,io.BytesIO(b))
(P/(name+'-payload.tar')).write_bytes(buf.getvalue())
script='test ! -e /work/src; test ! -e /work/CMakeLists.txt; mkdir /tmp/installed-admin; tar -xf - -C /tmp/installed-admin; test ! -e /tmp/installed-admin/src; sha256sum /avelino/lib/qml/Avelino/libAvelino.so; exec /opt/qt/bin/qmltestrunner -import /avelino/lib/qml -input /tmp/installed-admin/tests/components -o -,txt'
setup="""export XDG_RUNTIME_DIR=/tmp/installed-admin/runtime
mkdir -m 700 "$XDG_RUNTIME_DIR"
export LIBGL_ALWAYS_SOFTWARE=1
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>"$XDG_RUNTIME_DIR/display" >/tmp/installed-admin/xvfb.log 2>&1 &
xpid=$!
trap 'status=$?; cat /tmp/installed-admin/xvfb.log 2>/dev/null || true; kill "$xpid" 2>/dev/null || true; exit "$status"' EXIT
for ((i=0;i<100;i++)); do if [[ -s "$XDG_RUNTIME_DIR/display" ]]; then break; fi; kill -0 "$xpid"; sleep 0.05; done
export DISPLAY=":$(cat "$XDG_RUNTIME_DIR/display")"
xdotool mousemove --sync 2559 1919
"""
if platform=='wayland':
 setup+="""weston --backend=x11 --renderer=pixman --width=2400 --height=1800 --socket=installed-admin-wayland --idle-time=0 --no-config --log=/tmp/installed-admin/weston.log >/tmp/installed-admin/weston-client.log 2>&1 &
wpid=$!
trap 'status=$?; cat /tmp/installed-admin/weston.log /tmp/installed-admin/weston-client.log /tmp/installed-admin/xvfb.log 2>/dev/null || true; kill "$wpid" "$xpid" 2>/dev/null || true; exit "$status"' EXIT
for ((i=0;i<100;i++)); do if [[ -S "$XDG_RUNTIME_DIR/installed-admin-wayland" ]]; then break; fi; kill -0 "$wpid"; sleep 0.05; done
[[ -S "$XDG_RUNTIME_DIR/installed-admin-wayland" ]]
export WAYLAND_DISPLAY=installed-admin-wayland
"""
script=script.replace('sha256sum',setup+'sha256sum',1)
graphics=['-e','QT_QUICK_BACKEND=software'] if backend=='software' else ['-e','QSG_RHI_BACKEND=opengl']
command=['docker','--context','colima-avelino-verify','run','--init','--rm','-i','--ulimit','core=0','-v',str(PACKAGE/'install')+':/avelino:ro','-v',str(OUT)+':/evidence','-e','QT_QPA_PLATFORM='+platform,*graphics,'-e','QSG_INFO=1','-e','QT_SCALE_FACTOR='+scale,'-e','LD_LIBRARY_PATH=/avelino/lib/qml/Avelino:/opt/qt/lib',inputs['imageId'],'bash','-euc',script]
module=PACKAGE/'install/lib/qml/Avelino/libAvelino.so';before=sha(module);start=time.monotonic()
r=subprocess.run(command,input=buf.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(P/(name+'.log')).write_bytes(r.stdout);assert before==sha(module)
receipt={'command':command,'exitCode':r.returncode,'seconds':time.monotonic()-start,'sourceRevision':result['sourceRevision'],'platform':platform,'backend':backend,'hardwareAcceleration':False,'sourceInputHashes':{n:hashlib.sha256(b).hexdigest() for n,b in original.items()},'executedPayloadHashes':{n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},'librarySha256':before,'libraryQmldirSha256':sha(PACKAGE/'install/lib/qml/Avelino/qmldir'),'sourceProjectsMounted':False,'productBuildMounted':False,'diagnosticOnly':True,'waitForPolishObservationAdded':True,'librarySourceOverlayProvided':False,'libraryQmldirModified':False,'testFixtureSourcesSuppliedViaStdin':True,'nativeRasterAccepted':False,'accepted':False}
(P/(name+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(name,r.returncode,flush=True)
print('\n'.join(line for line in r.stdout.decode(errors='replace').splitlines() if not line.startswith('PASS   :')))
raise SystemExit(r.returncode)
