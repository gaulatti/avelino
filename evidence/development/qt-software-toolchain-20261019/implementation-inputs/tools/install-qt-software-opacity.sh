#!/usr/bin/env bash
set -euo pipefail

# Rebuild only Qt Quick, retaining the pinned SDK's other libraries and features.
qt_prefix="${1:-/opt/qt}"
script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
qt_opacity_build="$(mktemp -d)"
trap 'rm -rf "$qt_opacity_build"' EXIT
metadata="$qt_prefix/share/avelino/qt-software-opacity"
mkdir -p "$(dirname "$metadata")"
mkdir "$metadata"
[[ -z "${LD_PRELOAD-}" ]]

python3 - "$qt_opacity_build" "$qt_prefix" "$script_directory" "$metadata" "${2-}" <<'PY'
from pathlib import Path
import hashlib, json, os, re, subprocess, sys, urllib.request

work, prefix, scripts, metadata = map(Path, sys.argv[1:5])
url = 'https://download.qt.io/archive/qt/6.8/6.8.3/submodules/qtdeclarative-everywhere-src-6.8.3.tar.xz'
archive_sha = '1f03a2b8f5588b4face7da87926e9b2c1372b3a32157c52df07a75067a9db1af'
if sys.argv[5]:
    raw = Path(sys.argv[5]).read_bytes()
else:
    with urllib.request.urlopen(url, timeout=60) as response:
        raw = response.read()
assert hashlib.sha256(raw).hexdigest() == archive_sha
(work / 'qtdeclarative.tar.xz').write_bytes(raw)
patch = scripts / 'qt-software-opacity.patch'
patch_sha = hashlib.sha256(patch.read_bytes()).hexdigest()
assert patch_sha == 'e00c5b0d751e6472e98b4dc43c13da0a227d247d7b3d7344795ad3db728086c1'
headers = sorted(p for module in ['QtQml', 'QtQmlModels', 'QtQuick', 'QtQuickTemplates2', 'QtQuickControls2']
                 for p in (prefix / 'include' / module).rglob('*-config*.h'))
preprocess_input = '#include <QtCore/qglobal.h>\n' + ''.join('#include "' + str(path) + '"\n' for path in headers)
preprocess_command = ['c++', '-std=c++17', '-fPIC', '-dM', '-E', '-x', 'c++',
                      '-I' + str(prefix / 'include'), '-I' + str(prefix / 'mkspecs/linux-g++'), '-']
macros = subprocess.check_output(preprocess_command, input=preprocess_input, text=True)
(metadata / 'sdk-effective-macros.log').write_text(macros)
(metadata / 'sdk-feature-preprocessor.json').write_text(json.dumps(dict(
    command=preprocess_command, input=preprocess_input,
    target=subprocess.check_output(['c++', '-dumpmachine'], text=True).strip()), indent=2) + '\n')
effective = dict(re.findall(r'^#define (QT_FEATURE_\w+) (-?1)$', macros, re.M))
features = []
for path in headers:
    names = set(re.findall(r'^#define (QT_FEATURE_\w+) ', path.read_text(), re.M))
    if names:
        assert names <= effective.keys(), names - effective.keys()
        features.append(dict(path=str(path.relative_to(prefix / 'include')),
                             sdk={name: effective[name] for name in sorted(names)}))
assert len(features) == 7 and sum(len(row['sdk']) for row in features) == 49
jit = [row['sdk']['QT_FEATURE_qml_jit'] for row in features if 'QT_FEATURE_qml_jit' in row['sdk']]
assert len(jit) == 1
(work / 'qml-jit').write_text('ON' if jit[0] == '1' else 'OFF')
(metadata / 'features.json').write_text(json.dumps(features, indent=2) + '\n')
original = prefix / 'lib/libQt6Quick.so.6.8.3'
(metadata / 'provenance.json').write_text(json.dumps(dict(
    qt='6.8.3', sourceUrl=url, archiveSha256=archive_sha, patchSha256=patch_sha,
    originalLibrarySha256=hashlib.sha256(original.read_bytes()).hexdigest(),
    replacement='Qt Quick only', nativeAcceptance=False), indent=2) + '\n')
sdk = {}
for path in sorted(prefix.rglob('*')):
    if metadata in path.parents:
        continue
    name = str(path.relative_to(prefix))
    if path.is_symlink():
        sdk[name] = dict(type='symlink', target=os.readlink(path))
    elif path.is_file():
        sdk[name] = dict(type='file', bytes=path.stat().st_size,
                         sha256=hashlib.sha256(path.read_bytes()).hexdigest())
(metadata / 'sdk-before.json').write_text(json.dumps(sdk, indent=2) + '\n')
PY

# A red control must contain rendered frames with actual alpha corruption.
control_result=0
LD_LIBRARY_PATH="$qt_prefix/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    bash "$script_directory/check-qt-software-opacity.sh" "$metadata/sdk-control" "$qt_prefix" || control_result=$?
[[ "$control_result" == 1 ]]
python3 - "$metadata/sdk-control" <<'PY'
from pathlib import Path
import json, sys
reports = [json.loads(p.read_text()) for p in Path(sys.argv[1]).glob('*/result.json')]
assert reports and all(len(r['frames']) == 30 and all(f['paintedPixels'] > 0 for f in r['frames']) for r in reports)
assert all(r['canvasRuntimeChecksPassed'] for r in reports)
assert any(r['failedFrames'] > 0 and any(f['nonOpaquePixels'] > 0 for f in r['frames']) for r in reports)
PY

