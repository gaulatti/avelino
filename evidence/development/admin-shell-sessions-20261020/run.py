from pathlib import Path
import hashlib
import json
import re
import subprocess
import time

P = Path(__file__).resolve().parent
ROOT = Path('/Users/gaulatti/source/gaulatti/avelino')
PACKAGE = ROOT / 'artifacts/resumed-avelino-20261016/admin-shell-compiled-v1/output/package'
BUILD = Path('/Users/gaulatti/.codex/tmp/avelino-admin-window-readiness-build-20261020-v5')
result = json.loads((BUILD / 'result.json').read_text())
assert result['exitCode'] == 0 and result['consumerBuildPassed']
revision = result['sourceRevision']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
artifacts = json.loads((BUILD / 'artifacts.json').read_text())
assert artifacts['consumerSha256'] == sha(PACKAGE / 'consumer-build/InstalledConsumer')
assert artifacts['librarySha256'] == sha(PACKAGE / 'install/lib/qml/Avelino/libAvelino.so')
canonical = subprocess.check_output(['git', 'show', revision + ':scripts/check-display-sessions.sh'], cwd=ROOT)
filtered, count = re.subn(r'for fixture in [^\n]+; do', 'for fixture in admin-shell; do', canonical.decode(), count=1)
assert count == 1
(P / 'canonical.sh').write_bytes(canonical)
(P / 'filtered.sh').write_text(filtered)
(PACKAGE / 'check-admin-sessions-v3.sh').write_text(filtered)
inputs = dict(sourceRevision=revision, consumerSha256=artifacts['consumerSha256'],
              librarySha256=artifacts['librarySha256'],
              canonicalSessionScriptSha256=hashlib.sha256(canonical).hexdigest(),
              filteredSessionScriptSha256=hashlib.sha256(filtered.encode()).hexdigest(),
              sourceProjectsMounted=False, productBuildMounted=False,
              physicalDisplay=False, hardwareAcceleration=False, accepted=False)
raw = json.dumps(inputs, indent=2) + '\n'
(P / 'inputs.json').write_text(raw)
(PACKAGE / 'environment.json').write_text(raw)
command = ['docker', '--context', 'colima-avelino-verify', 'run', '--init', '--rm',
           '--ulimit', 'core=0', '-v', str(PACKAGE) + ':/package', '-w', '/package',
           '-e', 'LD_LIBRARY_PATH=/package/install/lib/qml/Avelino:/opt/weston-13.0.4/lib:/opt/qt/lib',
           'sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7',
           'bash', '-euc', 'test ! -e /work/src; test ! -e /work/CMakeLists.txt; exec bash check-admin-sessions-v3.sh /package/admin-sessions-v3']
start = time.monotonic()
with (P / 'sessions.log').open('x') as log:
    completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
assert inputs['consumerSha256'] == sha(PACKAGE / 'consumer-build/InstalledConsumer')
assert inputs['librarySha256'] == sha(PACKAGE / 'install/lib/qml/Avelino/libAvelino.so')
(P / 'result.json').write_text(json.dumps(dict(command=command, exitCode=completed.returncode,
    seconds=time.monotonic() - start, sourceProjectsMounted=False, productBuildMounted=False,
    binariesUnchangedSinceLaunch=True, accepted=False), indent=2) + '\n')
print('installed Admin sessions v3', completed.returncode, flush=True)
raise SystemExit(completed.returncode)
