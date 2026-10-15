import collections, hashlib, importlib.util, json, re, shutil
from pathlib import Path
from PIL import Image, ImageChops

root=Path('evidence/development/spinner')
assert not root.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
env=json.load(open('artifacts/linux/environment.json'))
for path,h in env['sourceInputs'].items():assert sha(Path(path))==h,path
root.mkdir()
shutil.copy2('artifacts/linux/environment.json',root/'build-environment.json')
baseline=json.load(open('artifacts/spinner/baseline.json'));assert baseline['count']==3254
results=[]
for previous in baseline['results']:
    row=dict(previous);old=Path(row['previousImage']);oldmeta=Path(row['previousMetadata']);new=Path(row['currentImage']);meta=new.with_name(new.name+'.json')
    assert sha(old)==row['sha256'] and sha(oldmeta)==row['metadataSha256']
    equal=old.read_bytes()==new.read_bytes() and oldmeta.read_bytes()==meta.read_bytes()
    row.update(currentSha256=sha(new),currentMetadataSha256=sha(meta),status='byte-identical PNG and full metadata' if equal else 'changed; audited separately')
    if not equal:
        dest=root/'captures'/row['group'];dest.mkdir(parents=True,exist_ok=True)
        shutil.copy2(new,dest/new.name);shutil.copy2(meta,dest/meta.name);row['currentImage']=str(dest/new.name);row['currentMetadata']=str(dest/meta.name)
        with Image.open(old) as a,Image.open(new) as b:
            assert a.size==b.size
            difference=ImageChops.difference(a.convert('RGB'),b.convert('RGB'))
            row['changedPixelsFromPrevious']=sum(any(p) for p in difference.get_flattened_data())
            row['maximumChannelErrorFromPrevious']=max(max(p) for p in difference.get_flattened_data())
            row['differenceBoundsFromPrevious']=difference.getbbox()
        row['beforeComponentSize']=json.loads(oldmeta.read_text()).get('componentSize')
        row['afterComponentSize']=json.loads(meta.read_text()).get('componentSize')
        assert row['group'] in ['desktop','presentation-states','catalog','presentation-catalog'],row
        if row['group']=='desktop':assert row['path'].startswith('spinner-'),row
        if row['group']=='presentation-states':assert json.loads(meta.read_text())['api']=='BleeckerLoadingOverlay',row
    results.append(row)