tar -xf "$qt_opacity_build/qtdeclarative.tar.xz" -C "$qt_opacity_build"
qt_source="$qt_opacity_build/qtdeclarative-everywhere-src-6.8.3"
cmp "$qt_source/src/quick/scenegraph/adaptations/software/qsgsoftwarerenderablenode_p.h" \
    "$qt_prefix/include/QtQuick/6.8.3/QtQuick/private/qsgsoftwarerenderablenode_p.h"
patch --batch --forward --fuzz=0 -p1 -d "$qt_source" -i "$script_directory/qt-software-opacity.patch"
cmake -S "$qt_source" -B "$qt_opacity_build/build" -G Ninja \
    -DCMAKE_PREFIX_PATH="$qt_prefix" -DCMAKE_INSTALL_PREFIX="$qt_prefix" \
    -DCMAKE_BUILD_TYPE=Release -DQT_BUILD_EXAMPLES=OFF -DQT_BUILD_TESTS=OFF \
    -DBUILD_WITH_PCH=OFF -DFEATURE_qml_jit="$(cat "$qt_opacity_build/qml-jit")"
python3 - "$metadata/features.json" "$qt_opacity_build/build/CMakeCache.txt" <<'PY'
from pathlib import Path
import json, re, sys
path = Path(sys.argv[1]); features = json.loads(path.read_text())
cache = dict(re.findall(r'^(QT_FEATURE_\w+):\w+=(ON|OFF)$', Path(sys.argv[2]).read_text(), re.M))
for row in features:
    row['source'] = {key: cache.get(key) for key in row['sdk']}
    row['matches'] = all(row['source'][key] == ('ON' if value == '1' else 'OFF') for key, value in row['sdk'].items())
    assert row['matches'], row
path.write_text(json.dumps(features, indent=2) + '\n')
PY
cmake --build "$qt_opacity_build/build" --target Quick --parallel 2

# Stage one library with a portable RPATH; never install source-built QML deps.
mkdir "$qt_opacity_build/overlay"
cp "$qt_opacity_build/build/lib/libQt6Quick.so.6.8.3" "$qt_opacity_build/overlay/"
python3 - "$qt_opacity_build/overlay/libQt6Quick.so.6.8.3" "$qt_prefix" "$metadata" <<'PY'
from pathlib import Path
import hashlib, json, os, re, subprocess, sys
library, prefix, metadata = map(Path, sys.argv[1:])
dynamic = subprocess.check_output(['readelf', '-d', str(library)], text=True)
paths = re.findall(r'\((?:RUNPATH|RPATH)\).*?\[(.*?)\]', dynamic)
assert len(paths) == 1, paths
script = library.parent / 'rpath.cmake'
script.write_text('file(RPATH_CHANGE FILE "${binary}" OLD_RPATH "${old_path}" NEW_RPATH "$ORIGIN")\n')
subprocess.run(['cmake', '-Dbinary=' + str(library), '-Dold_path=' + paths[0], '-P', str(script)], check=True)
(library.parent / 'libQt6Quick.so.6').symlink_to(library.name)
env = dict(os.environ, LD_LIBRARY_PATH=str(library.parent) + ':' + str(prefix / 'lib'))
linked = subprocess.check_output(['ldd', '-r', str(library)], env=env, text=True, stderr=subprocess.STDOUT)
assert 'not found' not in linked and 'undefined symbol' not in linked and str(library.parents[1] / 'build') not in linked, linked
(metadata / 'linkage.log').write_text(linked)
record = json.loads((metadata / 'provenance.json').read_text())
record['installedLibrarySha256'] = hashlib.sha256(library.read_bytes()).hexdigest()
record['runtimePath'] = '$ORIGIN'
(metadata / 'provenance.json').write_text(json.dumps(record, indent=2) + '\n')
PY
LD_LIBRARY_PATH="$qt_opacity_build/overlay:$qt_prefix/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    bash "$script_directory/check-qt-software-opacity.sh" "$metadata/patched-regression" "$qt_prefix"
install -m 755 "$qt_opacity_build/overlay/libQt6Quick.so.6.8.3" "$qt_prefix/lib/libQt6Quick.so.6.8.3.avelino-new"
mv -f "$qt_prefix/lib/libQt6Quick.so.6.8.3.avelino-new" "$qt_prefix/lib/libQt6Quick.so.6.8.3"
cp "$script_directory/qt-software-opacity.patch" "$metadata/"
python3 - "$qt_prefix" "$metadata" <<'PY'
from pathlib import Path
import hashlib, json, os, sys
prefix, metadata = map(Path, sys.argv[1:])
before = json.loads((metadata / 'sdk-before.json').read_text()); after = {}
for path in sorted(prefix.rglob('*')):
    if metadata in path.parents:
        continue
    name = str(path.relative_to(prefix))
    if path.is_symlink():
        after[name] = dict(type='symlink', target=os.readlink(path))
    elif path.is_file():
        after[name] = dict(type='file', bytes=path.stat().st_size,
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest())
assert before.keys() == after.keys(), (before.keys() - after.keys(), after.keys() - before.keys())
changed = [name for name in before if before[name] != after[name]]
assert changed == ['lib/libQt6Quick.so.6.8.3'], changed
record = json.loads((metadata / 'provenance.json').read_text())
assert after[changed[0]]['sha256'] == record['installedLibrarySha256']
assert before[changed[0]]['sha256'] == record['originalLibrarySha256']
(metadata / 'sdk-changes.json').write_text(json.dumps(dict(changed=changed, added=[], removed=[],
    unchangedEntries=len(before)-1, nativeAcceptance=False), indent=2) + '\n')
PY
