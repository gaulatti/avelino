import collections,hashlib,importlib.util,json,shutil,tempfile
from pathlib import Path
root=Path('evidence/development/text-wrapping');assert not root.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,j:p.write_text(json.dumps(j,indent=2)+'\n')
env=json.load(open('artifacts/linux/environment.json'))
for p,h in env['sourceInputs'].items():assert sha(Path(p))==h,p
root.mkdir();shutil.copy2('artifacts/linux/environment.json',root/'build-environment.json')
groups={
 'desktop':('proposals','desktop-20261012'),'composition':('composition-proposals','composition-20261012-v1'),
 'selectors':('selector-proposals','selectors-20261013'),'checkbox':('checkbox-proposals','checkbox-20261013'),
 'secure-field':('secure-field-proposals','secure-field-20261014'),'search-field':('search-field-proposals','search-field-20261014'),
 'collection-filters':('collection-filters-proposals','collection-filters-20261014'),'slider':('slider-proposals','slider-20261014-v2'),
 'tabs':('tabs-proposals','tabs-20261014'),'pagination':('pagination-proposals','pagination-20261014'),
 'pagination-integers':('pagination-integer-proposals','pagination-integers-20261014'),'buttons':('.','buttons')}
# Reuse prior diagnostic values only after both newly captured files are byte-identical.
# Every changed pair gets a fresh strict comparison and preserved raw diagnostics.
prior=json.load(open('evidence/development/pagination-integers/regressions.json'))['results']
for old in sorted(Path('evidence/development/pagination-integers/captures').glob('*.png')):
 prior.append({'group':'pagination-integers-captures','path':old.name,'previousImage':str(old),'previousMetadata':str(old.with_name(old.name+'.json')),'sha256':sha(old),'metadataSha256':sha(old.with_name(old.name+'.json'))})
for old in sorted(Path('evidence/development/pagination-integers/catalog').glob('*.png')):
 prior.append({'group':'pagination-integers-catalog','path':old.name,'previousImage':str(old),'previousMetadata':str(old.with_name(old.name+'.json')),'sha256':sha(old),'metadataSha256':sha(old.with_name(old.name+'.json'))})
