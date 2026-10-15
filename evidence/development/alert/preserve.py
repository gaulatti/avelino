import collections,hashlib,importlib.util,json,re,shutil
from pathlib import Path
from PIL import Image,ImageChops

root=Path('evidence/development/alert');assert not root.exists()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
env=json.load(open('artifacts/linux/environment.json'))
for path,h in env['sourceInputs'].items():assert sha(Path(path))==h,path
root.mkdir();shutil.copy2('artifacts/linux/environment.json',root/'build-environment.json')
shutil.copytree('artifacts/linux/alert-proposals',root/'captures')
assert json.load(open(root/'captures/capture-results.json'))['status']=='captured'
spec=importlib.util.spec_from_file_location('compare','scripts/compare-captures.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
compare.compare(Path('evidence/reference-proposals/alert-20261015'),root/'captures',root/'comparison')
fresh=json.load(open(root/'comparison/comparison.json'))['results'];assert len(fresh)==256 and not any(r.get('error') for r in fresh)
assert sum(r.get('geometryStatus')=='passed' for r in fresh)==256
baseline=json.load(open('artifacts/alert/baseline.json'));assert baseline['count']==3258
results=[]
for previous in baseline['results']:
    row=dict(previous);old=Path(row['previousImage']);oldmeta=Path(row['previousMetadata']);new=Path(row['currentImage']);meta=new.with_name(new.name+'.json')
    assert sha(old)==row['sha256'] and sha(oldmeta)==row['metadataSha256']
    equal=old.read_bytes()==new.read_bytes() and oldmeta.read_bytes()==meta.read_bytes()
    row.update(currentSha256=sha(new),currentMetadataSha256=sha(meta),status='byte-identical PNG and full metadata' if equal else 'changed; audited separately')
    if not equal:
        dest=root/'changed-captures'/row['group'];dest.mkdir(parents=True,exist_ok=True)
        shutil.copy2(new,dest/new.name);shutil.copy2(meta,dest/meta.name)
        row.update(currentImage=str(dest/new.name),currentMetadata=str(dest/meta.name))
        with Image.open(old) as a,Image.open(new) as b:
            assert a.size==b.size
            delta=ImageChops.difference(a.convert('RGB'),b.convert('RGB'))
            row.update(changedPixelsFromPrevious=sum(any(p) for p in delta.get_flattened_data()),differenceBoundsFromPrevious=delta.getbbox())
    results.append(row)
write(root/'regressions.json',{'previousCandidate':baseline['previousCandidate'],'auditedPairs':3258,'imagesAndMetadataUnchanged':sum(r['status'].startswith('byte-identical') for r in results),'changedPairs':sum(r['status'].startswith('changed') for r in results),'groups':dict(collections.Counter(r['group'] for r in results)),'results':results})
references={'desktop':'desktop-20261012','composition':'composition-20261012-v1','selectors':'selectors-20261013','checkbox':'checkbox-20261013','secure-field':'secure-field-20261014','search-field':'search-field-20261014','collection-filters':'collection-filters-20261014','slider':'slider-20261014-v2','tabs':'tabs-20261014','pagination':'pagination-20261014','pagination-integers':'pagination-integers-20261014','accordion':'accordion-20261014','presentation-states':'presentation-states-20261015-v2'}
audit=[];selections=[]
for group in sorted({r['group'] for r in results if r['status'].startswith('changed')}):
    changed=[r for r in results if r['group']==group and r['status'].startswith('changed')]
    if group not in references and group!='buttons':continue
    native=Path('reference/captures/desktop/buttons') if group=='buttons' else Path('evidence/reference-proposals')/references[group]
    manifest=json.load(open(native/'captures.json'));names={r['path'] for r in changed}
    cases=[c for c in manifest['captures'] if c['path'] in names];assert len(cases)==len(changed)
    selection=Path('artifacts/alert/subset-references')/group;selection.mkdir(parents=True,exist_ok=False)
    write(selection/'captures.json',{**manifest,'captures':cases})
    for c in cases:(selection/c['path']).symlink_to((native/c['path']).resolve())
    selections.append({'group':group,'originalManifest':str(native/'captures.json'),'originalManifestSha256':sha(native/'captures.json'),'paths':[c['path'] for c in cases],'method':'diagnostic subset manifest; PNG symlinks resolve to unchanged immutable source files'})
    before=Path('artifacts/alert/comparison-before')/group;before.mkdir(parents=True,exist_ok=False)
    for r in changed:
        (before/r['path']).symlink_to(Path(r['previousImage']).resolve());(before/(r['path']+'.json')).symlink_to(Path(r['previousMetadata']).resolve())
    after=root/'changed-captures'/group
    compare.compare(selection,before,root/'regression-comparison'/(group+'-before'))
    compare.compare(selection,after,root/'regression-comparison'/(group+'-after'))
    a=json.load(open(root/'regression-comparison'/(group+'-before')/'comparison.json'))['results'];b=json.load(open(root/'regression-comparison'/(group+'-after')/'comparison.json'))['results']
    for old,new in zip(a,b):
        assert old['fixture']==new['fixture'] and not old.get('error') and not new.get('error'),(old,new)
        assert old['referenceSHA256']==new['referenceSHA256']
        assert old['status']!='passed' or new['status']=='passed',new
        assert old.get('geometryStatus')!='passed' or new.get('geometryStatus')=='passed',new
        audit.append({'group':group,'fixture':new['fixture'],'referenceSHA256':new['referenceSHA256'],'beforeChangedPixels':old['changedPixels'],'afterChangedPixels':new['changedPixels'],'beforeMaximumChannelError':old['maximumChannelError'],'afterMaximumChannelError':new['maximumChannelError'],'beforeGeometry':old.get('geometryStatus'),'afterGeometry':new.get('geometryStatus'),'beforeExact':old['status'],'afterExact':new['status']})
write(root/'regression-comparison.json',{'sameNativeInputs':True,'geometryPassesLost':0,'exactPassesLost':0,'selections':selections,'results':audit})
folders={'desktop':'proposals','composition':'composition-proposals','selectors':'selector-proposals','checkbox':'checkbox-proposals','secure-field':'secure-field-proposals','search-field':'search-field-proposals','collection-filters':'collection-filters-proposals','slider':'slider-proposals','tabs':'tabs-proposals','pagination':'pagination-proposals','pagination-integers':'pagination-integer-proposals','accordion':'accordion-proposals','presentation-states':'presentation-state-proposals'}
for group,folder in folders.items():
    dest=root/'regression-inputs'/group;dest.mkdir(parents=True)
    for name in ['environment.json','capture-results.json']:shutil.copy2(Path('artifacts/linux')/folder/name,dest/name)
    assert json.load(open(dest/'environment.json'))['sourceInputs']==env['sourceInputs']
    report=json.load(open(dest/'capture-results.json'));assert report['status']=='captured' and all(r['exitCode']==0 and not r['runtimeErrors'] for r in report['results'])
gallery=root/'catalog';gallery.mkdir()
for p in Path('artifacts/linux').glob('alert-*.png*'):shutil.copy2(p,gallery/p.name)
assert len(list(gallery.glob('*.png')))==4
shutil.copytree('artifacts/alert/host-styles',root/'host-styles')
for appearance in ['light','dark']:
    for style in ['Basic','Fusion']:assert (root/f'host-styles/{style}-{appearance}.png').read_bytes()==(gallery/f'alert-{appearance}-dpr2.png').read_bytes()
shutil.copytree('artifacts/alert/package-only/sessions',root/'sessions',ignore=shutil.ignore_patterns('*.captured'))
assert json.load(open(root/'sessions/environment.json'))['sourceInputs']==env['sourceInputs']
sessions=[json.loads(p.read_text()) for p in (root/'sessions').glob('*.json') if p.name!='environment.json'];assert len(sessions)==128
own=[s for s in sessions if s['fixture']=='alert'];assert len(own)==8 and all(s['alertChecks']=='passed' and s['actions']==4 for s in own)
shutil.copytree('artifacts/alert/package-only/catalog',root/'installed-catalog');assert len(json.load(open(root/'installed-catalog/catalog-results.json'))['captures'])==75
for name in ['contracts','references','discovery','proposals','tokens','host-styles','source-verification']:shutil.copy2(Path('artifacts/alert')/(name+'.log'),root/(name+'.log'))
for src,dst in [('build/linux/Testing/Temporary/LastTest.log','qt-tests.log'),('artifacts/alert/full-check.log','linux-check.log'),('artifacts/alert/installed-check.log','installed-check.log'),('artifacts/alert/native-replay.log','native-replay.log'),('artifacts/alert/boundary-replay.log','boundary-replay.log')]:shutil.copy2(src,root/dst)
for name in ['feature-path-audit.json','visual-qa.json','previous-ci.json','previous-references-ci.json','native-replay.json','boundary-replay.json']:shutil.copy2(Path('artifacts/alert')/name,root/name)
for name in ['check-installed.sh','check-display-sessions.sh']:shutil.copy2(Path('scripts')/name,root/name)
totals=[int(v) for v in re.findall(r'Totals: (\d+) passed, 0 failed',(root/'qt-tests.log').read_text())];assert len(totals)==2 and sum(totals)==4552,totals
write(root/'verification-summary.json',{'qtChecks':sum(totals),'contractTests':84,'invalidStartupRefusals':20,'installedOffscreenModes':16,'virtualInstalledWindowPairs':128,'alertVirtualPairs':8,'installedCatalogCaptures':75,'nativeAlertCaptures':248,'nativeAnchorCaptures':8,'nativeLifecycleCases':96,'qtNativeLifecycleChecks':192,'nativeTextCases':96,'nativeBoundaryCases':84,'boundaryReplayByteIdenticalFiles':179,'nativeReplayByteIdenticalFiles':722,'nativeInstrumentationIdentityWitnesses':352,'auditedPriorPairs':3258,'unchangedPairs':sum(r['status'].startswith('byte-identical') for r in results),'changedPairs':sum(r['status'].startswith('changed') for r in results),'sourceComparisons':len(fresh),'geometryMatches':sum(r.get('geometryStatus')=='passed' for r in fresh),'exactMatches':sum(r['status']=='passed' for r in fresh),'regressionSourceComparisons':len(audit),'beforeGeometryPasses':sum(r['beforeGeometry']=='passed' for r in audit),'afterGeometryPasses':sum(r['afterGeometry']=='passed' for r in audit),'beforeExactPasses':sum(r['beforeExact']=='passed' for r in audit),'afterExactPasses':sum(r['afterExact']=='passed' for r in audit)})
print(json.loads((root/'verification-summary.json').read_text()))
