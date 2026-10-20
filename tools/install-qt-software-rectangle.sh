#!/usr/bin/env bash
set -euo pipefail

qt_rectangle_source="${1:?verified Qt source directory required}"
qt_rectangle_build="${2:?configured Qt build directory required}"
qt_prefix="${3:?Qt SDK prefix required}"
script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
qt_rectangle_work="$(mktemp -d)"
trap 'rm -rf "$qt_rectangle_work"' EXIT
metadata="$qt_prefix/share/avelino/qt-software-rectangle"
mkdir "$metadata"
[[ -z "${LD_PRELOAD-}" ]]

python3 - "$qt_rectangle_source" "$qt_rectangle_build" "$qt_prefix" "$script_directory" "$metadata" <<'PY'
from pathlib import Path
import hashlib,json,os,re,sys
source,build,prefix,scripts,metadata=map(Path,sys.argv[1:])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
previous=json.loads((prefix/'share/avelino/qt-software-opacity/provenance.json').read_text())
assert previous['qt']=='6.8.3' and not previous['nativeAcceptance']
assert previous['archiveSha256']=='1f03a2b8f5588b4face7da87926e9b2c1372b3a32157c52df07a75067a9db1af'
assert previous['installedLibrarySha256']==sha(prefix/'lib/libQt6Quick.so.6.8.3')
node=source/'src/quick/scenegraph/adaptations/software'
expected={'qsgsoftwareinternalrectanglenode.cpp':'521ae4ffc0a145c2de839b149873b2caa2718118eff603c4a47dd931e6251db2',
          'qsgsoftwareinternalrectanglenode_p.h':'c9f8f2e22bf8a7501cc781d3411078312a5037a848b5c132c2bf6a5c160acb38'}
for name,value in expected.items():assert sha(node/name)==value,name
header=prefix/'include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h'
assert sha(header)==expected[header.name]
assert sha(node/'qsgsoftwarerenderablenode.cpp')=='3aa438a27a031c531c3552c03dcc2a1173e0338dbf80fb2653419c1b4a886ec3'
patch=scripts/'qt-software-rectangle.patch'
assert sha(patch)=='3e6b140f30e05705b70cb0f139cf59b31c39bfb1ef47210c1c70abf49f5b195f'
features=json.loads((prefix/'share/avelino/qt-software-opacity/features.json').read_text())
cache=dict(re.findall(r'^(QT_FEATURE_\w+):\w+=(ON|OFF)$',(build/'CMakeCache.txt').read_text(),re.M))
assert len(features)==7 and sum(len(r['sdk'])for r in features)==49
for row in features:
 assert row['matches'] and row['source']=={k:cache[k]for k in row['sdk']}
 assert row['source']=={k:'ON'if v=='1'else'OFF'for k,v in row['sdk'].items()}
(metadata/'features.json').write_text(json.dumps(features,indent=2)+'\n')
before={}
for f in sorted(prefix.rglob('*')):
 if prefix/'share/avelino' in f.parents:continue
 name=str(f.relative_to(prefix))
 if f.is_symlink():before[name]=dict(type='symlink',target=os.readlink(f))
 elif f.is_file():before[name]=dict(type='file',bytes=f.stat().st_size,sha256=sha(f))
(metadata/'sdk-before.json').write_text(json.dumps(before,indent=2)+'\n')
record=dict(qt='6.8.3',sourceUrl=previous['sourceUrl'],archiveSha256=previous['archiveSha256'],
 patchSha256=sha(patch),previousStage='qt-software-opacity',originalLibrarySha256=previous['installedLibrarySha256'],
 originalHeaderSha256=sha(header),replacement='Qt Quick library and matching private rectangle header',nativeAcceptance=False)
(metadata/'provenance.json').write_text(json.dumps(record,indent=2)+'\n')
PY

LD_LIBRARY_PATH="$qt_prefix/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    bash "$script_directory/check-qt-software-rectangle.sh" "$metadata/baseline" 1 "$qt_prefix"
patch --batch --forward --fuzz=0 -p1 -d "$qt_rectangle_source" -i "$script_directory/qt-software-rectangle.patch"
python3 - "$qt_rectangle_source" <<'PY'
from pathlib import Path
import hashlib,sys
p=Path(sys.argv[1])/'src/quick/scenegraph/adaptations/software'
for name,value in {'qsgsoftwareinternalrectanglenode.cpp':'444866b924057f18f0caee5ef99e08a1876b8676e6f9a3f6676846af2556df65',
                   'qsgsoftwareinternalrectanglenode_p.h':'53823a7efab36af6338ba07a397f351934c7a0176a431ca4e8695fc5f7511ae0'}.items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==value,name
