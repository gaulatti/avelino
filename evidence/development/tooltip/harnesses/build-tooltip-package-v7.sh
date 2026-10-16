set -euo pipefail
python3 - <<'PY'
import hashlib,json,subprocess
from pathlib import Path
root=Path('/work');output=root/'artifacts/tooltip-package-20261016-v7'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def command(*args):return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT).strip()
files=sorted([Path('CMakeLists.txt'),Path('CMakePresets.json')]+[p for folder in ['src','samples','assets','tokens','tests','scripts','cmake','tools','evidence/geometry'] for p in Path(folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts])
qtfiles=[p for glob in ['include/QtQml/6.8.3/QtQml/private/qqmlvmemetaobject_p.h','include/QtQml/6.8.3/QtQml/private/qqmlpropertycache_p.h','include/QtQuick/6.8.3/QtQuick/private/qquickaccessibleattached_p.h','lib/libQt6Qml.so.6.8.3','lib/libQt6Quick.so.6.8.3'] for p in Path('/opt/qt').glob(glob)]
assert len(qtfiles)==5
metadata=dict(sourceRevision=command('git','-c','safe.directory=/work','rev-parse','HEAD'),uncommittedChanges=True,sourceInputs={str(p):digest(p) for p in files},compiler=command('c++','--version'),qt=command('qmake','-query','QT_VERSION'),cmake=command('cmake','--version'),installedPackages=command('dpkg-query','-W'),qtPrivateIntegrationFiles={str(p):digest(p) for p in qtfiles},buildImage='avelino-toolchain:data-metrics-qt6.8.3',runtimeImage='avelino-toolchain:clipping-qt6.8.3',attempt='v7: read-only VME integration; reduced-motion initialization precedes palette; fresh independent consumer source/build')
(output/'environment.json').write_text(json.dumps(metadata,indent=2)+'\n')
PY
cmake --preset linux
cmake --build --preset linux --parallel 2
cmake --install build/linux --prefix /work/artifacts/tooltip-package-20261016-v7/install
cp -R tests/consumer artifacts/tooltip-package-20261016-v7/consumer
python3 - <<'PY'
import hashlib,json
from pathlib import Path
root=Path('artifacts/tooltip-package-20261016-v7');p=root/'environment.json';d=json.loads(p.read_text())
for name,sha in d['sourceInputs'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha,name
d['installedFiles']={str(p.relative_to(root/'install')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'install').rglob('*') if p.is_file()}
d['focusedDisplayScript']={'sha256':hashlib.sha256((root/'check-tooltip-display-sessions.sh').read_bytes()).hexdigest(),'scope':'Only fixture loop narrowed to tooltip; unchanged eight protocol/backend/scaling/compositor/assertion profiles'}
p.write_text(json.dumps(d,indent=2)+'\n');print('Frozen package files:',len(d['installedFiles']))
PY