write(root/'regressions.json',{'previousCandidate':baseline['previousCandidate'],'auditedPairs':len(results),'imagesAndMetadataUnchanged':sum(r['status'].startswith('byte-identical') for r in results),'changedPairs':sum(r['status'].startswith('changed') for r in results),'groups':dict(collections.Counter(r['group'] for r in results)),'results':results})
spec=importlib.util.spec_from_file_location('compare','scripts/compare-captures.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
comparisons=[]
for group,ref,folder,api in [('desktop','desktop-20261012','proposals','BleeckerLoadingSpinner'),('presentation-states','presentation-states-20261015-v2','presentation-state-proposals','BleeckerLoadingOverlay')]:
    native=Path('evidence/reference-proposals')/ref;current=Path('artifacts/linux')/folder
    before=Path('artifacts/spinner/comparison-before')/group;before.mkdir(parents=True,exist_ok=False)
    for row in results:
        if row['group']!=group:continue
        shutil.copy2(row['previousImage'],before/row['path']);shutil.copy2(row['previousMetadata'],before/(row['path']+'.json'))
    compare.compare(native,before,root/'comparison'/(group+'-before'),[api])
    compare.compare(native,current,root/'comparison'/(group+'-after'),[api])
    old=json.load(open(root/'comparison'/(group+'-before')/'comparison.json'))['results'];new=json.load(open(root/'comparison'/(group+'-after')/'comparison.json'))['results']
    assert len(old)==len(new)
    for a,b in zip(old,new):
        assert a['fixture']==b['fixture'] and not a.get('error') and not b.get('error'),(a,b)
        assert a['referenceSHA256']==b['referenceSHA256']
        assert a['status']!='passed' or b['status']=='passed',b
        assert a.get('geometryStatus')!='passed' or b.get('geometryStatus')=='passed',b
        comparisons.append({'group':group,'fixture':b['fixture'],'referenceSHA256':b['referenceSHA256'],'beforeChangedPixels':a['changedPixels'],'afterChangedPixels':b['changedPixels'],'beforeMaximumChannelError':a['maximumChannelError'],'afterMaximumChannelError':b['maximumChannelError'],'beforeGeometry':a.get('geometryStatus'),'afterGeometry':b.get('geometryStatus'),'beforeExact':a['status'],'afterExact':b['status']})
    dest=root/'regression-inputs'/group;dest.mkdir(parents=True)
    for name in ['environment.json','capture-results.json']:shutil.copy2(current/name,dest/name)
    assert json.load(open(dest/'environment.json'))['sourceInputs']==env['sourceInputs']
    report=json.load(open(dest/'capture-results.json'));assert report['status']=='captured' and all(r['exitCode']==0 and not r['runtimeErrors'] for r in report['results'])
for group,folder in {'composition':'composition-proposals','selectors':'selector-proposals','checkbox':'checkbox-proposals','secure-field':'secure-field-proposals','search-field':'search-field-proposals','collection-filters':'collection-filters-proposals','slider':'slider-proposals','tabs':'tabs-proposals','pagination':'pagination-proposals','pagination-integers':'pagination-integer-proposals','accordion':'accordion-proposals'}.items():
    dest=root/'regression-inputs'/group;dest.mkdir(parents=True)
    for name in ['environment.json','capture-results.json']:shutil.copy2(Path('artifacts/linux')/folder/name,dest/name)
    assert json.load(open(dest/'environment.json'))['sourceInputs']==env['sourceInputs']
    report=json.load(open(dest/'capture-results.json'));assert report['status']=='captured' and all(r['exitCode']==0 and not r['runtimeErrors'] for r in report['results'])
write(root/'comparison/change-audit.json',{'sameNativeInputs':True,'geometryPassesLost':0,'exactPassesLost':0,'results':comparisons})
for row in results:
    if row['group'] not in ['desktop','presentation-states'] or not row['status'].startswith('changed'):continue
    assert any(c['group']==row['group'] and c['fixture']==row['path'] for c in comparisons),row
gallery=root/'catalog';gallery.mkdir()
for path in Path('artifacts/linux').glob('spinner-*.png*'):shutil.copy2(path,gallery/path.name)
assert len(list(gallery.glob('*.png')))==4
shutil.copytree('artifacts/spinner/host-styles',root/'host-styles')
for appearance in ['light','dark']:
    for style in ['Basic','Fusion']:assert (root/f'host-styles/{style}-{appearance}.png').read_bytes()==(gallery/f'spinner-{appearance}-dpr2.png').read_bytes()
shutil.copytree('artifacts/spinner/package-only/sessions',root/'sessions',ignore=shutil.ignore_patterns('*.captured'))
assert json.load(open(root/'sessions/environment.json'))['sourceInputs']==env['sourceInputs']
sessions=[json.loads(p.read_text()) for p in (root/'sessions').glob('*.json') if p.name!='environment.json'];assert len(sessions)==120
own=[s for s in sessions if s['fixture']=='spinner'];assert len(own)==8 and all(s['spinnerChecks']=='passed' and s['actions']==3 for s in own)
shutil.copytree('artifacts/spinner/package-only/catalog',root/'installed-catalog')
assert len(json.load(open(root/'installed-catalog/catalog-results.json'))['captures'])==71
for name in ['contracts','references','discovery','proposals','tokens','host-styles','source-verification']:
    shutil.copy2(Path('artifacts/spinner')/(name+'.log'),root/(name+'.log'))
for src,dst in [('build/linux/Testing/Temporary/LastTest.log','qt-tests.log'),('artifacts/spinner/full-check.log','linux-check.log'),('artifacts/spinner/installed-check.log','installed-check.log'),('artifacts/spinner/native-replay.log','native-replay.log')]:shutil.copy2(src,root/dst)
for name in ['feature-path-audit.json','visual-qa.json','previous-ci.json','previous-references-ci.json','native-replay.json']:shutil.copy2(Path('artifacts/spinner')/name,root/name)
for name in ['check-installed.sh','check-display-sessions.sh']:shutil.copy2(Path('scripts')/name,root/name)
totals=[int(v) for v in re.findall(r'Totals: (\d+) passed, 0 failed',(root/'qt-tests.log').read_text())];assert len(totals)==2 and sum(totals)==3922,totals
write(root/'verification-summary.json',{'qtChecks':sum(totals),'contractTests':80,'invalidStartupRefusals':16,'installedOffscreenModes':15,'virtualInstalledWindowPairs':120,'spinnerVirtualPairs':8,'installedCatalogCaptures':71,'nativeContexts':186,'nativeLoadingButtonCases':112,'controlledNativeFrames':144,'nativeReplayByteIdenticalFiles':335,'auditedPriorPairs':3254,'unchangedPairs':sum(r['status'].startswith('byte-identical') for r in results),'changedPairs':sum(r['status'].startswith('changed') for r in results),'sourceComparisons':len(comparisons),'beforeGeometryPasses':sum(r['beforeGeometry']=='passed' for r in comparisons),'afterGeometryPasses':sum(r['afterGeometry']=='passed' for r in comparisons),'beforeExactPasses':sum(r['beforeExact']=='passed' for r in comparisons),'afterExactPasses':sum(r['afterExact']=='passed' for r in comparisons)})
print(json.loads((root/'verification-summary.json').read_text()))