PY
cmake --build "$qt_rectangle_build" --target Quick --parallel 2
mkdir "$qt_rectangle_work/overlay"
cp "$qt_rectangle_build/lib/libQt6Quick.so.6.8.3" "$qt_rectangle_work/overlay/"
python3 - "$qt_rectangle_work/overlay/libQt6Quick.so.6.8.3" "$qt_prefix" "$metadata" <<'PY'
from pathlib import Path
import hashlib,json,os,re,subprocess,sys
library,prefix,metadata=map(Path,sys.argv[1:])
dynamic=subprocess.check_output(['readelf','-d',str(library)],text=True)
paths=re.findall(r'\((?:RUNPATH|RPATH)\).*?\[(.*?)\]',dynamic);assert len(paths)==1
script=library.parent/'rpath.cmake';script.write_text('file(RPATH_CHANGE FILE "${binary}" OLD_RPATH "${old_path}" NEW_RPATH "$ORIGIN")\n')
subprocess.run(['cmake','-Dbinary='+str(library),'-Dold_path='+paths[0],'-P',str(script)],check=True)
(library.parent/'libQt6Quick.so.6').symlink_to(library.name)
env=dict(os.environ,LD_LIBRARY_PATH=str(library.parent)+':'+str(prefix/'lib'))
linked=subprocess.check_output(['ldd','-r',str(library)],env=env,text=True,stderr=subprocess.STDOUT)
assert all(s not in linked for s in ['not found','undefined symbol','/qt-build/']),linked
assert 'libQt6Qml.so.6 => '+str(prefix/'lib')+'/' in linked
dynamic=subprocess.check_output(['readelf','-d',str(library)],text=True)
assert 'Library runpath: [$ORIGIN]' in dynamic
(metadata/'linkage.log').write_text(linked)
record=json.loads((metadata/'provenance.json').read_text());record.update(installedLibrarySha256=hashlib.sha256(library.read_bytes()).hexdigest(),runtimePath='$ORIGIN')
(metadata/'provenance.json').write_text(json.dumps(record,indent=2)+'\n')
PY
install -m 755 "$qt_rectangle_work/overlay/libQt6Quick.so.6.8.3" "$qt_prefix/lib/libQt6Quick.so.6.8.3.avelino-new"
mv -f "$qt_prefix/lib/libQt6Quick.so.6.8.3.avelino-new" "$qt_prefix/lib/libQt6Quick.so.6.8.3"
header_directory="$qt_prefix/include/QtQuick/6.8.3/QtQuick/private"
install -m 644 "$qt_rectangle_source/src/quick/scenegraph/adaptations/software/qsgsoftwareinternalrectanglenode_p.h" \
    "$header_directory/qsgsoftwareinternalrectanglenode_p.h.avelino-new"
mv -f "$header_directory/qsgsoftwareinternalrectanglenode_p.h.avelino-new" "$header_directory/qsgsoftwareinternalrectanglenode_p.h"
LD_LIBRARY_PATH="$qt_prefix/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    bash "$script_directory/check-qt-software-rectangle.sh" "$metadata/patched" 0 "$qt_prefix"
LD_LIBRARY_PATH="$qt_prefix/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    bash "$script_directory/check-qt-software-opacity.sh" "$metadata/opacity-regression" "$qt_prefix"
cp "$script_directory/qt-software-rectangle.patch" "$metadata/"
python3 - "$qt_prefix" "$metadata" "$qt_rectangle_build/CMakeCache.txt" <<'PY'
from pathlib import Path
import hashlib,json,os,re,sys
prefix,metadata,cache_path=map(Path,sys.argv[1:])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((metadata/'sdk-before.json').read_text());after={}
for f in sorted(prefix.rglob('*')):
 if prefix/'share/avelino' in f.parents:continue
 name=str(f.relative_to(prefix))
 if f.is_symlink():after[name]=dict(type='symlink',target=os.readlink(f))
 elif f.is_file():after[name]=dict(type='file',bytes=f.stat().st_size,sha256=sha(f))
assert before.keys()==after.keys()
changed=[n for n in before if before[n]!=after[n]]
assert changed==['include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h','lib/libQt6Quick.so.6.8.3'],changed
legacy=references=0
for profile in ['xcb-dpr1','xcb-dpr2','wayland-dpr1','wayland-dpr2']:
 a=metadata/'baseline'/profile;b=metadata/'patched'/profile
 old=json.loads((a/'result.json').read_text());new=json.loads((b/'result.json').read_text())
 assert old['floatingGeometryFailures']>0 and new['floatingGeometryFailures']==0
 for x,y in zip(old['frames'],new['frames'],strict=True):
  assert all(x[k]==y[k]for k in ['index','kind','shift','height','actualRect'])
  if x['kind']==0:
   assert (a/x['reference']).read_bytes()==(b/y['reference']).read_bytes();references+=1
  else:
   assert (a/x['capture']).read_bytes()==(b/y['capture']).read_bytes();legacy+=1
assert legacy==360 and references==120
cache=dict(re.findall(r'^(QT_FEATURE_\w+):\w+=(ON|OFF)$',cache_path.read_text(),re.M))
for row in json.loads((metadata/'features.json').read_text()):
 assert row['source']=={key:cache[key]for key in row['sdk']}
record=json.loads((metadata/'provenance.json').read_text())
assert before['lib/libQt6Quick.so.6.8.3']['sha256']==record['originalLibrarySha256']
assert after['lib/libQt6Quick.so.6.8.3']['sha256']==record['installedLibrarySha256']
record['installedHeaderSha256']=after[changed[0]]['sha256'];record['featuresMatched']=49
record['legacyByteIdentical']=legacy;record['floatingReferences']=references
(metadata/'provenance.json').write_text(json.dumps(record,indent=2)+'\n')
(metadata/'sdk-after.json').write_text(json.dumps(after,indent=2)+'\n')
(metadata/'sdk-changes.json').write_text(json.dumps(dict(changed=changed,added=[],removed=[],unchangedEntries=len(before)-2,nativeAcceptance=False),indent=2)+'\n')
PY
