from pathlib import Path
import hashlib,json,os,shutil,subprocess
p=Path('/result');sdk=Path('/opt/qt')
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def inventory():
 rows={}
 for f in sorted(sdk.rglob('*')):
  if sdk/'share/avelino' in f.parents:continue
  n=str(f.relative_to(sdk))
  if f.is_symlink():rows[n]=dict(type='symlink',target=os.readlink(f))
  elif f.is_file():rows[n]=dict(type='file',bytes=f.stat().st_size,sha256=sha(f))
 return rows
before=inventory();assert before==json.loads((p/'rectangle-stage/sdk-before.json').read_text())
shutil.copy2(p/'installed-quick.so',sdk/'lib/libQt6Quick.so.6.8.3')
shutil.copy2(p/'installed-rectangle.h',sdk/'include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h')
shutil.copytree(p/'rectangle-stage',sdk/'share/avelino/qt-software-rectangle')
for name,row in json.loads((p/'runtime-recipe.json').read_text()).items():
 source=p/'runtime-recipe'/name
 assert sha(source)==row['sha256']
 shutil.copy2(source,Path('/usr/local/lib/avelino')/name)
 assert (Path('/usr/local/lib/avelino')/name).stat().st_mode&0o777==row['mode']
after=inventory();assert after==json.loads((p/'rectangle-stage/sdk-after.json').read_text())
assert not any(Path(n).exists()for n in ['/qt-source','/qt-build'])
old=json.loads((sdk/'share/avelino/qt-software-opacity/provenance.json').read_text());new=json.loads((sdk/'share/avelino/qt-software-rectangle/provenance.json').read_text())
assert old['installedLibrarySha256']==new['originalLibrarySha256']
assert new['installedLibrarySha256']==sha(sdk/'lib/libQt6Quick.so.6.8.3')
assert new['installedHeaderSha256']==sha(sdk/'include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h')
linkage=subprocess.check_output(['ldd','-r',str(sdk/'lib/libQt6Quick.so.6.8.3')],text=True,stderr=subprocess.STDOUT)
assert all(t not in linkage for t in ['undefined symbol','not found','/qt-build/'])
result=dict(exitCode=0,sdkEntries=len(after),sdkMatchesTestedCandidate=True,chainedProvenance=True,recipeFilesInstalled=True,producerSourceAndBuildCacheAbsent=True,opacityStageInheritedFromProduct=True,fullDockerfileBuild=False,accepted=False)
(p/'runtime-assembly-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
