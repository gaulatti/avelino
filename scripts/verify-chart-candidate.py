#!/usr/bin/env python3
"""Recompute sealed Linux chart evidence without accepting native differences."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tarfile
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/development/charts-20261017'
GATES=['nativeGeometryAndRaster','nativeSystemFonts','nativeNonfiniteInputDeterminism','nativeInputTiming','physicalDisplaysInput','readers','independentMachineReferenceReplay']
spec=importlib.util.spec_from_file_location('chart_candidate_inputs',ROOT/'scripts/capture-charts.py')
inputs=importlib.util.module_from_spec(spec);spec.loader.exec_module(inputs)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_report(report):
    assert report['reference']==inputs.REFERENCE and report['accepted'] is False and report['status']=='verification-pending'
    assert report['tolerance']=='none' and report['approvedExceptions']==[] and report['expectedImagesChanged'] is False
    assert report['remainingAcceptance']==GATES and report['strictComparisonStatus']=='failed'
    summary=report['strictComparison'];assert summary['cases']==summary['stateMatches']==summary['layoutMatches']==1744
    assert summary['nativeFrameObservations']==summary['nativeFrameMatches']==summary['nativeMetricObservations']==1344
    assert 0<=summary['exactMatches']<=summary['pixelMatches']<1744
    assert 0<=summary['nativeMetricMatches']<1344
    assert {k:r['cases'] for k,r in summary['byKind'].items()}==dict(closed=960,edge=400,history=384)
    for key,value in dict(fullQtTargets=31,independentModes=33,catalogCaptures=135,legacyPngs=131,legacyMetadata=131,installedFiles=133,virtualProfiles=40,chartVirtualProfiles=8,operatorControls=14,operatorClicks=24,operatorStates=25,strictDefaultExitCode=1,strictImageExitCode=1).items():assert report['validation'][key]==value,key
    assert report['validation']['physicalDisplay'] is False and report['validation']['hardwareAcceleration'] is False
    expected={**{f'charts-build-v{i}':0 for i in range(1,6)},**{f'charts-package-v{i}':0 for i in range(1,4)},'charts-package-final-v1':0,'charts-full-v1':0,'charts-runtime-v1':0,'charts-operator-v1':0,'charts-comparison-v1':1}
    assert {r['name']:r['exitCode'] for r in report['attempts']}==expected
def validate_profile(actual,projection):
    assert actual['reference']==inputs.REFERENCE and actual['accepted'] is False and actual['structuralChecks']=='passed'
    assert actual['nativeGeometryComparisonStatus']=='failed' and actual['images']==218 and actual['geometryObservations']==168
    assert actual['nativeRasterAcceptance']==actual['physicalInputAcceptance']==actual['readerAcceptance']=='pending'
    assert actual['inputContexts']==10 and actual['qtAccessibilityChecks'].startswith('passed') and actual['inputChecks'].startswith('passed')
    assert actual['qt']=='6.8.3' and actual['platform'] in ['offscreen','xcb','wayland'] and actual['graphicsApi'] in [1,3]
    assert actual['width']==640 and actual['height']==400
    context=(actual['appearance'],actual['textScale'],actual['dpr'])
    selected=lambda rows:[r for r in rows if (r['appearance'],r['textScale'],r['dpr'])==context]
    closed={r['configuration']['id']:r for r in selected(projection['closed'])}
    edges={r['configuration']['id']:r for r in selected(projection['edges'])}
    histories={r['configuration']['id']:r for r in selected(projection['histories'])}
    assert len(actual['closed'])==len(closed)==120 and len(actual['edges'])==len(edges)==50 and len(actual['histories'])==len(histories)==6
    frames=metrics=0
    def observe(value,expected):
        nonlocal frames,metrics
        assert value['state']==dict(appearances=1,disappearances=0,wrapperInstances=1)
        assert value['configuration']==expected['configuration']
        same_frame=value['frame']==expected['frame'];same_metrics=inputs.subset(value['metrics'],expected['metrics'])
        assert value['nativeFrameMatches'] is same_frame and value['nativeMetricsMatch'] is same_metrics
        frames+=same_frame;metrics+=same_metrics
    assert {r['configuration']['id'] for r in actual['closed']}==set(closed)
    for row in actual['closed']:observe(row,closed[row['configuration']['id']])
    assert {r['configuration']['id'] for r in actual['edges']}==set(edges)
    for row in actual['edges']:
        native=edges[row['configuration']['id']]
        for key in ['configuration','specification','reference','nativeNonfiniteDeterminism']:assert row[key]==native[key]
        assert row['state']==dict(appearances=1,disappearances=0,wrapperInstances=1)
    assert {r['configuration']['id'] for r in actual['histories']}==set(histories)
    for history in actual['histories']:
        native=histories[history['configuration']['id']];assert len(history['steps'])==len(native['steps'])==8
        for value,expected in zip(history['steps'],native['steps']):
            for key in ['step','configuration','appearance','textScale','reference']:assert value[key]==expected[key],key
            observe(value,expected)
        assert history['steps'][-1]['restoredInitialPixelsAndGeometry'] is True
        for key in ['frame','metrics']:assert history['steps'][0][key]==history['steps'][-1][key]
    assert actual['frameMatches']==frames and actual['metricMatches']==metrics
def pixel_metrics(reference,candidate):
    with Image.open(reference) as a,Image.open(candidate) as b:
        assert a.size==b.size and 'icc_profile' not in a.info and 'icc_profile' not in b.info
        rgb=ImageChops.difference(a.convert('RGB'),b.convert('RGB'));alpha=ImageChops.difference(a.convert('RGBA').getchannel('A'),b.convert('RGBA').getchannel('A'))
        r,g,blue=rgb.split();maximum=ImageChops.lighter(ImageChops.lighter(r,g),blue)
        return dict(matches=rgb.getbbox() is None and alpha.getbbox() is None,changedPixels=rgb.width*rgb.height-maximum.histogram()[0],maximumChannelError=maximum.getextrema()[1])
def verify(directory=DIRECTORY):
    directory=Path(directory);read=lambda name:json.loads((directory/name).read_text());report=read('candidate.json');validate_report(report)
    assert set(report['files'])=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name not in ['candidate.json','README.md']}
    for name,checksum in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory/name)==checksum,name
    archived={};implementation={};blobs={};diagnostics={}
    for key,record in report['archives'].items():
        manifest=read(record['manifest'])
        with tarfile.open(directory/record['archive']) as stream:
            members=stream.getmembers();assert len(members)==len(manifest)==record['files']
            assert sum(m.size for m in members)<48*1024*1024
            assert {m.name for m in members}==set(manifest)
            for member in members:
                assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
                value=stream.extractfile(member).read();expected=manifest[member.name]
                assert len(value)==expected['bytes'] and hashlib.sha256(value).hexdigest()==expected['sha256']
                if key.startswith('runtime') or key=='installedPackage':archived[member.name]=value
                if key=='implementation':implementation[member.name]=value
                if key.startswith('source-blobs-'):blobs[member.name]=value
                if key.startswith('diagnostic-outputs-'):diagnostics[member.name]=value
    replay=read('replay/source-overlays.json');base=read('replay/base-files.json')
    assert replay['baseRevision']==base['baseRevision']=='ba2e98e9f96dc7e89fa3569447454532c410d443'
    assert set(replay['attempts'])=={f'charts-build-v{i}' for i in range(1,6)}
    for name,overlay in replay['attempts'].items():
        manifest=read('attempts/'+name+'/inputs.json')['sourceFiles']
        for path,checksum in manifest.items():
            if path in overlay:
                assert overlay[path]==checksum and hashlib.sha256(blobs['blobs/'+checksum]).hexdigest()==checksum
            else:assert base['files'][path]['sha256']==checksum
    # Verify the source-only replay base from its immutable Git objects in one
    # streaming process; no sibling checkout or network source is required.
    process=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    try:
        seen=set()
        for row in base['files'].values():
            if row['gitObject'] in seen:continue
            seen.add(row['gitObject']);process.stdin.write((row['gitObject']+'\n').encode());process.stdin.flush()
            header=process.stdout.readline().decode().strip().split();assert len(header)==3 and header[0]==row['gitObject'] and header[1]=='blob'
            size=int(header[2]);value=process.stdout.read(size);assert len(value)==size and process.stdout.read(1)==b'\n'
            assert hashlib.sha256(value).hexdigest()==row['sha256']
    finally:process.stdin.close();process.wait();process.stdout.close()
    assert process.returncode==0
    for record in read('replay/diagnostic-outputs.json').values():
        location=record['location']
        value=(directory/location.removeprefix('candidate/')).read_bytes() if location.startswith('candidate/') else diagnostics[location]
        assert hashlib.sha256(value).hexdigest()==record['sha256']
    binding=read('package/artifact-binding.json')
    assert len(binding['installedFiles'])==133
    for name,checksum in binding['installedFiles'].items():assert hashlib.sha256(archived['install/'+name]).hexdigest()==checksum
    assert hashlib.sha256(archived['consumer-build/InstalledConsumer']).hexdigest()==binding['consumerSha256']
    for name,checksum in binding['producerCriticalFiles'].items():assert hashlib.sha256(implementation[name]).hexdigest()==checksum,name
    for name,checksum in binding['consumerFiles'].items():assert hashlib.sha256(implementation['tests/consumer/'+name]).hexdigest()==checksum,name
    producer=read('attempts/charts-build-v5/inputs.json')['sourceFiles']
    for name,checksum in binding['producerCriticalFiles'].items():assert producer[name]==checksum,name
    package=read('package/inputs.json')
    for name,checksum in binding['consumerFiles'].items():assert package['consumer/'+name]==checksum,name
    for snapshot in [package,read('runtime-proof/inputs.json')['files']]:
        assert {n.removeprefix('install/'):v for n,v in snapshot.items() if n.startswith('install/')}==binding['installedFiles']
    assert '100% tests passed, 0 tests failed out of 31' in (directory/'qt/run.log').read_text()
    assert read('package/result.json')['exitCode']==read('runtime-proof/result.json')['exitCode']==0
    assert [r['exitCode'] for r in read('package/steps.json')]==[0,0,1]
    corpus=inputs.rows();expected={r['path']:r for r in corpus};comparison=read('comparison/comparison.json')
    assert comparison['status']=='failed' and comparison['summary']==report['strictComparison']
    assert len(comparison['results'])==len(expected)==1744
    for result in comparison['results']:
        row=expected[result['fixture']];path=directory/'captures'/row['path'];meta=read('captures/'+row['path']+'.json')
        observed=inputs.observations(row,meta)
        for key in ['layoutStatus','nativeFrameStatus','nativeMetricsStatus','stateStatus']:assert result[key]==observed[key]
        pixels=pixel_metrics(ROOT/row['reference'],path)
        assert result['pixelStatus']==('passed' if pixels['matches'] else 'failed')
        for key in ['changedPixels','maximumChannelError']:assert result[key]==pixels[key]
        assert result['status']==('passed' if pixels['matches'] and all(observed[k]!='failed' for k in ['layoutStatus','nativeMetricsStatus','stateStatus']) else 'failed')
    projection=json.loads(inputs.PROJECTION.read_text())
    for name in ['light','dark']:
        for scale in [1,1.5]:
            for dpr in [1,2]:validate_profile(read('captures/'+inputs.prefix(name,scale,dpr)+'.json'),projection)
    profiles=[p for p in (directory/'runtime').glob('*.json') if p.name!='environment.json']
    assert len(profiles)==40
    for profile in profiles:
        value=json.loads(profile.read_text());assert value['platform'] in ['xcb','wayland'] and value['graphicsApi'] in [1,3]
        if value['fixture']=='charts':
            validate_profile(value,projection)
            for history in value['histories']:
                stem=profile.stem+'-'+history['configuration']['id']+'-history-step'
                assert archived['runtime/'+stem+'0.png']==archived['runtime/'+stem+'7.png']
                assert archived['runtime/'+stem+'0.png']!=archived['runtime/'+stem+'1.png']
    regression=read('regression/catalogs.json');assert regression['status']=='passed' and len(regression['records'])==131
    assert all(r['pixelsIdentical'] and r['metadataIdentical'] for r in regression['records'])
    operator=read('operator/result.json');assert operator['status']=='passed' and operator['exitCode']==0 and operator['controls']==14 and operator['clicks']==24 and len(operator['records'])==25
    for row in operator['records']:
        assert row['passed'] is True and row['attempts'][-1]['exactViewportMatch'] is True
        actual=Image.open(directory/'operator'/row['attempts'][-1]['path']).convert('RGBA').crop((24,200,664,600))
        with Image.open(directory/'operator'/row['reference']) as native:assert actual.tobytes()==native.convert('RGBA').tobytes()
    if (directory/'host/results.json').exists():
        host=read('host/results.json');assert len(host)==report['validation']['hostCommands'] and all(row['exitCode']==0 for row in host)
        assert report['validation']['hostContractTests']==568
    print('Charts candidate: 1744 strict pairs, 40 virtual profiles, 25 operator states; native acceptance remains pending')
    return report
if __name__=='__main__':verify()