assert len(prior)==2782
spec=importlib.util.spec_from_file_location('comparison','scripts/compare-captures.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
by_group=collections.defaultdict(list);regressions=[]
for r in prior:
 old=Path(r['previousImage']);oldmeta=Path(r['previousMetadata']);assert sha(old)==r['sha256'] and sha(oldmeta)==r['metadataSha256']
 group=r['group'].removesuffix('-captures');is_catalog=group=='catalog' or group.endswith('-catalog')
 if is_catalog:group='catalog'
 current=Path('artifacts/linux')/('.' if group=='catalog' else groups[group][0])/r['path'];meta=current.with_name(current.name+'.json')
 image_same=old.read_bytes()==current.read_bytes();metadata_same=oldmeta.read_bytes()==meta.read_bytes()
 changed=not (image_same and metadata_same)
 if changed:
  dst=root/group/'captures';dst.mkdir(parents=True,exist_ok=True);shutil.copy2(current,dst/current.name);shutil.copy2(meta,dst/meta.name)
  stderr=current.with_name(current.name+'.stderr.txt')
  if stderr.exists():shutil.copy2(stderr,dst/stderr.name)
  retained=dst/current.name;retained_meta=dst/meta.name
 else:retained,retained_meta=old,oldmeta
 row={'group':group,'path':current.name,'previousImage':str(old),'previousMetadata':str(oldmeta),'currentImage':str(retained),'currentMetadata':str(retained_meta),'previousSha256':sha(old),'previousMetadataSha256':sha(oldmeta),'sha256':sha(current),'metadataSha256':sha(meta),'imageByteIdentical':image_same,'metadataByteIdentical':metadata_same,'status':'changed; fresh strict diagnostics required' if changed and not is_catalog else 'changed gallery; no source baseline' if changed else 'new capture PNG and complete metadata are byte-identical to preserved pair'}
 regressions.append(row);by_group[group].append(row)
write(root/'regressions.json',{'previousCandidate':'bcf8d4bcc476aa06cec79300bc5325b97df74ee8','pairs':2782,'imagesUnchanged':sum(r['imageByteIdentical'] for r in regressions),'metadataUnchanged':sum(r['metadataByteIdentical'] for r in regressions),'unchangedPairs':sum(r['imageByteIdentical'] and r['metadataByteIdentical'] for r in regressions),'results':regressions})
report_cache={};summaries={};audit={}
for group,(folder,refname) in groups.items():
 reference=Path('reference/captures/desktop/buttons') if group=='buttons' else Path('evidence/reference-proposals')/refname
 manifest=json.load(open(reference/'captures.json'));fixtures={r['path']:r for r in manifest['captures']};rows=by_group[group];assert set(fixtures)>=set(r['path'] for r in rows)
 before_stats={};missing_reports={}
 for row in rows:
  before_path=Path(row['previousImage']).parent.parent/'comparison/comparison.json'
  if before_path.is_file():
   if before_path not in report_cache:report_cache[before_path]={r['fixture']:r for r in json.load(open(before_path))['results']}
   old=report_cache[before_path].get(row['path'])
   if old and 'error' not in old and old['candidateSHA256']==row['previousSha256']:
    before_stats[row['path']]=(old,before_path)
  if row['path'] not in before_stats:missing_reports[row['path']]=str(before_path)
 changed=[r for r in rows if not(r['imageByteIdentical'] and r['metadataByteIdentical']) or r['path'] in missing_reports]
 target=root/group;target.mkdir(exist_ok=True)
 if group!='buttons':
  for name in ['environment.json','capture-results.json']:shutil.copy2(Path('artifacts/linux')/folder/name,target/name)
  assert json.load(open(target/'environment.json'))['sourceInputs']==env['sourceInputs']
 result={}
 if changed:
  captures=target/'captures';captures.mkdir(exist_ok=True)
  for row in changed:
   source=Path('artifacts/linux')/folder/row['path']
   for suffix in ['', '.json', '.stderr.txt']:
    p=source.with_name(source.name+suffix)
    if p.is_file():shutil.copy2(p,captures/p.name)
  with tempfile.TemporaryDirectory(prefix='avelino-strict-subset-') as temp:
   projection=Path(temp);write(projection/'captures.json',{**manifest,'captures':[fixtures[r['path']] for r in changed]})
   if (reference/'proposal.json').exists():shutil.copy2(reference/'proposal.json',projection/'proposal.json')
   for r in changed:(projection/r['path']).symlink_to((reference/r['path']).resolve())
   compare.compare(projection,target/'captures',target/'comparison')
  new=json.load(open(target/'comparison/comparison.json'))
  for r in new['results']:
   r['reference']=str(reference/r['fixture']);r['comparisonMethod']='fresh strict comparison; complete source fixture fields and original image bytes'
   assert 'error' not in r,(group,r);result[r['fixture']]=r
 changes=[];bodies=[]
 for row in rows:
  name=row['path']
  if name in before_stats:
   old,before_path=before_stats[name]
  else:
   assert row['imageByteIdentical'] and row['metadataByteIdentical'],(group,name,'missing before comparison for changed bytes')
   old=dict(result[name]);before_path=None
   result[name]['historicalComparisonGap']=missing_reports[name]
   result[name]['beforeStatisticsMethod']='fresh strict comparison also proves preceding candidate because PNG and complete metadata are byte-identical'
  assert old['candidateSHA256']==row['previousSha256'];assert old['referenceSHA256']==sha(reference/name),name
  if name not in result:
   assert row['imageByteIdentical'] and row['metadataByteIdentical']
   r={**old,'candidate':row['currentImage'],'reference':str(reference/name),'comparisonMethod':'prior strict pixel/geometry result reused after fresh PNG/full metadata byte identity','previousComparison':str(before_path),'previousComparisonSha256':sha(before_path)}
   result[name]=r
  r=result[name];assert r['candidateSHA256']==row['sha256'];assert r['referenceSHA256']==fixtures[name]['sha256']
  changes.append({'fixture':name,'api':fixtures[name].get('api','BleeckerButton'),'geometryBefore':old.get('geometryStatus'),'geometryAfter':r.get('geometryStatus'),'exactBefore':old['status'],'exactAfter':r['status'],'changedPixelsBefore':old['changedPixels'],'changedPixelsAfter':r['changedPixels'],'changedPixelDelta':r['changedPixels']-old['changedPixels']})
  if fixtures[name].get('api')=='BleeckerPagination' and 'bodySize' in fixtures[name]:
   m=json.load(open(row['currentMetadata']));oldm=json.load(open(row['previousMetadata']));bodies.append({'fixture':name,'reference':fixtures[name]['bodySize'],'before':oldm['bodySize'],'after':m['bodySize'],'beforeMatches':oldm['bodySize']==fixtures[name]['bodySize'],'afterMatches':m['bodySize']==fixtures[name]['bodySize']})
 ordered=[result[r['path']] for r in rows]
 if changed:
  new['originalSourceManifestSha256']=sha(reference/'captures.json')
  write(target/'comparison/comparison.json',new)
 write(target/'comparison.json',{'status':'passed' if all(r['status']=='passed' for r in ordered) else 'failed','acceptance':'strict diagnostic only; no baseline or exception approval','originalReference':str(reference),'sourceManifestSha256':sha(reference/'captures.json'),'freshComparisons':len(changed),'historicalComparisonGapsRechecked':len(missing_reports),'byteIdenticalPriorComparisons':len(rows)-len(changed),'results':ordered})
 audit[group]={'captures':len(rows),'freshComparisons':len(changed),'historicalComparisonGapsRechecked':len(missing_reports),'geometryGained':sum(c['geometryBefore']!='passed' and c['geometryAfter']=='passed' for c in changes),'geometryLost':sum(c['geometryBefore']=='passed' and c['geometryAfter']!='passed' for c in changes),'exactGained':sum(c['exactBefore']!='passed' and c['exactAfter']=='passed' for c in changes),'exactLost':sum(c['exactBefore']=='passed' and c['exactAfter']!='passed' for c in changes),'fewerChangedPixels':sum(c['changedPixelDelta']<0 for c in changes),'moreChangedPixels':sum(c['changedPixelDelta']>0 for c in changes),'unchangedPixelCount':sum(c['changedPixelDelta']==0 for c in changes),'bodyGeometryGained':sum(not c['beforeMatches'] and c['afterMatches'] for c in bodies),'bodyGeometryLost':sum(c['beforeMatches'] and not c['afterMatches'] for c in bodies),'bodyGeometryMatches':sum(c['afterMatches'] for c in bodies),'cases':changes,'bodies':bodies}
 summaries[group]={'captures':len(rows),'rootGeometryMatches':sum(r.get('geometryStatus')=='passed' for r in ordered),'exactMatches':sum(r['status']=='passed' for r in ordered),'bodyGeometryMatches':sum(c['afterMatches'] for c in bodies)}
write(root/'before-after.json',audit);write(root/'comparison-summary.json',summaries)
assert not any(a['geometryLost'] or a['exactLost'] or a['bodyGeometryLost'] for a in audit.values()),'A preceding geometry/exact pass regressed; inspect raw evidence'
print('Audit:',json.dumps({g:{k:v for k,v in a.items() if k not in ['cases','bodies']} for g,a in audit.items()},indent=2))
print('Pair retention:',collections.Counter((r['imageByteIdentical'],r['metadataByteIdentical']) for r in regressions))
