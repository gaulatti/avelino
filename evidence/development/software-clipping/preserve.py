import collections,hashlib,importlib.util,json,re,shutil
from pathlib import Path
from PIL import Image,ImageChops

root=Path('evidence/development/software-clipping');assert not root.exists()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
env=json.load(open('artifacts/linux/environment.json'))
for path,h in env['sourceInputs'].items():assert sha(Path(path))==h,path
root.mkdir();shutil.copy2('artifacts/linux/environment.json',root/'build-environment.json')
baseline=json.load(open('artifacts/software-clipping/baseline.json'));assert baseline['count']==3518
results=[]
for previous in baseline['results']:
 row=dict(previous);old=Path(row['previousImage']);oldmeta=Path(row['previousMetadata']);new=Path(row['currentImage']);meta=new.with_name(new.name+'.json')
 assert sha(old)==row['sha256'] and sha(oldmeta)==row['metadataSha256']
 imageEqual=old.read_bytes()==new.read_bytes();metaEqual=oldmeta.read_bytes()==meta.read_bytes()
 row.update(currentSha256=sha(new),currentMetadataSha256=sha(meta),imageUnchanged=imageEqual,metadataUnchanged=metaEqual,status='byte-identical PNG and full metadata' if imageEqual and metaEqual else 'changed; audited separately')
 if not imageEqual or not metaEqual:
  dest=root/'changed-captures'/row['group'];dest.mkdir(parents=True,exist_ok=True)
  shutil.copy2(new,dest/new.name);shutil.copy2(meta,dest/meta.name)
  row.update(currentImage=str(dest/new.name),currentMetadata=str(dest/meta.name))
  oldRecord=json.loads(oldmeta.read_text());newRecord=json.loads(meta.read_text())
  row['changedMetadataKeys']=[k for k in sorted(set(oldRecord)|set(newRecord)) if oldRecord.get(k)!=newRecord.get(k)]
  with Image.open(old) as a,Image.open(new) as b:
   assert a.size==b.size,(old,new)
   delta=ImageChops.difference(a.convert('RGBA'),b.convert('RGBA'))
   row.update(changedPixelsFromPrevious=sum(any(p) for p in delta.get_flattened_data()),differenceBoundsFromPrevious=delta.getbbox(alpha_only=False))
 results.append(row)
