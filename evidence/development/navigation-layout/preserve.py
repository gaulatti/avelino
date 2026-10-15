import collections,hashlib,importlib.util,json,re,shutil
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path('evidence/development/navigation-layout')
assert not ROOT.exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
work=Path('artifacts/navigation-implementation')
frozen=json.loads((work/'frozen-inputs.json').read_text());env=json.loads(Path('artifacts/linux/environment.json').read_text())
assert env['sourceInputs']==frozen
for name,digest in frozen.items():assert sha(name)==digest,name
ROOT.mkdir();shutil.copy2('artifacts/linux/environment.json',ROOT/'build-environment.json')
folders={'desktop':'proposals','composition':'composition-proposals','selectors':'selector-proposals','checkbox':'checkbox-proposals','secure-field':'secure-field-proposals','search-field':'search-field-proposals','collection-filters':'collection-filters-proposals','slider':'slider-proposals','tabs':'tabs-proposals','pagination':'pagination-proposals','pagination-integers':'pagination-integer-proposals','accordion':'accordion-proposals','presentation-states':'presentation-state-proposals','alert':'alert-proposals','navigation':'navigation-proposals'}
references={'desktop':'desktop-20261012','composition':'composition-20261012-v1','selectors':'selectors-20261013','checkbox':'checkbox-20261013','secure-field':'secure-field-20261014','search-field':'search-field-20261014','collection-filters':'collection-filters-20261014','slider':'slider-20261014-v2','tabs':'tabs-20261014','pagination':'pagination-20261014','pagination-integers':'pagination-integers-20261014','accordion':'accordion-20261014','presentation-states':'presentation-states-20261015-v2','alert':'alert-20261015','navigation':'navigation-layout-20261015'}
previous=json.loads((work/'previous-captures.json').read_text());rows=[]
for old in previous['pairs']:
 oldimage,oldmeta=Path(old['image']),Path(old['metadata'])
 assert sha(oldimage)==old['sha256'] and sha(oldmeta)==old['metadataSha256']
 current=Path('artifacts/linux')/(folders[old['group']] if old['group'] in folders else '')/old['path'];meta=current.with_name(current.name+'.json')
 image_equal=oldimage.read_bytes()==current.read_bytes();meta_equal=oldmeta.read_bytes()==meta.read_bytes()
 row={'group':old['group'],'path':old['path'],'previousImage':str(oldimage),'previousMetadata':str(oldmeta),'sha256':old['sha256'],'metadataSha256':old['metadataSha256'],'currentImage':str(current),'currentMetadata':str(meta),'currentSha256':sha(current),'currentMetadataSha256':sha(meta),'imageUnchanged':image_equal,'metadataUnchanged':meta_equal}
 if not image_equal or not meta_equal:
  dest=ROOT/'changed-captures'/old['group'];dest.mkdir(parents=True,exist_ok=True)
  shutil.copy2(current,dest/current.name);shutil.copy2(meta,dest/meta.name)
  row.update(currentImage=str(dest/current.name),currentMetadata=str(dest/meta.name))
  a,b=json.loads(oldmeta.read_text()),json.loads(meta.read_text())
  row['changedMetadataKeys']=[k for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k)]
  with Image.open(oldimage) as a,Image.open(current) as b:
   assert a.size==b.size
   diff=ImageChops.difference(a.convert('RGBA'),b.convert('RGBA'))
   row['changedPixelsFromPrevious']=sum(any(pixel) for pixel in diff.get_flattened_data());row['differenceBoundsFromPrevious']=diff.getbbox(alpha_only=False)
 rows.append(row)
assert len(rows)==3522
write(ROOT/'regressions.json',{'previousCandidate':previous['revision'],'auditedPairs':len(rows),'imagesAndMetadataUnchanged':sum(r['imageUnchanged'] and r['metadataUnchanged'] for r in rows),'changedPairs':sum(not(r['imageUnchanged'] and r['metadataUnchanged']) for r in rows),'imagesUnchanged':sum(r['imageUnchanged'] for r in rows),'metadataUnchanged':sum(r['metadataUnchanged'] for r in rows),'groups':dict(collections.Counter(r['group'] for r in rows)),'results':rows})
for group,folder in folders.items():
 dest=ROOT/'regression-inputs'/group;dest.mkdir(parents=True)
 for name in ['environment.json','capture-results.json']:shutil.copy2(Path('artifacts/linux')/folder/name,dest/name)
 assert json.loads((dest/'environment.json').read_text())['sourceInputs']==frozen
 capture=json.loads((dest/'capture-results.json').read_text());assert capture['status']=='captured' and all(r['exitCode']==0 and not r['runtimeErrors'] for r in capture['results'])
