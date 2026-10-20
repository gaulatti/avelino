from pathlib import Path
import hashlib,json,os,subprocess
p=Path('/result');sdk=Path('/opt/qt');meta=sdk/'share/avelino/qt-software-rectangle-experiment'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
actual={}
for f in sorted(sdk.rglob('*')):
 if sdk/'share/avelino' in f.parents:continue
 name=str(f.relative_to(sdk))
 if f.is_symlink():actual[name]=dict(type='symlink',target=os.readlink(f))
 elif f.is_file():actual[name]=dict(type='file',bytes=f.stat().st_size,sha256=sha(f))
(p/'immutable-sdk-files.json').write_text(json.dumps(actual,indent=2)+'\n')
expected=json.loads((meta/'sdk-after.json').read_text());assert actual==expected
before=json.loads((meta/'sdk-before.json').read_text());assert before.keys()==actual.keys()
changed=[n for n in before if before[n]!=actual[n]]
assert changed==['include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h','lib/libQt6Quick.so.6.8.3']
features=json.loads((meta/'features.json').read_text());assert len(features)==7 and sum(len(r['sdk'])for r in features)==49
assert all(r['matches'] and r['source']=={k:'ON'if v=='1'else'OFF'for k,v in r['sdk'].items()}for r in features)
assert next(r['sdk']['QT_FEATURE_qml_jit']for r in features if 'QT_FEATURE_qml_jit'in r['sdk'])=='1'
assert os.environ.get('LD_PRELOAD') is None
assert subprocess.check_output(['c++','-dumpmachine'],text=True).strip()=='aarch64-linux-gnu'
assert subprocess.check_output(['/opt/qt/bin/qmake','-query','QT_VERSION'],text=True).strip()=='6.8.3'
linkage=subprocess.check_output(['ldd','-r',str(sdk/'lib/libQt6Quick.so.6.8.3')],text=True,stderr=subprocess.STDOUT)
assert all(t not in linkage for t in ['undefined symbol','not found','/qt-build/'])
assert 'libQt6Qml.so.6 => /opt/qt/lib/'in linkage
(p/'immutable-linkage.log').write_text(linkage)
result=dict(exitCode=0,imageId=json.loads((p/'image.json').read_text())['imageId'],sdkEntries=len(actual),changed=changed,unchangedEntries=len(actual)-2,featuresMatched=49,qmlJit=True,actualImageSdkAudited=True,qt='6.8.3',target='aarch64-linux-gnu',experimentalOnly=True,productSdkChanged=False,accepted=False)
(p/'immutable-audit-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
