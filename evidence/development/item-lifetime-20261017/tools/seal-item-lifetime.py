from pathlib import Path
import hashlib,json,re,shutil,subprocess
r=Path.cwd();a=r/'artifacts/resumed-avelino-20261016';d=r/'evidence/development/item-lifetime-20261017'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(a/'item-lifetime-fixed-v1/result.json')['exitCode']==0
assert read(a/'item-lifetime-signal-tests-v2/result.json')['exitCode']==0
assert read(a/'item-lifetime-package-v1/result.json')['exitCode']==0
assert not d.exists();d.mkdir()
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for name in ['inherited-control-lifetime-baseline-v1','inherited-control-lifetime-baseline-v2','item-lifetime-matrix-baseline-v1','inherited-control-qml-baseline-v1','item-lifetime-fixed-v1','item-lifetime-signal-tests-v1','item-lifetime-signal-tests-v2','item-lifetime-package-v1']:
 src=a/name
 for f in src.iterdir():
  if f.is_file()and f.suffix in ['.cpp','.txt','.py','.json','.log','.sh']:copy(f,d/'attempts'/name/f.name)
files=['src/Avelino/'+s for s in ['inheritedcontrol.h','inheritedcontrol.cpp','radiogroupbase.h','radiogroupbase.cpp','chartrenderer.h','chartrenderer.cpp','spotlightrows.cpp','softwarecontentmask.cpp']]
for name in files:
 assert sha(r/name)==sha(a/'item-lifetime-fixed-v1/source'/name)
 copy(r/name,d/'overlay'/name)
for name in ['tests/components/itemlifetime.cpp','tests/components/tst_control_lifetime.qml','docs/qt-lifetime.md']:copy(r/name,d/'overlay'/name)
assert sha(r/'tests/components/itemlifetime.cpp')==sha(a/'item-lifetime-signal-tests-v2/itemlifetime.cpp')
# The code-only checkpoint excludes the unrelated FileInput CMake additions.
cmake=subprocess.check_output(['git','show','a411c51b58810bf7df84eb72ae3271637c1274ab:tests/components/CMakeLists.txt'])+(a/'item-lifetime-cmake-block.txt').read_bytes()
p=d/'overlay/tests/components/CMakeLists.txt';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(cmake)
# Retain the original focused test source and explicitly bind its later supplement.
copy(a/'item-lifetime-fixed-v1/source/tests/components/itemlifetime.cpp',d/'fixed-original-itemlifetime.cpp')
copy(a/'item-lifetime-fixed-v1/build/Testing/Temporary/LastTest.log',d/'fixed-lifetime-LastTest.log')
previous=r/'evidence/development/dropdown-menu-20261017/catalogs';current=a/'item-lifetime-package-v1/catalog-evidence';records=[]
for f in sorted(current.glob('*.png')):
 old=previous/f.name;meta=Path(str(f)+'.json');oldmeta=Path(str(old)+'.json');assert old.exists()and oldmeta.exists()
 assert f.read_bytes()==old.read_bytes(),f.name
 assert meta.read_bytes()==oldmeta.read_bytes(),meta.name
 records.append(dict(path=f.name,sha256=sha(f),metadataSha256=sha(meta)))
 copy(f,d/'catalogs'/f.name);copy(meta,d/'catalogs'/meta.name)
assert len(records)==151
copy(current/'catalog-results.json',d/'catalogs/catalog-results.json');copy(current/'missing-module.log',d/'catalogs/missing-module.log')
(d/'catalog-regression.json').write_text(json.dumps(dict(accepted=False,status='passed',baseline=str(previous.relative_to(r)),records=records),indent=2)+chr(10))
baseline=read(a/'item-lifetime-matrix-baseline-v1/result.json')['repros'];assert sum(v==0 for v in baseline.values())==24;assert sum(v==133 for v in baseline.values())==16
for scale in [1,2]:assert 'Totals: 42 passed, 0 failed' in (a/'item-lifetime-signal-tests-v2'/('tests-dpr'+str(scale)+'.log')).read_text()
report=dict(accepted=False,baseGit='a411c51b58810bf7df84eb72ae3271637c1274ab',status='Linux teardown correction; native mirror acceptance pending',baselineCases=40,baselineSurvived=24,baselineIncorrectTypeAborts=16,affectedClasses=['InheritedControl','RadioGroupBase','ChartRenderer','SpotlightRows','SoftwareContentMask'],fixedMatrixChecksPerScale=42,fixedScales=[1,2],qmlRegressionChecksPerScale=3,sourceAbsentConsumerModes=37,installedCatalogs=151,unchangedCatalogPairs=151,physicalDisplay=False,readerAcceptance='pending',expectedImagesChanged=False,tolerance='none',approvedExceptions=[],sourceOverlay={name:sha(d/'overlay'/name)for name in files},testSupplement='Current itemlifetime.cpp adds style-notification absence checks; tested separately against the same unchanged isolated library. The original fixed-build test source is retained.',fullCombinedRegression='Separate file-input-qt-v14 47-target run remains in progress; not claimed by this record')
(d/'validation.json').write_text(json.dumps(report,indent=2)+chr(10))
copy(Path(__file__),d/'tools/seal-item-lifetime.py')
(d/'files.json').write_text(json.dumps({str(f.relative_to(d)):dict(sha256=sha(f),bytes=f.stat().st_size)for f in sorted(d.rglob('*'))if f.is_file()and f.name!='files.json'},indent=2)+chr(10))
print(json.dumps({k:v for k,v in report.items()if k!='sourceOverlay'},indent=2))
