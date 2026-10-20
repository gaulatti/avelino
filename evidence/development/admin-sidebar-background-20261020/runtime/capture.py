from pathlib import Path
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import time

P = Path(__file__).resolve().parent
ROOT = Path('/Users/gaulatti/.codex/tmp/avelino-reference-repair-20261020-v1')
OUT = Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-sidebar-background-v1')
PACKAGE = Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-shell-compiled-v1/output/package/install')
scale = int(sys.argv[1])
assert scale in (1, 2)
destination = OUT / f'dpr{scale}'
destination.mkdir(parents=True, exist_ok=False)
names = ['src/Avelino/BleeckerAdminShell.qml', 'src/Avelino/DesktopNavigationToolbar.qml',
         'src/Avelino/DesktopSidebarGlyph.qml', 'tests/consumer/AdminShellCase.qml',
         'tests/consumer/native-admin-shell-witnesses.json']
payload = {n: (ROOT / n).read_bytes() for n in names}
payload['tests/components/witnesses.js'] = b'var data = ' + payload[names[-1]] + b';\n'
payload['tests/components/tst_background_capture.qml'] = b'''import QtQuick
import QtTest
import Avelino
import "../consumer" as Fixtures
import "witnesses.js" as Native
Item {
    id: root
    width: 1100; height: 700
    Component { id: factory; Fixtures.AdminShellCase {} }
    TestCase {
        name: "AdminSidebarBackgroundCapture"
        when: windowShown
        function test_capture_data() {
            return Native.data.profiles.filter(row => row.definition.id === "standard" && row.initial)
                .map(row => Object.assign({tag:row.name}, row))
        }
        function test_capture(row) {
            BleeckerTheme.dark = row.dark
            const fixture = createTemporaryObject(factory, root, {definition:row.definition, initial:true})
            verify(fixture); wait(40)
            const background = findChild(fixture, "bleeckerAdminSidebarBackground")
            verify(background.visible)
            const p = background.mapToItem(fixture, 0, 0)
            compare(p.x, 44); compare(p.y, 0)
            compare(background.width, 212); compare(background.height, 500)
            let finished = false, saved = false
            verify(fixture.grabToImage(function(result) {
                saved = result.saveToFile("/capture/" + row.name + ".png"); finished = true
            }))
            tryVerify(function() { return finished }, 5000)
            verify(saved)
        }
    }
}
'''
snapshot = P / f'capture-inputs-dpr{scale}'
snapshot.mkdir()
for name, raw in payload.items():
    path = snapshot / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
buffer = io.BytesIO()
with tarfile.open(fileobj=buffer, mode='w') as archive:
    for name, raw in payload.items():
        info = tarfile.TarInfo(name); info.size = len(raw)
        archive.addfile(info, io.BytesIO(raw))
script = '''set -e
mkdir -p /tmp/admin/overlay/Avelino
tar -xf - -C /tmp/admin
for f in /avelino/lib/qml/Avelino/*; do
  name=${f##*/}
  case "$name" in qmldir|BleeckerAdminShell.qml|DesktopNavigationToolbar.qml|DesktopSidebarGlyph.qml) continue;; esac
  ln -s "$f" "/tmp/admin/overlay/Avelino/$name"
done
sed '/^prefer /d' /avelino/lib/qml/Avelino/qmldir > /tmp/admin/overlay/Avelino/qmldir
cp /tmp/admin/src/Avelino/*.qml /tmp/admin/overlay/Avelino/
/opt/qt/bin/qmltestrunner -import /tmp/admin/overlay -input /tmp/admin/tests/components -o -,txt
'''
command = ['docker', '--context', 'colima-avelino-verify', 'run', '--rm', '-i', '--ulimit', 'core=0',
           '-e', 'QT_QPA_PLATFORM=offscreen', '-e', 'QT_QUICK_BACKEND=software',
           '-e', f'QT_SCALE_FACTOR={scale}', '-e', 'LD_LIBRARY_PATH=/avelino/lib/qml/Avelino:/opt/qt/lib',
           '-v', str(PACKAGE) + ':/avelino:ro', '-v', str(destination) + ':/capture',
           'sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7', 'bash', '-euc', script]
start = time.monotonic()
result = subprocess.run(command, input=buffer.getvalue(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(P / f'capture-dpr{scale}.log').write_bytes(result.stdout)
(P / f'capture-dpr{scale}.json').write_text(json.dumps({
    'command': command, 'exitCode': result.returncode, 'seconds': time.monotonic() - start,
    'scaleFactor': scale, 'sourceInputHashes': {n: hashlib.sha256(payload[n]).hexdigest() for n in names},
    'executedPayloadHashes': {n: hashlib.sha256(b).hexdigest() for n, b in payload.items()},
    'rawCaptures': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in destination.glob('*.png')},
    'freshCompilation': False, 'sourceColourInputsIntegrated': False, 'nativeRasterAccepted': False, 'accepted': False,
}, indent=2) + '\n')
print(result.stdout.decode(errors='replace'))
raise SystemExit(result.returncode)
