#!/usr/bin/env python3
"""Recompute the chart geometry correction and retain every open mirror gate."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tarfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/development/chart-geometry-20261017'
BASE=ROOT/'evidence/development/charts-20261017'
GATES=['nativeGeometryAndRaster','nativeSystemFonts','nativeFractionalFontLayout','nativeNonfiniteInputDeterminism','nativeInputTiming','intrinsicProposals','physicalDisplaysInput','readers','independentMachineReferenceReplay']
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
previous=module('chart_geometry_previous','verify-chart-candidate.py')
supplement=module('chart_geometry_supplement','capture-chart-geometry-cases.py')
inputs=previous.inputs
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_report(report):
    assert report['reference']==inputs.REFERENCE and report['baseRevision']=='4184245ca3cfad425c7e3b268a1b4ec159bd8e29'
    assert report['accepted'] is False and report['status']=='verification-pending'
    assert report['tolerance']=='none' and report['approvedExceptions']==[] and report['expectedImagesChanged'] is False
    assert report['remainingAcceptance']==GATES
    c,s=report['canonicalComparison'],report['supplementalComparison']
    assert c['cases']==c['stateMatches']==c['layoutMatches']==1744 and c['exactMatches']==c['pixelMatches']==40
    assert c['nativeFrameMatches']==c['nativeFrameObservations']==c['nativeMetricObservations']==1344 and c['nativeMetricMatches']==624
    assert s==dict(cases=125,exactMatches=0,pixelMatches=0,nativeFrameMatches=125,nativeMetricMatches=67,stateMatches=125)
    for key,value in dict(componentChecksDpr1=15,componentChecksDpr2=15,focusedCatalogTargets=2,isolatedCatalogInputs=170,invalidInputs=8,installedFiles=133,unchangedInstalledFiles=132,independentModes=33,catalogCaptures=135,legacyPngs=131,legacyMetadata=131,virtualProfiles=8,operatorControls=14,operatorClicks=24,operatorStates=25).items():assert report['validation'][key]==value,key
    assert report['validation']['physicalDisplay'] is False and report['validation']['hardwareAcceleration'] is False
    assert report['historicalFullQtSuite']['targets']==31 and report['historicalFullQtSuite']['currentModuleTestedByThatRun'] is False
    expected={**{f'charts-geometry-build-v{i}':1 if i==1 else 0 for i in range(1,6)},'charts-geometry-focused-v1':0,'charts-geometry-package-v1':0,'charts-geometry-package-v2':0,'charts-geometry-package-final-v1':0,'charts-geometry-supplement-v1':0,'charts-geometry-runtime-v1':0,'charts-geometry-operator-v1':0,'charts-geometry-comparison-v1':1,'charts-geometry-supplement-comparison-v1':1}
    assert {r['name']:r['exitCode'] for r in report['attempts']}==expected
def archive(directory,record):
    manifest=json.loads((directory/record['manifest']).read_text());result={}
    with tarfile.open(directory/record['archive']) as stream:
        members=stream.getmembers();assert len(members)==record['files']==len(manifest) and sum(m.size for m in members)<48*1024*1024
        assert {m.name for m in members}==set(manifest)
        for member in members:
            assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            value=stream.extractfile(member).read();row=manifest[member.name]
            assert len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256']
            result[member.name]=value
    return result
def verify(directory=DIRECTORY):
    directory=Path(directory);read=lambda n:json.loads((directory/n).read_text());report=read('candidate.json');validate_report(report)
    assert set(report['files'])=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name not in ['candidate.json','README.md']}
    for name,checksum in report['files'].items():assert digest(directory/name)==checksum,name
    for row in report['attempts']:assert read('attempts/'+row['name']+'/result.json')['exitCode']==row['exitCode']
    assert 'Totals: 15 passed, 0 failed' in (directory/'qt/run.log').read_text()
    assert 'Totals: 15 passed, 0 failed' in (directory/'qt/focused/run.log').read_text()
    assert '100% tests passed, 0 tests failed out of 2' in (directory/'qt/focused/run.log').read_text()
    assert [r['exitCode'] for r in read('package/steps.json')]==[0,0,1]
    assert read('supplement-proof/post-capture-dimension-kind-audit.json')['exitCode']==0
    supplement_inputs=read('supplement-proof/inputs.json')
    for path in (directory/'supplement-proof/driver').iterdir():assert digest(path)==supplement_inputs['driver/scripts/'+path.name]
    for record in read('package/strict-images.json').values():assert digest(directory/'captures'/record['identicalCapture'])==record['sha256']
    if (directory/'host/results.json').exists():
        host=read('host/results.json');assert len(host)==report['validation']['hostCommands'] and all(r['exitCode']==0 for r in host)
        assert report['validation']['hostContractTests']==596
    payload={}
    for record in report['archives'].values():
        part=archive(directory,record)
        for name,value in part.items():assert name not in payload;payload[name]=value
    base_report=json.loads((BASE/'candidate.json').read_text());installed=archive(BASE,base_report['archives']['installedPackage'])
    binding=read('package/artifact-binding.json');assert len(binding['installedFiles'])==133
    installed.update({n:v for n,v in payload.items() if n.startswith('install/') or n=='consumer-build/InstalledConsumer'})
    for name,checksum in binding['installedFiles'].items():assert hashlib.sha256(installed['install/'+name]).hexdigest()==checksum
    assert hashlib.sha256(installed['consumer-build/InstalledConsumer']).hexdigest()==binding['consumerSha256']
    old_binding=json.loads((BASE/'package/artifact-binding.json').read_text())
    assert binding['consumerSha256']==old_binding['consumerSha256'] and binding['consumerFiles']==old_binding['consumerFiles']
    assert [n for n,v in binding['installedFiles'].items() if old_binding['installedFiles'][n]!=v]==['lib/qml/Avelino/libAvelino.so']
    for snap in [read('package/inputs.json'),read('runtime-proof/inputs.json')['files']]:assert {n.removeprefix('install/'):v for n,v in snap.items() if n.startswith('install/')}==binding['installedFiles']
    replay=read('replay/source-overlays.json');base=read('replay/base-files.json');assert replay['baseRevision']==base['baseRevision']==report['baseRevision']
    assert set(replay['attempts'])=={f'charts-geometry-build-v{i}' for i in range(1,6)}
    for name,overlay in replay['attempts'].items():
        frozen=read('attempts/'+name+'/inputs.json')['sourceFiles']
        for path,checksum in frozen.items():
            if path in overlay:assert overlay[path]==checksum and hashlib.sha256(payload['blobs/'+checksum]).hexdigest()==checksum
            else:assert base['files'][path]['sha256']==checksum
    frozen=read('attempts/charts-geometry-build-v5/inputs.json')['sourceFiles']
    for name,checksum in binding['producerCriticalFiles'].items():assert frozen[name]==checksum
    for name,checksum in binding['consumerFiles'].items():assert base['files']['tests/consumer/'+name]['sha256']==checksum
    with subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE) as process:
        seen=set()
        for row in base['files'].values():
            if row['gitObject'] in seen:continue
            seen.add(row['gitObject']);process.stdin.write((row['gitObject']+'\n').encode());process.stdin.flush()
            header=process.stdout.readline().decode().split();assert header[:2]==[row['gitObject'],'blob']
            value=process.stdout.read(int(header[2]));assert process.stdout.read(1)==b'\n' and hashlib.sha256(value).hexdigest()==row['sha256']
        process.stdin.close()
    assert process.returncode==0
    for record in read('replay/diagnostic-outputs.json').values():
        location=record['location']
        value=(directory/location.removeprefix('candidate/')).read_bytes() if location.startswith('candidate/') else payload[location]
        assert hashlib.sha256(value).hexdigest()==record['sha256']
    canonical=read('comparison/comparison.json');assert canonical['status']=='failed' and canonical['summary']==report['canonicalComparison']
    rows={r['path']:r for r in inputs.rows()};assert len(canonical['results'])==len(rows)==1744
    assert {r['fixture'] for r in canonical['results']}==set(rows)
    for result in canonical['results']:
        expected=rows[result['fixture']];image=directory/'captures'/expected['path'];actual=read('captures/'+expected['path']+'.json')
        observation=inputs.observations(expected,actual)
        for key in ['layoutStatus','nativeFrameStatus','nativeMetricsStatus','stateStatus']:assert result[key]==observation[key]
        pixels=previous.pixel_metrics(ROOT/expected['reference'],image)
        assert result['pixelStatus']==('passed' if pixels['matches'] else 'failed')
        for key in ['changedPixels','maximumChannelError']:assert result[key]==pixels[key]
        assert result['status']==('passed' if pixels['matches'] and all(result[k]!='failed' for k in ['layoutStatus','nativeMetricsStatus','stateStatus']) else 'failed')
    results=canonical['results']
    assert canonical['summary']==dict(cases=len(results),exactMatches=sum(r['status']=='passed' for r in results),pixelMatches=sum(r['pixelStatus']=='passed' for r in results),layoutMatches=sum(r['layoutStatus']=='passed' for r in results),nativeFrameObservations=sum(r['nativeFrameStatus']!='unobserved' for r in results),nativeFrameMatches=sum(r['nativeFrameStatus']=='passed' for r in results),nativeMetricObservations=sum(r['nativeMetricsStatus']!='unobserved' for r in results),nativeMetricMatches=sum(r['nativeMetricsStatus']=='passed' for r in results),stateMatches=sum(r['stateStatus']=='passed' for r in results),byKind={kind:dict(cases=sum(r['kind']==kind for r in results),exactMatches=sum(r['kind']==kind and r['status']=='passed' for r in results)) for kind in ['closed','edge','history']})
    projected=json.loads(inputs.PROJECTION.read_text())
    for name in ['light','dark']:
        for scale in [1,1.5]:
            for dpr in [1,2]:previous.validate_profile(read('captures/'+inputs.prefix(name,scale,dpr)+'.json'),projected)
    supplemental=read('supplement-comparison/comparison.json');assert supplemental['status']=='failed' and supplemental['summary']==report['supplementalComparison']
    rows={r['path']:r for r in supplement.rows()};assert len(rows)==len(supplemental['results'])==125
    assert {r['fixture'] for r in supplemental['results']}==set(rows)
    for result in supplemental['results']:
        expected=rows[result['fixture']];actual=read('supplement/'+expected['path']+'.json');raw=actual['catalogMetadata'];image=directory/'supplement'/expected['path']
        assert actual['configuration']==expected['configuration'] and actual['state']==dict(appearances=1,disappearances=0,wrapperInstances=1)
        assert raw['width']==640 and raw['height']==400 and actual['metrics']['kind']==expected['configuration']['kind']
        pixels=previous.pixel_metrics(ROOT/expected['reference'],image)
        assert result['pixelStatus']==('passed' if pixels['matches'] else 'failed')
        for key in ['changedPixels','maximumChannelError']:assert result[key]==pixels[key]
        assert result['nativeFrameStatus']==('passed' if actual['frame']==expected['frame'] else 'failed')
        assert result['nativeMetricsStatus']==('passed' if inputs.subset(actual['metrics'],expected['metrics']) else 'failed')
        assert result['stateStatus']=='passed'
        assert result['status']==('passed' if all(result[k]=='passed' for k in ['pixelStatus','nativeFrameStatus','nativeMetricsStatus','stateStatus']) else 'failed')
        with Image.open(image) as png:assert png.size==(round(640*expected['dpr']),round(400*expected['dpr']))
    results=supplemental['results']
    assert supplemental['summary']==dict(cases=len(results),exactMatches=sum(r['status']=='passed' for r in results),pixelMatches=sum(r['pixelStatus']=='passed' for r in results),nativeFrameMatches=sum(r['nativeFrameStatus']=='passed' for r in results),nativeMetricMatches=sum(r['nativeMetricsStatus']=='passed' for r in results),stateMatches=sum(r['stateStatus']=='passed' for r in results))
    profiles=[p for p in (directory/'runtime').glob('*.json') if p.name!='environment.json'];assert len(profiles)==8
    for path in profiles:
        value=json.loads(path.read_text());previous.validate_profile(value,projected)
        assert value['platform'] in ['xcb','wayland'] and value['graphicsApi'] in [1,3] and value['physicalDisplay'] is False
        for history in value['histories']:
            prefix='runtime/'+path.stem+'-'+history['configuration']['id']+'-history-step'
            assert payload[prefix+'0.png']==payload[prefix+'7.png'] and payload[prefix+'0.png']!=payload[prefix+'1.png']
    regression=read('regression/catalogs.json');assert len(regression['records'])==131 and all(r['pixelsIdentical'] and r['metadataIdentical'] for r in regression['records'])
    for row in regression['records']:
        assert digest(directory/'catalogs'/row['path'])==digest(BASE/'catalogs'/row['path'])==row['currentSha256']
        assert digest(directory/'catalogs'/(row['path']+'.json'))==digest(BASE/'catalogs'/(row['path']+'.json'))==row['currentMetadataSha256']
    operator=read('operator/result.json');assert operator['exitCode']==0 and operator['controls']==14 and operator['clicks']==24 and len(operator['records'])==25
    for row in operator['records']:
        assert row['passed'] and row['attempts'][-1]['exactViewportMatch']
        with Image.open(directory/'operator'/row['attempts'][-1]['path']) as full,Image.open(directory/'operator'/row['reference']) as isolated:assert full.convert('RGBA').crop((24,200,664,600)).tobytes()==isolated.convert('RGBA').tobytes()
    print('Chart geometry: 1869 strict pairs, 691 native metric matches, eight virtual profiles and 25 operator states; native acceptance remains pending')
    return report
if __name__=='__main__':verify()
