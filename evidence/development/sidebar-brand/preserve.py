import collections,hashlib,importlib.util,json,re,shutil
from pathlib import Path
ROOT=Path('evidence/development/sidebar-brand');work=Path('artifacts/sidebar-brand')
assert not ROOT.exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
frozen=json.loads((work/'frozen-inputs.json').read_text());env=json.loads(Path('artifacts/linux/environment.json').read_text());assert env['sourceInputs']==frozen
for name,digest in frozen.items():assert sha(name)==digest,name
ROOT.mkdir();shutil.copy2('artifacts/linux/environment.json',ROOT/'build-environment.json')
folders={'desktop':'proposals','composition':'composition-proposals','selectors':'selector-proposals','checkbox':'checkbox-proposals','secure-field':'secure-field-proposals','search-field':'search-field-proposals','collection-filters':'collection-filters-proposals','slider':'slider-proposals','tabs':'tabs-proposals','pagination':'pagination-proposals','pagination-integers':'pagination-integer-proposals','accordion':'accordion-proposals','presentation-states':'presentation-state-proposals','alert':'alert-proposals','navigation':'navigation-proposals','sidebar-brand':'sidebar-brand-proposals'}
previous=json.loads((work/'previous-captures.json').read_text());rows=[]
for old in previous['pairs']:
 image,meta=Path(old['image']),Path(old['metadata']);assert sha(image)==old['sha256'] and sha(meta)==old['metadataSha256']
 current=Path('artifacts/linux')/folders.get(old['group'],'')/old['path'];currentmeta=current.with_name(current.name+'.json')
 assert image.read_bytes()==current.read_bytes(),str(current)
 assert meta.read_bytes()==currentmeta.read_bytes(),str(currentmeta)
 rows.append({**old,'imageUnchanged':True,'metadataUnchanged':True})
assert len(rows)==3918
write(ROOT/'regressions.json',{'previousCandidate':previous['revision'],'auditedPairs':len(rows),'imagesAndMetadataUnchanged':len(rows),'changedPairs':0,'groups':dict(collections.Counter(r['group'] for r in rows)),'results':rows})
for group,folder in folders.items():
 dest=ROOT/'regression-inputs'/group;dest.mkdir(parents=True)
 for name in ['environment.json','capture-results.json']:shutil.copy2(Path('artifacts/linux')/folder/name,dest/name)
 assert json.loads((dest/'environment.json').read_text())['sourceInputs']==frozen
 result=json.loads((dest/'capture-results.json').read_text());assert result['status']=='captured' and all(r['exitCode']==0 and not r['runtimeErrors'] for r in result['results'])
shutil.copytree('artifacts/linux/sidebar-brand-proposals',ROOT/'captures')
spec=importlib.util.spec_from_file_location('compare','scripts/compare-captures.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
compare.compare(Path('evidence/reference-proposals/sidebar-brand-20261015'),ROOT/'captures',ROOT/'comparison')
child=[]
for case in json.loads(Path('evidence/reference-proposals/sidebar-brand-20261015/captures.json').read_text())['captures']:
 if case['api'] not in ['BleeckerSidebarItem','BleeckerBrandLockup']:continue
 labels={r['role']:r for r in json.loads((ROOT/'captures'/(case['path']+'.json')).read_text())['labels']}
 role='bleeckerSidebarTitle' if case['api']=='BleeckerSidebarItem' else 'bleeckerBrandLockupName'
 expected=case['layoutWitnessRects']['title'];measured=labels[role]
 delta={axis:measured[axis]-expected[axis] for axis in ['width','height']}
 child.append({'fixture':case['path'],'role':role,'source':{axis:expected[axis] for axis in delta},'candidate':{axis:measured[axis] for axis in delta},'delta':delta,'status':'passed' if all(abs(v)<=1e-6 for v in delta.values()) else 'failed; unaccepted'})
write(ROOT/'native-child-bounds.json',{'method':'actual Qt title metadata against independently identical native layout witnesses; width/height only','accepted':False,'results':child,'knownUnacceptedFailures':[r for r in child if r['status']!='passed']})
gallery=ROOT/'catalog';gallery.mkdir();shutil.copy2('artifacts/linux/environment.json',gallery/'environment.json')
for p in Path('artifacts/linux').glob('sidebar-brand-*.png*'):shutil.copy2(p,gallery/p.name)
assert len(list(gallery.glob('*.png')))==4
shutil.copytree(work/'host-styles',ROOT/'host-styles')
for appearance in ['light','dark']:
 for style in ['Basic','Fusion']:assert (ROOT/f'host-styles/{style}-{appearance}.png').read_bytes()==(gallery/f'sidebar-brand-{appearance}-dpr2.png').read_bytes()
shutil.copytree(work/'package-only/sessions',ROOT/'sessions',ignore=shutil.ignore_patterns('*.captured'))
assert json.loads((ROOT/'sessions/environment.json').read_text())['sourceInputs']==frozen
sessions=[json.loads(p.read_text()) for p in (ROOT/'sessions').glob('*.json') if p.name!='environment.json'];assert len(sessions)==152
own=[s for s in sessions if s['fixture']=='sidebar-brand'];assert len(own)==8 and all(s['sidebarBrandChecks']=='passed' and s['requests']==4 and s['logoSize']==64.5 for s in own)
shutil.copytree(work/'package-only/catalog',ROOT/'installed-catalog');shutil.copy2('artifacts/linux/environment.json',ROOT/'installed-catalog/environment.json');assert len(json.loads((ROOT/'installed-catalog/catalog-results.json').read_text())['captures'])==87
for name in ['full-check.log','contracts.log','host-styles.log','package-only.log','references.log','discovery.log','proposals.log','tokens.log','source-verification.log','feature-path-audit.json','visual-qa.json','previous-ci.json','runtime-images.json','frozen-inputs.json','acceptance.md']:
 shutil.copy2(work/name,ROOT/name)
for name in ['component-check.log','component-check2.log','consumer-check.log','consumer-check2.log','replay.log','replay2.log','native-build.log','native-build2.log','native-build3.log','native-capture.log','native-capture2.log','native-capture3.log']:
 if (work/name).exists():shutil.copy2(work/name,ROOT/('investigation-'+name))
shutil.copy2(work/'package-only/installed-check.log',ROOT/'installed-check.log')
shutil.copy2('build/linux/Testing/Temporary/LastTest.log',ROOT/'qt-tests.log')
qt=[int(x) for x in re.findall(r'Totals: (\d+) passed, 0 failed',(ROOT/'qt-tests.log').read_text())];assert len(qt)==2
comparison=json.loads((ROOT/'comparison/comparison.json').read_text())
write(ROOT/'verification-summary.json',{'qtChecks':sum(qt),'contractTests':97,'invalidStartupRefusals':30,'installedOffscreenModes':19,'virtualInstalledWindowPairs':152,'sidebarBrandVirtualPairs':8,'installedCatalogCaptures':87,'sourceInputs':len(frozen),'auditedPriorPairs':3918,'imagesAndMetadataUnchanged':3918,'changedPairs':0,'nativeComparisons':len(comparison['results']),'nativeExactMatches':sum(r['status']=='passed' for r in comparison['results']),'nativeComponentBoundsMatches':sum(r.get('geometryStatus')=='passed' for r in comparison['results']),'nativeChildBoundsChecks':len(child),'nativeChildBoundsFailures':sum(r['status']!='passed' for r in child)})
print(json.loads((ROOT/'verification-summary.json').read_text()))
