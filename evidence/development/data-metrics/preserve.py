import collections,hashlib,importlib.util,json,re,shutil
from pathlib import Path
ROOT=Path('evidence/development/data-metrics');work=Path('artifacts/data-metrics-implementation')
resumed=Path('artifacts/resumed-avelino-20261016')
assert not ROOT.exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
frozen=json.loads((work/'frozen-inputs.json').read_text());env=json.loads(Path('artifacts/linux/environment.json').read_text());assert env['sourceInputs']==frozen
for name,digest in frozen.items():assert sha(name)==digest,name
ROOT.mkdir();shutil.copy2('artifacts/linux/environment.json',ROOT/'build-environment.json')
folders={'desktop':'proposals','composition':'composition-proposals','selectors':'selector-proposals','checkbox':'checkbox-proposals','secure-field':'secure-field-proposals','search-field':'search-field-proposals','collection-filters':'collection-filters-proposals','slider':'slider-proposals','tabs':'tabs-proposals','pagination':'pagination-proposals','pagination-integers':'pagination-integer-proposals','accordion':'accordion-proposals','presentation-states':'presentation-state-proposals','alert':'alert-proposals','navigation':'navigation-proposals','sidebar-brand':'sidebar-brand-proposals','data-metrics':'data-metrics-proposals'}
previous=json.loads((work/'previous-captures.json').read_text());rows=[]
correctionReport=json.loads((resumed/'source-action-corrections.json').read_text())
corrections={(r['group'],r['path']):r for r in correctionReport['results']}
assert len(corrections)==12 and correctionReport['accepted'] is False and correctionReport['expectedSourceImagesChanged'] is False
for old in previous['pairs']:
 image,meta=Path(old['image']),Path(old['metadata']);assert sha(image)==old['sha256'] and sha(meta)==old['metadataSha256']
 current=Path('artifacts/linux')/folders.get(old['group'],'')/old['path'];currentmeta=current.with_name(current.name+'.json')
 sameImage=image.read_bytes()==current.read_bytes();sameMeta=meta.read_bytes()==currentmeta.read_bytes()
 value={**old,'imageUnchanged':sameImage,'metadataUnchanged':sameMeta}
 if not sameImage or not sameMeta:
  correction=corrections[(old['group'],old['path'])]
  assert sha(current)==correction['candidateImageSha256'] and sha(currentmeta)==correction['candidateMetadataSha256']
  assert correction['sourceActionRect']==correction['candidateActionRect'] and correction['sourceLabelBounds']==correction['candidateLabelBounds']
  destination=ROOT/'changed-captures'/old['group'];destination.mkdir(parents=True,exist_ok=True)
  shutil.copy2(current,destination/current.name);shutil.copy2(currentmeta,destination/currentmeta.name)
  correction['candidateImage']=str(destination/current.name);correction['candidateMetadata']=str(destination/currentmeta.name)
  value['sourceCorrectionEvidence']=str(ROOT/'source-action-corrections.json')
 rows.append(value)
assert len(rows)==4338
assert sum(not r['imageUnchanged'] for r in rows)==4 and sum(not r['metadataUnchanged'] for r in rows)==12
write(ROOT/'regressions.json',{'previousCandidate':previous['revision'],'auditedPairs':len(rows),'imagesAndMetadataUnchanged':4326,'imagesUnchanged':4334,'metadataUnchanged':4326,'changedPairs':12,'strictPriorCandidateEquality':'failed; 12 source-measured corrections retained','sourceCorrectionEvidence':'source-action-corrections.json','groups':dict(collections.Counter(r['group'] for r in rows)),'results':rows})
write(ROOT/'source-action-corrections.json',correctionReport)
for name in ['native-action-text.json','action-text-provenance.json']:
 shutil.copy2(resumed/name,ROOT/name)
for group,folder in folders.items():
 dest=ROOT/'regression-inputs'/group;dest.mkdir(parents=True)
 for name in ['environment.json','capture-results.json']:shutil.copy2(Path('artifacts/linux')/folder/name,dest/name)
 assert json.loads((dest/'environment.json').read_text())['sourceInputs']==frozen
 result=json.loads((dest/'capture-results.json').read_text());assert result['status']=='captured' and all(r['exitCode']==0 and not r['runtimeErrors'] for r in result['results'])
