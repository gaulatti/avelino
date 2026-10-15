import collections,hashlib,importlib.util,json,re,shutil
from pathlib import Path
root=Path('evidence/development/accordion');assert not root.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,j:p.write_text(json.dumps(j,indent=2)+'\n')
env=json.load(open('artifacts/linux/environment.json'))
for p,h in env['sourceInputs'].items():assert sha(Path(p))==h,p
source=Path('artifacts/linux/accordion-proposals');report=json.load(open(source/'capture-results.json'));assert report['status']=='captured' and len(report['results'])==192
root.mkdir();shutil.copytree(source,root/'captures');shutil.copy2('artifacts/linux/environment.json',root/'build-environment.json')
spec=importlib.util.spec_from_file_location('compare','scripts/compare-captures.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
compare.compare(Path('evidence/reference-proposals/accordion-20261014'),root/'captures',root/'comparison')
rows=json.load(open(root/'comparison/comparison.json'))['results'];assert len(rows)==192 and not any('error' in r for r in rows)
assert sum(r.get('geometryStatus')=='passed' for r in rows)==192
folders={'desktop':'proposals','composition':'composition-proposals','selectors':'selector-proposals','checkbox':'checkbox-proposals','buttons':'.','catalog':'.',**{k:k+'-proposals' for k in ['secure-field','search-field','collection-filters','slider','tabs','pagination']},'pagination-integers':'pagination-integer-proposals'}
prior=json.load(open('evidence/development/text-wrapping/regressions.json'))['results'];assert len(prior)==2782
regressions=[]
for row in prior:
 old,oldmeta=Path(row['currentImage']),Path(row['currentMetadata']);assert sha(old)==row['sha256'] and sha(oldmeta)==row['metadataSha256']
 new=Path('artifacts/linux')/folders[row['group']]/row['path'];meta=new.with_name(new.name+'.json')
 assert old.read_bytes()==new.read_bytes(),(row['group'],row['path'],'pixels')
 assert oldmeta.read_bytes()==meta.read_bytes(),(row['group'],row['path'],'metadata')
 regressions.append({'group':row['group'],'path':row['path'],'previousImage':str(old),'previousMetadata':str(oldmeta),'sha256':sha(new),'metadataSha256':sha(meta),'status':'byte-identical PNG and full metadata'})
write(root/'regressions.json',{'previousCandidate':'9fe238ab87dae54059782edd527b5f5187fa6c4c','imagesAndMetadataUnchanged':2782,'groups':dict(collections.Counter(r['group'] for r in regressions)),'results':regressions})
for group,folder in folders.items():
 if folder=='.':continue
 dst=root/'regression-inputs'/group;dst.mkdir(parents=True)
 for name in ['environment.json','capture-results.json']:shutil.copy2(Path('artifacts/linux')/folder/name,dst/name)
 assert json.load(open(dst/'environment.json'))['sourceInputs']==env['sourceInputs']
(root/'catalog').mkdir()
for p in Path('artifacts/linux').glob('accordion-*.png*'):shutil.copy2(p,root/'catalog'/p.name)
shutil.copytree('artifacts/accordion/host-styles',root/'host-styles')
for appearance in ['light','dark']:
 for style in ['Basic','Fusion']:assert (root/f'host-styles/{style}-{appearance}.png').read_bytes()==(root/f'catalog/accordion-{appearance}-dpr2.png').read_bytes()
shutil.copytree('artifacts/accordion/package-only/sessions',root/'sessions',ignore=shutil.ignore_patterns('*.captured'))
assert json.load(open(root/'sessions/environment.json'))['sourceInputs']==env['sourceInputs']
sessions=[json.loads(p.read_text()) for p in (root/'sessions').glob('*.json') if p.name!='environment.json'];assert len(sessions)==104
own=[s for s in sessions if s['fixture']=='accordion'];assert len(own)==8
for s in own:assert s['created']==3 and s['destroyed']==2 and s['actions']==1 and s['expanded'] is True and s['narrowHeight']==104
shutil.copytree('artifacts/accordion/package-only/catalog',root/'installed-catalog');assert len(json.load(open(root/'installed-catalog/catalog-results.json'))['captures'])==63
for name in ['contracts','references','discovery','proposals','tokens','host-styles']:shutil.copy2('artifacts/accordion/'+name+'.log',root/(name+'.log'))
for src,dst in [('build/linux/Testing/Temporary/LastTest.log','qt-tests.log'),('artifacts/accordion/full-check.txt','linux-check.log'),('artifacts/accordion/installed-check.txt','installed-check.log'),('artifacts/accordion/native-replay.json','native-replay.json'),('artifacts/accordion/previous-ci.json','previous-ci.json'),('artifacts/accordion/previous-references-ci.json','previous-references-ci.json')]:shutil.copy2(src,root/dst)
for name in ['check-installed.sh','check-display-sessions.sh']:shutil.copy2('scripts/'+name,root/name)
qt=[int(v) for v in re.findall(r'Totals: (\d+) passed, 0 failed',(root/'qt-tests.log').read_text())];assert len(qt)==2 and sum(qt)==3214,qt
native=json.load(open('evidence/reference-proposals/accordion-20261014/captures.json'))['captures']
for c in native:
 if c['api']!='BleeckerAccordion':continue
 m=json.load(open(root/'captures'/(c['path']+'.json')))
 for key in ['sourceExpandedAfterAction','sourceMounts','sourceUnmounts','sourceCounterValue','sourceTitleAfterAction','sourceInitialAfterAction','sourceContentTextAfterAction']:assert m[key]==c[key],(c['path'],key)
assert all(c['path']==r['fixture'] for c,r in zip(native,rows))
summary={api:{'captures':sum(c['api']==api for c in native),'geometryMatches':sum(c['api']==api and r.get('geometryStatus')=='passed' for c,r in zip(native,rows)),'exactMatches':sum(c['api']==api and r['status']=='passed' for c,r in zip(native,rows))} for api in ['BleeckerAccordion','BleeckerButton']}
write(root/'comparison/api-summary.json',summary)
print('Preserved 192 source cases, 2782 unchanged pairs, 104 virtual-session pairs;',sum(qt),'Qt checks')
