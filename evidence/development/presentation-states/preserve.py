import collections,hashlib,importlib.util,json,re,shutil
from pathlib import Path
root=Path('evidence/development/presentation-states');assert not root.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,j:p.write_text(json.dumps(j,indent=2)+'\n')
env=json.load(open('artifacts/linux/environment.json'))
for p,h in env['sourceInputs'].items():assert sha(Path(p))==h,p
source=Path('artifacts/linux/presentation-state-proposals');report=json.load(open(source/'capture-results.json'));assert report['status']=='captured' and len(report['results'])==272
root.mkdir();shutil.copytree(source,root/'captures');shutil.copy2('artifacts/linux/environment.json',root/'build-environment.json')
spec=importlib.util.spec_from_file_location('compare','scripts/compare-captures.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
compare.compare(Path('evidence/reference-proposals/presentation-states-20261015-v2'),root/'captures',root/'comparison')
rows=json.load(open(root/'comparison/comparison.json'))['results'];assert len(rows)==272 and not any('error' in r for r in rows)
assert sum(r.get('geometryStatus')=='passed' for r in rows)==272
folders={'desktop':'proposals','composition':'composition-proposals','selectors':'selector-proposals','checkbox':'checkbox-proposals','buttons':'.','catalog':'.',**{k:k+'-proposals' for k in ['secure-field','search-field','collection-filters','slider','tabs','pagination']},'pagination-integers':'pagination-integer-proposals'}
prior=json.load(open('artifacts/presentation-implementation/baseline.json'))['results'];assert len(prior)==2978
regressions=[]
for row in prior:
 old,oldmeta=Path(row['previousImage']),Path(row['previousMetadata'])
 new=Path(row['currentImage']);meta=new.with_name(new.name+'.json')
 assert sha(old)==row['sha256'] and sha(oldmeta)==row['metadataSha256']
 assert old.read_bytes()==new.read_bytes(),(row['group'],row['path'],'pixels')
 assert oldmeta.read_bytes()==meta.read_bytes(),(row['group'],row['path'],'metadata')
 regressions.append({**row,'status':'byte-identical PNG and full metadata'})
write(root/'regressions.json',{'previousCandidate':'25e56280b685c51d731ac26636597cf0a5953470','imagesAndMetadataUnchanged':2978,'groups':dict(collections.Counter(r['group'] for r in regressions)),'results':regressions})
folders['accordion']='accordion-proposals'
for group,folder in folders.items():
 if folder=='.':continue
 dst=root/'regression-inputs'/group;dst.mkdir(parents=True)
 for name in ['environment.json','capture-results.json']:shutil.copy2(Path('artifacts/linux')/folder/name,dst/name)
 assert json.load(open(dst/'environment.json'))['sourceInputs']==env['sourceInputs']
(root/'catalog').mkdir()
for p in Path('artifacts/linux').glob('presentation-states-*.png*'):shutil.copy2(p,root/'catalog'/p.name)
shutil.copytree('artifacts/presentation-implementation/host-styles',root/'host-styles')
for appearance in ['light','dark']:
 for style in ['Basic','Fusion']:assert (root/f'host-styles/{style}-{appearance}.png').read_bytes()==(root/f'catalog/presentation-states-{appearance}-dpr2.png').read_bytes()
shutil.copytree('artifacts/presentation-implementation/package-only/sessions',root/'sessions',ignore=shutil.ignore_patterns('*.captured'))
assert json.load(open(root/'sessions/environment.json'))['sourceInputs']==env['sourceInputs']
sessions=[json.loads(p.read_text()) for p in (root/'sessions').glob('*.json') if p.name!='environment.json'];assert len(sessions)==112
own=[s for s in sessions if s['fixture']=='presentation-states'];assert len(own)==8
for s in own:assert s['created']==2 and s['destroyed']==1 and s['actions']==4 and s['underlying']==2 and s['outside']==1
shutil.copytree('artifacts/presentation-implementation/package-only/catalog',root/'installed-catalog');assert len(json.load(open(root/'installed-catalog/catalog-results.json'))['captures'])==67
for name in ['contracts','references','discovery','proposals','tokens','host-styles']:shutil.copy2('artifacts/presentation-implementation/'+name+'.log',root/(name+'.log'))
for src,dst in [('build/linux/Testing/Temporary/LastTest.log','qt-tests.log'),('artifacts/presentation-implementation/full-check.log','linux-check.log'),('artifacts/presentation-implementation/installed-check.log','installed-check.log'),('evidence/reference-investigations/loading-native-20261015/native-replay.json','native-replay.json'),('artifacts/presentation-implementation/previous-ci.json','previous-ci.json'),('artifacts/presentation-implementation/previous-references-ci.json','previous-references-ci.json')]:shutil.copy2(src,root/dst)
for name in ['check-installed.sh','check-display-sessions.sh']:shutil.copy2('scripts/'+name,root/name)
qt=[int(v) for v in re.findall(r'Totals: (\d+) passed, 0 failed',(root/'qt-tests.log').read_text())];assert len(qt)==2 and sum(qt)==3646,qt
native=json.load(open('evidence/reference-proposals/presentation-states-20261015-v2/captures.json'))['captures']
assert all(c['path']==r['fixture'] for c,r in zip(native,rows))
summary={api:{'captures':sum(c['api']==api for c in native),'geometryMatches':sum(c['api']==api and r.get('geometryStatus')=='passed' for c,r in zip(native,rows)),'exactMatches':sum(c['api']==api and r['status']=='passed' for c,r in zip(native,rows))} for api in ['BleeckerEmptyState','BleeckerErrorState','BleeckerLoadingOverlay','BleeckerButton']}
write(root/'comparison/api-summary.json',summary)
print('Preserved 272 source cases, 2978 unchanged pairs, 112 virtual-session pairs;',sum(qt),'Qt checks')