shutil.copytree('artifacts/linux/data-metrics-proposals',ROOT/'captures')
spec=importlib.util.spec_from_file_location('compare','scripts/compare-captures.py');compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)
compare.compare(Path('evidence/reference-proposals/data-metrics-20261015'),ROOT/'captures',ROOT/'comparison')
child=[]
for case in json.loads(Path('evidence/reference-proposals/data-metrics-20261015/captures.json').read_text())['captures']:
 if case['api'] in ['BleeckerButton','BleeckerIconBadge']:continue
 labels={r['role']:r for r in json.loads((ROOT/'captures'/(case['path']+'.json')).read_text())['labels']}
 mapping={'bleeckerKbdKey':'key'} if case['api']=='BleeckerKbd' else {'bleeckerMetricLabel':'label','bleeckerMetricValue':'value'}
 if case['api']=='BleeckerStatCard' and case['delta'] is not None:mapping['bleeckerStatCardDelta']='delta'
 for role,key in mapping.items():
  expected=case['layoutWitnessRects'][key];measured=labels[role]
  delta={axis:measured[axis]-expected[axis] for axis in ['width','height']}
  child.append({'fixture':case['path'],'role':role,'source':{axis:expected[axis] for axis in delta},'candidate':{axis:measured[axis] for axis in delta},'delta':delta,'status':'passed' if all(abs(v)<=1e-6 for v in delta.values()) else 'failed; unaccepted'})
write(ROOT/'native-child-bounds.json',{'method':'actual Qt title/value/key/delta metadata against independently identical native layout witnesses; width/height only','accepted':False,'results':child,'knownUnacceptedFailures':[r for r in child if r['status']!='passed']})
gallery=ROOT/'catalog';gallery.mkdir();shutil.copy2('artifacts/linux/environment.json',gallery/'environment.json')
for p in Path('artifacts/linux').glob('data-metrics-*.png*'):shutil.copy2(p,gallery/p.name)
assert len(list(gallery.glob('*.png')))==4
shutil.copytree(work/'host-styles',ROOT/'host-styles')
for appearance in ['light','dark']:
 for style in ['Basic','Fusion']:assert (ROOT/f'host-styles/{style}-{appearance}.png').read_bytes()==(gallery/f'data-metrics-{appearance}-dpr2.png').read_bytes()
shutil.copytree(resumed/'package-only/sessions',ROOT/'sessions',ignore=shutil.ignore_patterns('*.captured'))
assert json.loads((ROOT/'sessions/environment.json').read_text())['sourceInputs']==frozen
sessions=[json.loads(p.read_text()) for p in (ROOT/'sessions').glob('*.json') if p.name!='environment.json'];assert len(sessions)==160
own=[s for s in sessions if s['fixture']=='data-metrics'];assert len(own)==8 and all(s['dataMetricsChecks']=='passed' and s['updates']==1 and s['formattedValue']=='12.345679%' for s in own)
shutil.copytree(resumed/'package-only/catalog',ROOT/'installed-catalog');shutil.copy2('artifacts/linux/environment.json',ROOT/'installed-catalog/environment.json');assert len(json.loads((ROOT/'installed-catalog/catalog-results.json').read_text())['captures'])==91
for name in ['full-check.log','host-styles.log','package-only.log','references.log','discovery.log','tokens.log','source-verification.log','feature-path-audit.json','visual-qa.json','previous-ci.json','runtime-images.json','frozen-inputs.json','acceptance.md']:
 shutil.copy2(work/name,ROOT/('interrupted-full-check.log' if name=='full-check.log' else name))
for name in ['resume-captures.sh','capture-audit.log','verification.json','visual-qa.json']:
 shutil.copy2(resumed/name,ROOT/('resumed-'+name))
for name in ['format-diagnostics.log','mode-conflict.log','display-check.log']:
 shutil.copy2(resumed/'package-only'/name,ROOT/('resumed-'+name))
