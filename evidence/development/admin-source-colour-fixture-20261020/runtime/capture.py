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
OUT = Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-source-colour-fixture-v1')
PACKAGE = Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-shell-compiled-v1/output/package/install')
scale = int(sys.argv[1]); assert scale in (1, 2)
destination = OUT / f'dpr{scale}'
destination.mkdir(parents=True, exist_ok=False)
names = ['src/Avelino/BleeckerAdminShell.qml', 'src/Avelino/DesktopNavigationToolbar.qml',
         'src/Avelino/DesktopSidebarGlyph.qml', 'tests/consumer/AdminShellCase.qml',
         'tests/consumer/native-admin-shell-witnesses.json', 'tests/consumer/native-admin-shell-colours.js']
payload = {name: (ROOT / name).read_bytes() for name in names}
payload['tests/components/witnesses.js'] = b'var data = ' + payload[names[4]] + b';\n'
payload['tests/components/tst_source_capture.qml'] = b'''import QtQuick
import QtTest
import Avelino
import "../consumer" as Fixtures
import "witnesses.js" as Native
import "../consumer/native-admin-shell-colours.js" as Inputs
Item {
    id: root
    width: 1100; height: 700
    Component { id: factory; Fixtures.AdminShellCase {} }
    TestCase {
        name: "AdminSourceColourFixtureCapture"
        when: windowShown
        function test_capture_data() { return Native.data.profiles.map(row => Object.assign({tag:row.name}, row)) }
        function test_capture(row) {
            BleeckerTheme.dark = row.dark
            const fixture = createTemporaryObject(factory, root, {definition:row.definition, initial:row.initial})
            verify(fixture); wait(40)
            const actual = fixture.snapshot()
            for (const key of ["navigation", "requests", "pending", "displayedNavigation", "columnWidth"])
                compare(actual[key], row.state[key], row.name + " " + key)
            compare(Object.keys(actual.frames).sort(), Object.keys(row.state.frames).sort())
            for (const role of Object.keys(row.state.frames)) for (const axis of ["x", "y", "width", "height"])
                compare(actual.frames[role][axis], row.state.frames[role][axis], role + " " + axis)
            const items = {root:findChild(fixture, "adminShellFixtureBackground"), sidebar:fixture.shell.sidebarItem,
                header:fixture.shell.headerItem, content:fixture.shell.contentSlotItem}
            const colours = {}
            for (const role of Object.keys(items)) {
                if (!items[role]) continue
                const value = Inputs.environments[row.dark ? "dark" : "light"][role].encodedSRGB
                compare(items[role].color, Qt.rgba(value[0], value[1], value[2], value[3]))
                const c = items[role].color
                colours[role] = [c.r, c.g, c.b, c.a]
            }
            let finished = false, saved = false
            verify(fixture.grabToImage(function(result) {
                saved = result.saveToFile("/capture/" + row.name + ".png"); finished = true
            }))
            tryVerify(function() { return finished }, 5000); verify(saved)
            console.log("SOURCE_COLOUR " + JSON.stringify({name:row.name, dark:row.dark, initial:row.initial,
                width:fixture.width, height:fixture.height, state:actual, colours:colours}))
        }
    }
}
'''
snapshot = P / f'capture-inputs-dpr{scale}'; snapshot.mkdir()
for name, raw in payload.items():
    target = snapshot / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
buffer = io.BytesIO()
with tarfile.open(fileobj=buffer, mode='w') as archive:
    for name, raw in payload.items():
        info = tarfile.TarInfo(name); info.size = len(raw); archive.addfile(info, io.BytesIO(raw))
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
    '-e', 'QT_QPA_PLATFORM=offscreen', '-e', 'QT_QUICK_BACKEND=software', '-e', f'QT_SCALE_FACTOR={scale}',
    '-e', 'LD_LIBRARY_PATH=/avelino/lib/qml/Avelino:/opt/qt/lib', '-v', str(PACKAGE) + ':/avelino:ro',
    '-v', str(destination) + ':/capture',
    'sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7', 'bash', '-euc', script]
start = time.monotonic()
result = subprocess.run(command, input=buffer.getvalue(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
log = result.stdout.decode(errors='replace')
(P / f'capture-dpr{scale}.log').write_bytes(result.stdout)
observations = [json.loads(line.split('SOURCE_COLOUR ', 1)[1]) for line in log.splitlines() if 'SOURCE_COLOUR ' in line]
(P / f'capture-dpr{scale}.json').write_text(json.dumps(dict(command=command, exitCode=result.returncode,
    seconds=time.monotonic() - start, scaleFactor=scale,
    sourceInputHashes={n:hashlib.sha256(payload[n]).hexdigest() for n in names},
    executedPayloadHashes={n:hashlib.sha256(raw).hexdigest() for n,raw in payload.items()},
    observations=observations,
    rawCaptures={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in destination.glob('*.png')},
    freshCompilation=False, sourceColourInputsIntegrated=True, nativeRasterAccepted=False, accepted=False), indent=2) + '\n')
print('\n'.join(line for line in log.splitlines() if not line.startswith('PASS   :') and 'SOURCE_COLOUR ' not in line))
raise SystemExit(result.returncode)