write(root/'regressions.json',{'previousCandidate':baseline['previousCandidate'],'auditedPairs':3518,'imagesAndMetadataUnchanged':sum(r['status'].startswith('byte-identical') for r in results),'changedPairs':sum(r['status'].startswith('changed') for r in results),'imagesUnchanged':sum(r['imageUnchanged'] for r in results),'metadataUnchanged':sum(r['metadataUnchanged'] for r in results),'groups':dict(collections.Counter(r['group'] for r in results)),'results':results})
spec=importlib.util.spec_from_file_location('compare','scripts/compare-captures.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
references={'desktop':'desktop-20261012','composition':'composition-20261012-v1','selectors':'selectors-20261013','checkbox':'checkbox-20261013','secure-field':'secure-field-20261014','search-field':'search-field-20261014','collection-filters':'collection-filters-20261014','slider':'slider-20261014-v2','tabs':'tabs-20261014','pagination':'pagination-20261014','pagination-integers':'pagination-integers-20261014','accordion':'accordion-20261014','presentation-states':'presentation-states-20261015-v2','alert':'alert-20261015'}
audit=[];selections=[]
for group in sorted({r['group'] for r in results if r['status'].startswith('changed')}):
 changed=[r for r in results if r['group']==group and r['status'].startswith('changed')]
 if group not in references and group!='buttons':continue
 native=Path('reference/captures/desktop/buttons') if group=='buttons' else Path('evidence/reference-proposals')/references[group]
 manifest=json.load(open(native/'captures.json'));names={r['path'] for r in changed}
 cases=[c for c in manifest['captures'] if c['path'] in names];assert len(cases)==len(changed)
 selection=Path('artifacts/software-clipping/subset-references')/group;selection.mkdir(parents=True,exist_ok=False)
 write(selection/'captures.json',{**manifest,'captures':cases})
 for c in cases:(selection/c['path']).symlink_to((native/c['path']).resolve())
 selections.append({'group':group,'originalManifest':str(native/'captures.json'),'originalManifestSha256':sha(native/'captures.json'),'paths':[c['path'] for c in cases],'method':'diagnostic subset; all native source images unchanged'})
 before=Path('artifacts/software-clipping/comparison-before')/group;before.mkdir(parents=True,exist_ok=False)
 for r in changed:
  (before/r['path']).symlink_to(Path(r['previousImage']).resolve());(before/(r['path']+'.json')).symlink_to(Path(r['previousMetadata']).resolve())
 compare.compare(selection,before,root/'regression-comparison'/(group+'-before'))
 compare.compare(selection,root/'changed-captures'/group,root/'regression-comparison'/(group+'-after'))
 a=json.load(open(root/'regression-comparison'/(group+'-before')/'comparison.json'))['results'];b=json.load(open(root/'regression-comparison'/(group+'-after')/'comparison.json'))['results']
 for old,new in zip(a,b):
  assert old['fixture']==new['fixture'] and not old.get('error') and not new.get('error'),(old,new)
  assert old['referenceSHA256']==new['referenceSHA256']
  assert old['status']!='passed' or new['status']=='passed',new
  assert old.get('geometryStatus')!='passed' or new.get('geometryStatus')=='passed',new
  audit.append({'group':group,'fixture':new['fixture'],'referenceSHA256':new['referenceSHA256'],'beforeChangedPixels':old['changedPixels'],'afterChangedPixels':new['changedPixels'],'beforeMaximumChannelError':old['maximumChannelError'],'afterMaximumChannelError':new['maximumChannelError'],'beforeGeometry':old.get('geometryStatus'),'afterGeometry':new.get('geometryStatus'),'beforeExact':old['status'],'afterExact':new['status']})
write(root/'regression-comparison.json',{'sameNativeInputs':True,'geometryPassesLost':0,'exactPassesLost':0,'selections':selections,'results':audit})
folders={'desktop':'proposals','composition':'composition-proposals','selectors':'selector-proposals','checkbox':'checkbox-proposals','secure-field':'secure-field-proposals','search-field':'search-field-proposals','collection-filters':'collection-filters-proposals','slider':'slider-proposals','tabs':'tabs-proposals','pagination':'pagination-proposals','pagination-integers':'pagination-integer-proposals','accordion':'accordion-proposals','presentation-states':'presentation-state-proposals','alert':'alert-proposals'}
for group,folder in folders.items():
 dest=root/'regression-inputs'/group;dest.mkdir(parents=True)
 for name in ['environment.json','capture-results.json']:shutil.copy2(Path('artifacts/linux')/folder/name,dest/name)
 assert json.load(open(dest/'environment.json'))['sourceInputs']==env['sourceInputs']
 report=json.load(open(dest/'capture-results.json'));assert report['status']=='captured' and all(r['exitCode']==0 and not r['runtimeErrors'] for r in report['results'])
gallery=root/'catalog';gallery.mkdir()
for p in Path('artifacts/linux').glob('clipping-*.png*'):shutil.copy2(p,gallery/p.name)
assert len(list(gallery.glob('*.png')))==4
shutil.copytree('artifacts/software-clipping/host-styles',root/'host-styles')
for appearance in ['light','dark']:
 for style in ['Basic','Fusion']:assert (root/f'host-styles/{style}-{appearance}.png').read_bytes()==(gallery/f'clipping-{appearance}-dpr2.png').read_bytes()
shutil.copytree('artifacts/software-clipping/package-only/sessions',root/'sessions',ignore=shutil.ignore_patterns('*.captured'))
assert json.load(open(root/'sessions/environment.json'))['sourceInputs']==env['sourceInputs']
sessions=[json.loads(p.read_text()) for p in (root/'sessions').glob('*.json') if p.name!='environment.json'];assert len(sessions)==136,len(sessions)
own=[s for s in sessions if s['fixture']=='clipping'];assert len(own)==8 and all(s['clippingChecks']=='passed' and s['actions']==3 for s in own)
shutil.copytree('artifacts/software-clipping/package-only/catalog',root/'installed-catalog');assert len(json.load(open(root/'installed-catalog/catalog-results.json'))['captures'])==79
for name in ['contracts','references','discovery','proposals','tokens','host-styles','linux-boundary','toolchain-image']:shutil.copy2(Path('artifacts/software-clipping')/(name+'.log'),root/(name+'.log'))
for src,dst in [('build/linux/Testing/Temporary/LastTest.log','qt-tests.log'),('artifacts/software-clipping/full-check.log','linux-check.log'),('artifacts/software-clipping/installed-check.log','installed-check.log')]:shutil.copy2(src,root/dst)
for name in ['feature-path-audit.json','visual-qa.json','previous-ci.json']:shutil.copy2(Path('artifacts/software-clipping')/name,root/name)
for name in ['check-installed.sh','check-display-sessions.sh']:shutil.copy2(Path('scripts')/name,root/name)
shutil.copytree('artifacts/software-clipping/first-pass',root/'first-pass')
shutil.copytree('artifacts/software-clipping/second-pass',root/'second-pass')
shutil.copytree('artifacts/software-clipping/third-pass',root/'third-pass')
shutil.copytree('artifacts/software-clipping/fourth-pass',root/'fourth-pass')
shutil.copytree('artifacts/software-clipping/fifth-pass',root/'fifth-pass',ignore=shutil.ignore_patterns('full-evidence','package-only','subset-references','comparison-before','rhi-interior-raster-diagnostic.log'))
shutil.copytree('artifacts/software-clipping/qt-alpha-probe',root/'qt-alpha-probe',ignore=shutil.ignore_patterns('build'))
for name in ['focused-dpr1.log','focused-dpr2.log','focused-opengl-dpr1.log','focused-opengl-dpr2.log','consumer-focused-dpr1.log','consumer-focused-dpr2.log','consumer-opengl-dpr1.log','consumer-opengl-dpr2.log']:shutil.copy2(Path('artifacts/software-clipping')/name,root/name)
totals=[int(v) for v in re.findall(r'Totals: (\d+) passed, 0 failed',(root/'qt-tests.log').read_text())];assert len(totals)==2 and sum(totals)==4608,totals
write(root/'verification-summary.json',{'qtChecks':sum(totals),'contractTests':84,'invalidStartupRefusals':20,'installedOffscreenModes':17,'virtualInstalledWindowPairs':136,'clippingVirtualPairs':8,'installedCatalogCaptures':79,'sourceInputs':len(env['sourceInputs']),'auditedPriorPairs':3518,'unchangedPairs':sum(r['status'].startswith('byte-identical') for r in results),'changedPairs':sum(r['status'].startswith('changed') for r in results),'regressionSourceComparisons':len(audit),'beforeGeometryPasses':sum(r['beforeGeometry']=='passed' for r in audit),'afterGeometryPasses':sum(r['afterGeometry']=='passed' for r in audit),'beforeExactPasses':sum(r['beforeExact']=='passed' for r in audit),'afterExactPasses':sum(r['afterExact']=='passed' for r in audit)})
print(json.loads((root/'verification-summary.json').read_text()))
