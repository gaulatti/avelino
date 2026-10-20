from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time
p=Path('/result');sdk=Path('/opt/qt');meta=sdk/'share/avelino/qt-software-opacity';steps=[]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def write(name,value):(p/name).write_text(json.dumps(value,indent=2)+'\n')
def inventory():
 result={}
 for f in sorted(sdk.rglob('*')):
  if sdk/'share/avelino' in f.parents:continue
  name=str(f.relative_to(sdk))
  if f.is_symlink():result[name]=dict(type='symlink',target=os.readlink(f))
  elif f.is_file():result[name]=dict(type='file',bytes=f.stat().st_size,sha256=sha(f))
 return result
try:
 inputs=json.loads((p/'inputs.json').read_text())
 for name,value in inputs['files'].items():assert sha(p/name)==value,name
 features=json.loads((meta/'features.json').read_text());cache=(p/'CMakeCache.txt').read_text();feature_rows=[]
 for row in features:
  header=sdk/'include'/row['path']
  command=['c++','-E','-dM','-x','c++','-std=c++17','-I/opt/qt/include','-include',str(header),'-']
  raw=subprocess.check_output(command,input=b'').decode()
  macros=dict(re.findall(r'^#define (QT_FEATURE_\w+) (-?1)$',raw,re.M))
  actual={key:macros[key] for key in row['sdk']}
  source={key:re.search(r'^'+re.escape(key)+r':[^=]+=(.*)$',cache,re.M).group(1) for key in actual}
  assert actual==row['sdk'] and source=={key:'ON' if value=='1' else 'OFF' for key,value in actual.items()},row['path']
  feature_rows.append(dict(path=row['path'],sdk=actual,source=source,matches=True))
 assert sum(len(row['sdk']) for row in feature_rows)==49
 write('features.json',feature_rows)
 before=inventory();write('sdk-before.json',before)
 library=sdk/'lib/libQt6Quick.so.6.8.3';header=sdk/'include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h'
 assert before['lib/libQt6Quick.so.6.8.3']['sha256']=='aa4568a285661d11667aad745903a6d3dd49045d40ea8008c12dc24015cf3c77'
 assert header.is_file()
 shutil.copyfile(p/library.name,library);shutil.copyfile(p/header.name,header)
 dynamic=subprocess.check_output(['readelf','-d',str(library)],text=True)
 paths=re.findall(r'\((?:RUNPATH|RPATH)\).*?\[(.*?)\]',dynamic);assert len(paths)==1
 script=p/'set-rpath.cmake';script.write_text('file(RPATH_CHANGE FILE "${binary}" OLD_RPATH "${old_path}" NEW_RPATH "$ORIGIN")\n')
 subprocess.run(['cmake','-Dbinary='+str(library),'-Dold_path='+paths[0],'-P',str(script)],check=True)
 dynamic=subprocess.check_output(['readelf','-d',str(library)],text=True)
 assert 'Library runpath: [$ORIGIN]' in dynamic and '/qt-build/' not in dynamic
 linkage=subprocess.check_output(['ldd','-r',str(library)],text=True,stderr=subprocess.STDOUT)
 (p/'linkage.log').write_text(linkage+'\n'+dynamic)
 assert 'undefined symbol' not in linkage and 'not found' not in linkage and '/qt-build/' not in linkage
 assert 'libQt6Qml.so.6 => /opt/qt/lib/' in linkage
 after=inventory();write('sdk-after.json',after)
 assert before.keys()==after.keys()
 changed=[name for name in before if before[name]!=after[name]]
 assert changed==['include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h','lib/libQt6Quick.so.6.8.3'],changed
 assert after['lib/libQt6Gui.so.6.8.3']['sha256']=='14563f31392210bffca0274a80a97a3d749c91900f621f9bae5bb2d8aef067f9'
 result=dict(exitCode=0,baseImage=inputs['baseImage'],sourceBase=inputs['sourceBase'],sdkEntries=len(after),changed=changed,unchangedEntries=len(after)-len(changed),added=[],removed=[],featuresMatched=49,qmlJit=True,installedQuickSha256=sha(library),runtimePath='$ORIGIN',originalQmlLibrariesRetained=True,privateHeaderUpdated=True,experimentalOnly=True,productSdkChanged=False,nativeAcceptance=False,accepted=False)
 overlay=sdk/'share/avelino/qt-software-rectangle-experiment';overlay.mkdir()
 for name,value in [('provenance.json',result),('sdk-before.json',before),('sdk-after.json',after),('features.json',feature_rows)]:
  (overlay/name).write_text(json.dumps(value,indent=2)+'\n')
 write('stage-result.json',result);print(json.dumps(result,indent=2))
except BaseException as e:
 write('stage-result.json',dict(exitCode=1,error=repr(e),accepted=False));raise