shutil.copytree('artifacts/linux/navigation-proposals',ROOT/'captures')
spec=importlib.util.spec_from_file_location('compare','scripts/compare-captures.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
compare.compare(Path('evidence/reference-proposals/navigation-layout-20261015'),ROOT/'captures',ROOT/'comparison')
child_bounds=[]
source_cases=json.loads(Path('evidence/reference-proposals/navigation-layout-20261015/captures.json').read_text())['captures']
for case in source_cases:
 if case['api']=='BleeckerButton':continue
 metadata=json.loads((ROOT/'captures'/(case['path']+'.json')).read_text())
 labels={r['role']:r for r in metadata['labels']}
 mapping={}
 if case['api']=='BleeckerPageHeader':
  mapping={'bleeckerPageHeader'+key[0].upper()+key[1:]:key for key in ['eyebrow','title','description']}
 else:
  mapping={**{'bleeckerBreadcrumbItem'+str(i):'button-'+str(i) for i in range(len(case['titles']))},**{'bleeckerBreadcrumbSeparator'+str(i):'separator-'+str(i) for i in range(1,len(case['titles']))}}
 for role,key in mapping.items():
  measured=labels[role];expected=case['layoutWitnessRects'][key]
  delta={axis:measured[axis]-expected[axis] for axis in ['width','height']}
  child_bounds.append({'fixture':case['path'],'role':role,'source':{axis:expected[axis] for axis in ['width','height']},'candidate':{axis:measured[axis] for axis in ['width','height']},'delta':delta,'status':'passed' if all(abs(v)<=1e-6 for v in delta.values()) else 'failed; unaccepted'})
failures=[r for r in child_bounds if r['status']!='passed']
assert all(r['fixture'].startswith('page-header-unicode-') and r['role']=='bleeckerPageHeaderTitle' for r in failures),failures
write(ROOT/'native-child-bounds.json',{'method':'actual visible Qt label/button/separator metadata against sealed native layout witnesses; width/height only, not glyph raster or scene paint alignment','results':child_bounds,'knownUnacceptedFailures':failures,'accepted':False})
audit=[]
for group in sorted({r['group'] for r in rows if not(r['imageUnchanged'] and r['metadataUnchanged'])}):
 changed=[r for r in rows if r['group']==group and not(r['imageUnchanged'] and r['metadataUnchanged'])]
 if group not in references and group!='buttons':continue
 native=Path('reference/captures/desktop/buttons') if group=='buttons' else Path('evidence/reference-proposals')/references[group]
 manifest=json.loads((native/'captures.json').read_text());names={r['path'] for r in changed};cases=[c for c in manifest['captures'] if c['path'] in names];assert len(cases)==len(changed)
 subset=work/'subset-references'/group;subset.mkdir(parents=True)
 write(subset/'captures.json',{**manifest,'captures':cases})
 before=work/'comparison-before'/group;before.mkdir(parents=True)
 for c in cases:(subset/c['path']).symlink_to((native/c['path']).resolve())
 for r in changed:
  (before/r['path']).symlink_to(Path(r['previousImage']).resolve());(before/(r['path']+'.json')).symlink_to(Path(r['previousMetadata']).resolve())
 compare.compare(subset,before,ROOT/'regression-comparison'/(group+'-before'))
 compare.compare(subset,ROOT/'changed-captures'/group,ROOT/'regression-comparison'/(group+'-after'))
 a=json.loads((ROOT/'regression-comparison'/(group+'-before')/'comparison.json').read_text())['results'];b=json.loads((ROOT/'regression-comparison'/(group+'-after')/'comparison.json').read_text())['results']
 for old,new in zip(a,b):
  assert not old.get('error') and not new.get('error') and old['referenceSHA256']==new['referenceSHA256']
  assert old['status']!='passed' or new['status']=='passed'
  assert old.get('geometryStatus')!='passed' or new.get('geometryStatus')=='passed'
  audit.append({'group':group,'fixture':new['fixture'],'referenceSHA256':new['referenceSHA256'],'beforeChangedPixels':old['changedPixels'],'afterChangedPixels':new['changedPixels'],'beforeGeometry':old.get('geometryStatus'),'afterGeometry':new.get('geometryStatus'),'beforeExact':old['status'],'afterExact':new['status']})
write(ROOT/'regression-comparison.json',{'sameNativeInputs':True,'geometryPassesLost':0,'exactPassesLost':0,'results':audit})
gallery=ROOT/'catalog';gallery.mkdir();shutil.copy2('artifacts/linux/environment.json',gallery/'environment.json')
for p in Path('artifacts/linux').glob('navigation-*.png*'):shutil.copy2(p,gallery/p.name)
assert len(list(gallery.glob('*.png')))==4
shutil.copytree(work/'host-styles',ROOT/'host-styles')
for appearance in ['light','dark']:
 for style in ['Basic','Fusion']:assert (ROOT/f'host-styles/{style}-{appearance}.png').read_bytes()==(gallery/f'navigation-{appearance}-dpr2.png').read_bytes()
shutil.copytree(work/'package-only/sessions',ROOT/'sessions',ignore=shutil.ignore_patterns('*.captured'))
assert json.loads((ROOT/'sessions/environment.json').read_text())['sourceInputs']==frozen
sessions=[json.loads(p.read_text()) for p in (ROOT/'sessions').glob('*.json') if p.name!='environment.json'];assert len(sessions)==144
own=[s for s in sessions if s['fixture']=='navigation'];assert len(own)==8 and all(s['navigationChecks']=='passed' and s['modelRestoredForCapture'] is True for s in own)
shutil.copytree(work/'package-only/catalog',ROOT/'installed-catalog');shutil.copy2('artifacts/linux/environment.json',ROOT/'installed-catalog/environment.json');assert len(json.loads((ROOT/'installed-catalog/catalog-results.json').read_text())['captures'])==83
for name in ['full-check.log','contracts.log','host-styles.log','package-only.log','references.log','discovery.log','proposals.log','tokens.log','source-verification.log','feature-path-audit.json','visual-qa.json','source-color-probes.json','previous-ci.json','runtime-images.json']:shutil.copy2(work/name,ROOT/name)
shutil.copy2(work/'package-only/installed-check.log',ROOT/'installed-check.log')
shutil.copy2('build/linux/Testing/Temporary/LastTest.log',ROOT/'qt-tests.log')
shutil.copy2(work/'frozen-inputs.json',ROOT/'frozen-inputs.json')
shutil.copy2(work/'first-pass/frozen-inputs.json',ROOT/'first-pass-inputs.json')
shutil.copy2(work/'first-pass/full-check.log',ROOT/'first-pass.log')
qt=[int(x) for x in re.findall(r'Totals: (\d+) passed, 0 failed',(ROOT/'qt-tests.log').read_text())];assert len(qt)==2
comparison=json.loads((ROOT/'comparison/comparison.json').read_text())
write(ROOT/'verification-summary.json',{'qtChecks':sum(qt),'contractTests':93,'invalidStartupRefusals':25,'installedOffscreenModes':18,'virtualInstalledWindowPairs':144,'navigationVirtualPairs':8,'installedCatalogCaptures':83,'sourceInputs':len(frozen),'auditedPriorPairs':3522,'imagesAndMetadataUnchanged':sum(r['imageUnchanged'] and r['metadataUnchanged'] for r in rows),'changedPairs':sum(not(r['imageUnchanged'] and r['metadataUnchanged']) for r in rows),'nativeComparisons':len(comparison['results']),'nativeExactMatches':sum(r['status']=='passed' for r in comparison['results']),'nativeComponentBoundsMatches':sum(r.get('geometryStatus')=='passed' for r in comparison['results']),'nativeChildBoundsChecks':len(child_bounds),'nativeChildBoundsFailures':len(failures),'regressionSourceComparisons':len(audit),'geometryPassesLost':0,'exactPassesLost':0})
print(json.loads((ROOT/'verification-summary.json').read_text()))
