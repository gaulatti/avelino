from pathlib import Path
import json,hashlib,shutil,subprocess,time
from PIL import Image
ROOT=Path('/Users/gaulatti/.codex/tmp/avelino-reference-repair-20261020-v1')
SOURCE=Path('/Users/gaulatti/source/gaulatti/avelino')
P=Path(__file__).resolve().parent
OUT=SOURCE/'artifacts/resumed-avelino-20261016/admin-clipping-comparison-v1'
OUT.mkdir();reference=OUT/'reference';reference.mkdir();candidate=OUT/'candidate';candidate.mkdir()
old=SOURCE/'artifacts/resumed-avelino-20261016/admin-source-colours-prototype-v1/reference-aliases'
manifest=json.loads((old/'captures.json').read_text());assert len(manifest['captures'])==80
native_cap=ROOT/'evidence/reference-investigations/admin-shell-pinned-matrix-20261020'
native_images=json.loads((native_cap/'images.json').read_text())
profiles=json.loads((ROOT/'tests/consumer/native-admin-shell-witnesses.json').read_text());profiles={r['name']:r for r in profiles['profiles']}
package=SOURCE/'artifacts/resumed-avelino-20261016/admin-clipping-compiled-v1/output/package'
report_path=package/'reports/light-dpr2.json';report=json.loads(report_path.read_text());assert report['dpr']==2 and report['textScale']==1
actual={r['name']:r for r in report['layouts']};bindings=[]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for fixture in manifest['captures']:
 name=Path(fixture['path']).stem;profile=profiles[name];theme='dark' if profile['dark'] else 'light';alias=profile['sourceCapture']
 row=native_images[alias];original=native_cap/row['stored'];assert sha(original)==fixture['sha256']==sha(old/fixture['path'])
 assert fixture['source']=='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
 shutil.copy2(original,reference/fixture['path'])
 record=actual[name];src=package/'reports'/record['capture'];target=candidate/fixture['path'];shutil.copy2(src,target);assert sha(src)==sha(target)
 frame=record['frames']['root'];metadata={'width':record['pixelWidth']/report['dpr'],'height':record['pixelHeight']/report['dpr'],'dpr':report['dpr'],'textScale':report['textScale'],'fixture':name,'appearance':theme,'api':'BleeckerAdminShell','state':{'navigationPresented':record['navigation']},'componentSize':{'width':frame['width'],'height':frame['height']},'geometryEvidence':'Viewport dimensions from captured pixel size / reported DPR; overflowing component dimensions from actual consumer frames.root.','appearanceEvidence':'Actual configure input from the pinned profile; raw body matches the committed interpreted input fixture.','sourceRevision':'7253695c3e94b0626bcb0612fbc8467fe94445b5','compiledInstalledConsumer':True,'physicalInput':False,'accepted':False}
 for key in ['width','height','dpr','textScale','fixture','appearance','api','state','componentSize']:assert metadata[key]==fixture[key],(name,key)
 with Image.open(target) as im:im.load();assert im.size==(record['pixelWidth'],record['pixelHeight'])
 (candidate/(fixture['path']+'.json')).write_text(json.dumps(metadata,indent=2)+'\n')
 bindings.append({'profile':name,'nativeAlias':alias,'nativeSha256':fixture['sha256'],'packageCapture':record['capture'],'candidateSha256':sha(src)})
(reference/'captures.json').write_text(json.dumps(manifest,indent=2)+'\n')
comparator=ROOT/'scripts/compare-captures.py'
historical=subprocess.check_output(['git','show','39489069c52ac40c7a4dadfdec33b0fd1d76261a:scripts/compare-captures.py'],cwd=ROOT)
assert hashlib.sha256(historical).hexdigest()==sha(comparator)
command=['/Users/gaulatti/.codex/tmp/avelino-visuals-20261020/bin/python',str(comparator),'--reference',str(reference),'--candidate',str(candidate),'--output',str(OUT/'canonical')]
start=time.monotonic();run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(P/'comparison.log').write_text(run.stdout);comparison=json.loads((OUT/'canonical/comparison.json').read_text())
assert run.returncode==1 and comparison['status']=='failed' and len(comparison['results'])==80
assert all(r.get('error')=='ICC-managed captures require an explicitly reviewed color-space conversion' and r['status']=='failed' for r in comparison['results'])
assert all(r['geometryStatus']=='passed' for r in comparison['results'])
result={'command':command,'comparisonExitCode':run.returncode,'seconds':time.monotonic()-start,'sourceRevision':'7253695c3e94b0626bcb0612fbc8467fe94445b5','evidenceHead':'7253695c3e94b0626bcb0612fbc8467fe94445b5','comparisonStatus':'failed','comparedFixtures':80,'iccPolicyRefusals':80,'rootGeometryChecksPassed':80,'imageBytesConverted':False,'comparatorSha256':sha(comparator),'comparatorPolicyUnchanged':True,'nativeRasterAccepted':False,'accepted':False,'packageReportSha256':sha(report_path)}
(P/'result.json').write_text(json.dumps(result,indent=2)+'\n');(P/'image-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
shutil.copy2(OUT/'canonical/comparison.json',P/'comparison.json');print(json.dumps(result,indent=2))
