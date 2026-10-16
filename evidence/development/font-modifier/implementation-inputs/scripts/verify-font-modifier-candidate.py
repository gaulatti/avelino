#!/usr/bin/env python3
"""Audit complete font candidate observations while preserving every failed comparison."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'evidence/development/font-modifier'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
inputs=load('font_candidate_inputs','capture-font-modifier-cases.py')
observations=load('font_candidate_observations','font-modifier-observations.py').observations

def verify(base=BASE):
 report=read(base/'candidate.json');assert report['accepted'] is False and report['status']=='verification-pending'
 assert report['referenceRevision']==inputs.REFERENCE
 files={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
 assert files==set(report['files'])|{'candidate.json'},'Missing or unsealed candidate evidence'
 for name,sha in report['files'].items():assert digest(base/name)==sha,name
 corpus=inputs.rows();indexed={r['path']:r for r in corpus};names=set(indexed)
 captures=read(base/'captures/capture-results.json');records=captures['records']
 assert len(records)==captures['cases']==1656 and captures['fixtures']==207 and captures['accepted'] is False
 assert captures['reference']==inputs.REFERENCE and {r['path'] for r in records}==names
 assert {p.name for p in (base/'captures').glob('*.png')}==names
 for row in records:
  assert digest(base/'captures'/row['path'])==row['sha256']
  assert digest(base/'captures'/(row['path']+'.json'))==row['metadataSha256']
  log=(base/'captures'/(row['path']+'.log')).read_text()
  assert not any(message in log for message in ['Unable to assign','QFont::','ReferenceError','TypeError']),row['path']
 for kind,(source,_) in inputs.CORPORA.items():
  assert captures['sourceInvestigations'][kind]==digest(ROOT/'evidence/reference-investigations'/f'{source}-20261016/investigation.json')
 installed=read(base/'installed-files.json')
 assert len(installed['files'])==installed['fileCount']==123
 assert captures['catalogSha256']==installed['files']['bin/AvelinoCatalog']
 comparison=read(base/'comparison/comparison.json');results=comparison['results']
 assert len(results)==1656 and {r['fixture'] for r in results}==names and comparison['accepted'] is False
 for result in results:
  row=indexed[result['fixture']];image=row['directory']/'captures'/row['source']['paths'][0]
  assert result['referenceRevision']==inputs.REFERENCE and result['referenceSHA256']==digest(image)
  assert result['candidateSHA256']==digest(base/'captures'/row['path'])
  measured=observations(row,read(base/'captures'/(row['path']+'.json')))
  for key,value in measured.items():assert result[key]==value,(row['path'],key)
  pixel_match=result['changedPixels']==0 and result['maximumChannelError']==0 and result['differenceBounds'] is None and result['alphaDifferenceBounds'] is None
  full_match=pixel_match and all(measured[k]=='passed' for k in ['partFramesStatus','baselineStatus','stateStatus'])
  assert result['status']==('passed' if full_match else 'failed')
 summary=dict(cases=1656,exactPixelAndGeometryMatches=sum(r['status']=='passed' for r in results),
  partFrameMatches=sum(r['partFramesStatus']=='passed' for r in results),baselineMatches=sum(r['baselineStatus']=='passed' for r in results),
  stateMatches=sum(r['stateStatus']=='passed' for r in results))
 assert summary==comparison['summary']==report['strictComparison']
 assert comparison['status']==('passed' if summary['exactPixelAndGeometryMatches']==1656 else 'failed')
 expected=set(itertools.product(['xcb','wayland'],['software','opengl'],['standard','scaled']));seen=set()
 for path in (base/'sessions').glob('font-modifier-*.json'):
  _,_,protocol,backend,configuration=path.stem.split('-');seen.add((protocol,backend,configuration));row=read(path)
  assert row['fixture']=='font-modifier' and row['qt']=='6.8.3' and row['accepted'] is False
  assert row['platform']==protocol and row['graphicsApi']==(1 if backend=='software' else 3)
  assert row['dpr']==(1 if configuration=='standard' else 2) and row['textScale']==(1 if configuration=='standard' else 1.5)
  assert row['appearance']==('light' if configuration=='standard' else 'dark') and row['physicalDisplay'] is False and row['hardwareAcceleration'] is False
  for key in ['fontModifierChecks','callerStateChecks','liveFontPaintChecks','focusChecks','qtAccessibilityChecks']:assert row[key]=='passed'
  assert row['closedContextCount']==len(row['closedContexts'])==207 and len(row['retainedUpdates'])==3
  expected_names={r['definition']['fixture'] for r in corpus if r['source']['appearance']==row['appearance'] and r['source']['textScale']==row['textScale'] and r['source']['dpr']==row['dpr']}
  assert {r['fixture'] for r in row['closedContexts']}==expected_names and len(expected_names)==207
  assert row['exactFrameSets']==sum(r['nativeFrameStatus']=='passed' for r in row['closedContexts'])
  assert row['exactBaselineSets']==sum(r['nativeBaselineStatus']=='passed' for r in row['closedContexts'])
  assert path.with_suffix('.captured').is_file()
  assert digest(path.with_suffix('.png'))==row['windowCaptureSha256']
  assert digest(path.with_name(path.stem+'-session.png'))==row['sessionCaptureSha256']
  log=path.with_suffix('.log').read_text()
  assert not any(message in log for message in ['Unable to assign','QFont::','ReferenceError','TypeError'])
  for observation in row['closedContexts']:
   native=next(r for r in corpus if r['definition']['fixture']==observation['fixture'] and r['source']['appearance']==row['appearance'] and r['source']['textScale']==row['textScale'] and r['source']['dpr']==row['dpr'])
   measured=observations(native,observation['observations'])
   assert measured['stateStatus']=='passed'
   assert observation['nativeFrameStatus']==measured['partFramesStatus'] and observation['nativeBaselineStatus']==measured['baselineStatus']
 assert seen==expected
 operator=read(base/'operator-ui/result.json')
 assert operator['status']=='passed' and operator['exitCode']==0 and operator['accepted'] is False
 assert operator['controls']==6 and operator['clicks']==8 and operator['phases']==len(operator['records'])==9
 assert operator['physicalDisplay'] is False and operator['sourceAndConsumerSourcesAbsent'] is True
 for phase in operator['records']:
  assert phase['passed'] is True and phase['viewport']==[24,202,640,400]
  assert phase['referenceSha256']==digest(base/'captures'/phase['reference'])
  assert phase['attempts'][-1]['exactViewportMatch'] is True
  for attempt in phase['attempts']:assert digest(base/'operator-ui'/attempt['path'])==attempt['sha256']
 package=read(base/'package-validation.json')
 assert package['requiredCheckExitCode']==0 and package['outerWrapperExitCode']==1 and package['artifactsOverwritten'] is False
 assert package['completedModes']==28 and package['catalogCaptures']==123 and package['priorAttemptPreserved'] is True
 regression=read(base/'prior-gallery-identity.json')
 assert regression['previousCaptures']==119 and regression['allPixelsIdentical'] and regression['allFullMetadataIdentical']
 assert len(regression['records'])==119 and all(r['pixelsIdentical'] and r['metadataIdentical'] for r in regression['records'])
 assert report['desktopInventory']==dict(registered=80,verificationPending=64,pending=16,accepted=0)
 assert report['televisionInventory']==dict(registered=46,pending=46,accepted=0)
 assert report['referencePinsChanged'] is False and report['expectedImagesChanged'] is False and report['tolerancesChanged'] is False and report['approvedExceptionsChanged'] is False
 print(f'Font candidate: {len(files)-1} sealed files, 1656 closed captures, eight virtual profiles; strict acceptance pending')
 return summary
if __name__=='__main__':verify()
