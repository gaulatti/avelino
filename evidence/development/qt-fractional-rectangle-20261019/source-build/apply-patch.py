import hashlib,json,re
from pathlib import Path
p=Path('/result')
s=Path('/qt-source/qtdeclarative-everywhere-src-6.8.3/src/quick/scenegraph/adaptations/software')
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
verified=json.loads((p/'archive-source-verification.json').read_text())
before={name:digest(s/name) for name in verified['files']}
assert all(before[name]==row['sha256'] for name,row in verified['files'].items())
cache=Path('/qt-build/CMakeCache.txt')
cache_sha=digest(cache)
jit=re.findall(r'^QT_FEATURE_qml_jit:[^=]+=(.*)$',cache.read_text(),re.M)
assert jit==['ON'],jit
qtgui=Path('/opt/qt/lib/libQt6Gui.so.6.8.3')
assert digest(qtgui)=='14563f31392210bffca0274a80a97a3d749c91900f621f9bae5bb2d8aef067f9'
opacity=s/'qsgsoftwarerenderablenode.cpp'
opacity_sha=digest(opacity)
for name in verified['files']: (s/name).write_bytes((p/'patched'/name).read_bytes())
assert cache_sha==digest(cache) and opacity_sha==digest(opacity)
result=dict(before=before,after={name:digest(s/name) for name in before},qmlJit=jit[0],cmakeCacheSha256=cache_sha,opacitySourceSha256=opacity_sha,qtGuiSha256=digest(qtgui),privateHeaderLayoutChanges=True,productSdkChanged=False,accepted=False)
(p/'applied-patch.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