shutil.copy2(work/'contracts3.log',ROOT/'contracts.log')
shutil.copy2(work/'proposals2.log',ROOT/'proposals.log')
shutil.copy2(work/'input-verification.log',ROOT/'input-verification.log')
for name in ['component-check.log','component-check2.log','component-check3.log','all-component-check.log','all-component-check2.log','final-component-prototype.log','consumer-check.log','build.log','toolchain-build.log','native-inputs-build.log','native-inputs.log','input-replay.log','native-text-build.log','native-text-build2.log','native-text.log','native-text2.log','text-replay.log','measure.log','contracts.log','adapter-contracts.log','adapter-contracts2.log','capture-failure-contract.log','mesa-repro.log','empty-rtl-repro.log']:
 if (work/name).exists():shutil.copy2(work/name,ROOT/('investigation-'+name))
shutil.copy2('artifacts/linux/number-formatting.json',ROOT/'number-formatting.json')
shutil.copy2(resumed/'package-only/number-formatting.json',ROOT/'installed-number-formatting.json')
assert (ROOT/'installed-number-formatting.json').read_bytes()==(ROOT/'number-formatting.json').read_bytes()
formatting=json.loads((ROOT/'number-formatting.json').read_text());assert formatting['cases']==1330 and formatting['matches']==1302 and formatting['mismatches']==28
shutil.copy2(resumed/'package-only/installed-check.log',ROOT/'installed-check.log')
shutil.copy2(work/'second-pass/frozen-inputs.json',ROOT/'second-pass-inputs.json')
shutil.copy2(work/'second-pass/full-check.log',ROOT/'second-pass.log')
shutil.copy2(work/'second-pass/package-only.log',ROOT/'second-pass-package-only.log')
shutil.copytree(work/'mesa-repro/sessions',ROOT/'mesa-layout-investigation',ignore=shutil.ignore_patterns('*.captured'))
shutil.copy2(work/'mesa-repro-command.sh',ROOT/'mesa-repro-command.sh')
shutil.copytree(work/'empty-rtl-repro',ROOT/'empty-rtl-isolated-replay')
shutil.copy2(work/'first-pass/frozen-inputs.json',ROOT/'first-pass-inputs.json')
shutil.copy2(work/'first-pass/full-check.log',ROOT/'first-pass.log')
shutil.copy2(work/'first-pass/package-only.log',ROOT/'first-pass-package-only.log')
shutil.copy2(work/'first-pass/package/consumer/DataMetrics.qml',ROOT/'first-pass-DataMetrics.qml')
for name in ['data-metrics-wayland-software-scaled.json','data-metrics-wayland-software-scaled.png','data-metrics-wayland-software-scaled-session.png']:
 shutil.copy2(work/'first-pass/package-only/sessions'/name,ROOT/('first-pass-'+name))
shutil.copy2(resumed/'qt-tests.log',ROOT/'qt-tests.log')
qt=[int(x) for x in re.findall(r'Totals: (\d+) passed, 0 failed',(ROOT/'qt-tests.log').read_text())];assert len(qt)==2
comparison=json.loads((ROOT/'comparison/comparison.json').read_text())
write(ROOT/'verification-summary.json',{'qtChecks':sum(qt),'contractTests':107,'invalidStartupRefusals':37,'installedOffscreenModes':20,'virtualInstalledWindowPairs':160,'dataMetricsVirtualPairs':8,'installedCatalogCaptures':91,'sourceInputs':len(frozen),'auditedPriorPairs':4338,'imagesAndMetadataUnchanged':4326,'changedPairs':12,'sourceMeasuredActionCorrections':12,'nativeActionTextProbes':128,'nativeComparisons':len(comparison['results']),'nativeExactMatches':sum(r['status']=='passed' for r in comparison['results']),'nativeComponentBoundsMatches':sum(r.get('geometryStatus')=='passed' for r in comparison['results']),'nativeChildBoundsChecks':len(child),'nativeChildBoundsFailures':sum(r['status']!='passed' for r in child),'nativeFormatterCases':1330,'nativeFormatterMatches':1302,'nativeFormatterFailures':28})
print(json.loads((ROOT/'verification-summary.json').read_text()))
