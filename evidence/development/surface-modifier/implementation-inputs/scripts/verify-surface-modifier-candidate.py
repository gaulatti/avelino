#!/usr/bin/env python3
"""Verify complete surface evidence without accepting native mirror parity."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/development/surface-modifier'
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
inputs=load('surface_candidate_inputs','capture-surface-modifier-cases.py')
observe=load('surface_candidate_observations','surface-modifier-observations.py').observations
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify(directory=DIRECTORY):
 from PIL import Image,ImageChops
 directory=Path(directory);read=lambda name:json.loads((directory/name).read_text())
 report=read('candidate.json')
 assert report['accepted'] is False and report['status']=='verification-pending'
 assert report['reference']==inputs.REFERENCE and report['closedFixtures']==52
 assert report['baselineAcceptance']=='pending; no native first-baseline contexts captured'
 assert report['remainingAcceptance']==['nativeRasterShadow','systemFontsAndButton','nativeFirstBaseline','nativeHitTesting','physicalDisplaysInput','readers']
 assert set(report['files'])=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name not in ['candidate.json','README.md']}
 for name,checksum in report['files'].items():
  path=Path(name);assert not path.is_absolute() and '..' not in path.parts
  assert digest(directory/path)==checksum,name
 for name,checksum in report['implementationFiles'].items():assert digest(directory/'implementation-inputs'/name)==checksum,name
 corpus=inputs.rows();results=read('comparison/comparison.json');capture=read('captures/capture-results.json')
 assert capture['accepted'] is False and capture['fixtures']==52 and capture['cases']==416
 assert results['accepted'] is False and len(results['results'])==416
 byname={r['fixture']:r for r in results['results']};records={r['path']:r for r in capture['records']}
 assert len(byname)==len(records)==416 and set(byname)==set(records)=={r['path'] for r in corpus}
 exact=frames=states=0
 for row in corpus:
  name=row['path'];r=byname[name];p=directory/'captures'/name;meta=read('captures/'+name+'.json')
  assert records[name]['sha256']==r['candidateSHA256']==digest(p)
  assert records[name]['metadataSha256']==digest(directory/'captures'/ (name+'.json'))
  reference=row['directory']/'captures'/row['source']['paths'][0]
  assert r['referenceSHA256']==digest(reference) and r['referenceRevision']==inputs.REFERENCE
  assert r['tolerance']=='none; glyph-edge policy has not been calibrated or approved'
  inputs.verify_capture_log((directory/'captures'/(name+'.log')).read_text())
  assert meta['asyncShapeFrameChecks']=='passed'
  measurement=observe(row,meta)
  for key,value in measurement.items():assert r[key]==value,(name,key)
  expected=Image.open(reference).convert('RGBA');actual=Image.open(p).convert('RGBA');assert expected.size==actual.size
  difference=ImageChops.difference(expected,actual);channels=difference.split();maximum=channels[0]
  for channel in channels[1:]:maximum=ImageChops.lighter(maximum,channel)
  histogram=maximum.histogram();changed=expected.width*expected.height-histogram[0]
  assert r['changedPixels']==changed and r['maximumChannelError']==max(i for i,n in enumerate(histogram) if n),name
  matched=changed==0 and measurement['partFramesStatus']=='passed' and measurement['stateStatus']=='passed'
  assert r['status']==('passed' if matched else 'failed'),name
  assert measurement['baselineStatus']=='not-requested'
  exact+=matched;frames+=measurement['partFramesStatus']=='passed';states+=measurement['stateStatus']=='passed'
 summary=dict(cases=416,exactPixelAndGeometryMatches=exact,partFrameMatches=frames,requestedBaselineContexts=0,baselineMismatches=0,stateMatches=states)
 assert results['summary']==report['strictComparison']==summary
 assert results['status']==('passed' if exact==416 else 'failed')
 assert report['validation']['fullQtTargets']==27 and report['validation']['finalFocusedTargets']==2
 assert report['validation']['independentModes']==29 and report['validation']['catalogCaptures']==127
 assert report['validation']['priorGalleryPngsAndMetadataUnchanged']==123
 assert report['validation']['publishedModuleFilesUnchanged']==96
 runtime=list((directory/'runtime').glob('*.json'));assert len(runtime)==16
 surface=[p for p in runtime if p.name.startswith('surface-modifier-')];assert len(surface)==8
 for p in surface:
  r=json.loads(p.read_text());assert r['accepted'] is False and r['closedContextCount']==52 and len(r['closedContexts'])==52
  assert r['requestedBaselineContexts']==0 and r['exactFrameSets']==frames//8
  assert len(r['retainedHistories'])==5 and all(len(h['steps'])==6 and h['restoredPixelsIdentical'] for h in r['retainedHistories'])
  for key in ['surfaceModifierChecks','callerStateChecks','focusChecks','qtAccessibilityChecks','liveRadiusPaintChecks','asyncShapeFrameChecks']:assert r[key]=='passed'
 operator=read('operator-ui/result.json')
 assert operator['status']=='passed' and operator['accepted'] is False and operator['exitCode']==0
 assert (operator['controls'],operator['clicks'],operator['phases'])==(10,10,11)
 assert operator['sourceAndConsumerSourcesAbsent'] and operator['producerBuildAbsent']
 assert all(r['passed'] and r['attempts'][-1]['exactViewportMatch'] for r in operator['records'])
 for record in operator['records']:
  expected=Image.open(directory/'operator-ui/references'/record['reference']).convert('RGBA')
  for attempt in record['attempts']:
   path=directory/'operator-ui'/attempt['path'];assert digest(path)==attempt['sha256']
   x,y,w,h=record['viewport'];actual=Image.open(path).convert('RGBA').crop((x,y,x+w,y+h))
   assert (expected.tobytes()==actual.tobytes())==attempt['exactViewportMatch']
 for archive in report['archives'].values():
  manifest=read(archive['manifest'])
  with tarfile.open(directory/archive['archive']) as stream:
   members=stream.getmembers();assert all(m.isfile() for m in members)
   assert len(members)==len(manifest)==archive['files'] and {m.name for m in members}==set(manifest)
   for member in members:
    data=stream.extractfile(member).read();assert len(data)==manifest[member.name]['bytes'] and hashlib.sha256(data).hexdigest()==manifest[member.name]['sha256']
 return summary
if __name__=='__main__':print(json.dumps(verify(),indent=2))
