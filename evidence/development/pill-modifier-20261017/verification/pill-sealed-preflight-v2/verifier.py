#!/usr/bin/env python3
"""Recompute sealed pill evidence while keeping native acceptance pending."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import re
import tarfile
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/development/pill-modifier-20261017'
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
GATES=['nativeFontsAndRaster','nativeSystemSymbols','richTextLineLimitCombinations','nativeInputTiming','physicalDisplaysInput','readers','independentMachineReferenceReplay']
ATTEMPT_EXITS={**{f'pill-build-v{i}':(1 if i==1 else 0) for i in range(1,16)},
    **{f'pill-package-v{i}':(1 if i<=2 else 0) for i in range(1,14)},
    'pill-package-final-v1':0,'pill-package-final-v2':0,'pill-package-final-v3':0,'pill-package-final-v4':0,'pill-full-v1':8,'pill-full-v2':8,'pill-full-v3':8,'pill-full-v4':0,
    'pill-focused-v1':0,'pill-focused-v2':0,'pill-dpr2-focused-v1':0,'pill-dpr2-focused-v2':0,'pill-marker-raster-v1':1,'pill-marker-raster-v2':0,'pill-focused-launch-v1':1,'pill-capture-v1':1,
    'pill-comparison-v1':1,'pill-comparison-v2':1,'pill-comparison-v3':1,'pill-comparison-v4':1,'pill-runtime-v1':1,'pill-runtime-v2':1,'pill-runtime-v3':1,'pill-runtime-v4':0,
    **{f'pill-runtime-probe-v{i}':(0 if i>=7 else 1) for i in range(1,10)},
    'pill-operator-v1':None,'pill-operator-v2':0,'pill-operator-v3':0,'pill-operator-v4':0,'pill-operator-v5':0}
def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
inputs=load('pill_candidate_inputs','capture-pill-modifier-cases.py')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_report(report):
    assert report['reference']==REFERENCE and report['accepted'] is False and report['status']=='verification-pending'
    assert report['tolerance']=='none' and report['approvedExceptions']==[] and report['expectedImagesChanged'] is False
    assert report['remainingAcceptance']==GATES
    assert report['strictComparisonStatus']=='failed'
    summary=report['strictComparison'];assert summary['cases']==2112 and summary['stateMatches']==2112
    assert 0<=summary['exactMatches']<2112
    for key in ['pixelMatches','partFrameMatches','baselineMatches']:assert summary['exactMatches']<=summary[key]<=2112
    assert {k:r['cases'] for k,r in summary['byKind'].items()}==dict(public=888,bare=888,history=336)
    validation=report['validation']
    for key,value in dict(fullQtTargets=29,independentModes=32,catalogCaptures=131,legacyPngs=127,legacyMetadata=127,installedFiles=127,virtualProfiles=32,operatorControls=18,operatorClicks=22,operatorStates=23,publicScalePairs=444,strictDefaultExitCode=1,strictImageExitCode=1).items():assert validation[key]==value,key
    assert validation['physicalDisplay'] is False and validation['hardwareAcceleration'] is False
    assert {r['name']:r['exitCode'] for r in report['attempts']}==ATTEMPT_EXITS
def validate_pill_profile(actual,projection):
    assert actual['reference']==REFERENCE and actual['accepted'] is False and actual['structuralChecks']=='passed'
    assert actual['nativeComparisonStatus']=='failed' and actual['measurements']==264
    assert actual['nativeRasterAcceptance']==actual['physicalInputAcceptance']==actual['readerAcceptance']=='pending'
    assert actual['qt']=='6.8.3' and actual['platform'] in ['offscreen','xcb','wayland'] and actual['graphicsApi'] in [1,3]
    assert actual['width']==640 and actual['height']==400
    context=(actual['appearance'],actual['textScale'],actual['dpr'])
    closed={r['configuration']['id']:r for r in projection['closed'] if (r['appearance'],r['textScale'],r['dpr'])==context}
    histories={r['configuration']['id']:r for r in projection['histories'] if (r['appearance'],r['textScale'],r['dpr'])==context}
    assert len(actual['rows'])==len(closed)==111 and len(actual['histories'])==len(histories)==7
    assert {r['configuration']['id'] for r in actual['rows']}==set(closed)
    assert {r['configuration']['id'] for r in actual['histories']}==set(histories)
    frames=guides=0
    def observe(value,expected):
        nonlocal frames,guides
        assert value['state']==dict(appearances=1,disappearances=0,callerInstances=1)
        same_frames=value['parts']==expected['parts'];same_guides=value['guides']==expected['guides']
        assert value['nativeFramesMatch'] is same_frames and value['nativeGuidesMatch'] is same_guides
        frames+=same_frames;guides+=same_guides
    for row in actual['rows']:
        expected=closed[row['configuration']['id']];assert row['configuration']==expected['configuration']
        assert [m['mode'] for m in row['modes']]==[0,3]
        for mode in row['modes']:observe(mode,expected if mode['mode']==0 else expected['bare'])
    for history in actual['histories']:
        expected=histories[history['configuration']['id']];assert history['configuration']==expected['configuration']
        assert len(history['steps'])==len(expected['steps'])==6
        for value,native in zip(history['steps'],expected['steps']):
            for key in ['step','configuration','appearance','textScale']:assert value[key]==native[key],key
            observe(value,native)
        assert history['steps'][-1]['restoredInitialPixelsAndGeometry'] is True
        assert history['steps'][0]['parts']==history['steps'][-1]['parts'] and history['steps'][0]['guides']==history['steps'][-1]['guides']
    assert actual['exactFrameSets']==frames and actual['exactGuideSets']==guides
def pixel_metrics(reference,candidate):
    with Image.open(reference) as a,Image.open(candidate) as b:
        assert a.size==b.size and 'icc_profile' not in a.info and 'icc_profile' not in b.info
        rgb=ImageChops.difference(a.convert('RGB'),b.convert('RGB'));alpha=ImageChops.difference(a.convert('RGBA').getchannel('A'),b.convert('RGBA').getchannel('A'))
        r,g,blue=rgb.split();maximum=ImageChops.lighter(ImageChops.lighter(r,g),blue)
        return dict(matches=rgb.getbbox() is None and alpha.getbbox() is None,changedPixels=rgb.width*rgb.height-maximum.histogram()[0],maximumChannelError=maximum.getextrema()[1])
def verify(directory=DIRECTORY):
    directory=Path(directory);read=lambda n:json.loads((directory/n).read_text());report=read('candidate.json');validate_report(report)
    assert set(report['files'])=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name not in ['candidate.json','README.md']}
    for name,checksum in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory/name)==checksum,name
    archives={}
    for key,record in report['archives'].items():
        manifest=read(record['manifest']);data={}
        with tarfile.open(directory/record['archive']) as stream:
            members=stream.getmembers();assert len(members)==len(manifest)==record['files']
            assert {m.name for m in members}==set(manifest)
            assert sum(m.size for m in members)<60*1024*1024
            for member in members:
                assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
                body=stream.extractfile(member).read();assert len(body)==manifest[member.name]['bytes'] and hashlib.sha256(body).hexdigest()==manifest[member.name]['sha256']
                data[member.name]=body
        archives[key]=data
    members={}
    for archive in archives.values():
        for name,data in archive.items():
            if name in members:assert members[name]==data
            members[name]=data
    if 'hostValidation' in archives:
        host=read('host/results.json');assert host and all(row['exitCode']==0 for row in host)
        assert report['validation']['hostCommands']==len(host) and report['validation']['hostContractTests']==518
        contracts=next(row for row in host if 'unittest' in row['command'])
        assert re.search(r'Ran 518 tests in .*\n\nOK',archives['hostValidation'][contracts['log']].decode())
        assert json.loads(archives['hostValidation']['inputs.json'])==read('host/inputs.json')
    for name,code in ATTEMPT_EXITS.items():assert read('attempts/'+name+'/result.json').get('exitCode')==code,name
    source=read('replay/source-overlays.json')
    assert source['baseRevision']=='63525f25f306b193b89a3baaab77e7cd8976383e'
    assert set(source['attempts'])=={f'pill-build-v{i}' for i in range(1,16)}
    for name,overlay in source['attempts'].items():
        manifest=read('attempts/'+name+'/inputs.json')['sourceFiles']
        for path,checksum in overlay.items():assert manifest[path]==checksum and hashlib.sha256(members['blobs/'+checksum]).hexdigest()==checksum
    references=list(read('replay/diagnostic-files.json').values())
    for snapshot in read('replay/consumer-snapshots.json').values():references.extend(snapshot.values())
    for record in references:
        location=record['location']
        if location.startswith('candidate/'):checksum=digest(directory/location.removeprefix('candidate/'))
        elif location.startswith('reference/'):checksum=digest(ROOT/location.removeprefix('reference/'))
        elif location.startswith('implementation/'):checksum=hashlib.sha256(archives['implementation'][location.removeprefix('implementation/')]).hexdigest()
        else:checksum=hashlib.sha256(members[location]).hexdigest()
        assert checksum==record['sha256'],location
    binding=read('package/artifact-binding.json');installation=archives['installedPackage']
    assert len(binding['installedFiles'])==127
    for name,checksum in binding['installedFiles'].items():assert hashlib.sha256(installation['install/'+name]).hexdigest()==checksum
    assert hashlib.sha256(installation['consumer-build/InstalledConsumer']).hexdigest()==binding['consumerSha256']
    implementation=archives['implementation']
    for name,checksum in binding['producerCriticalFiles'].items():assert hashlib.sha256(implementation[name]).hexdigest()==checksum
    for name,checksum in binding['consumerFiles'].items():assert hashlib.sha256(implementation['tests/consumer/'+name]).hexdigest()==checksum
    runtime_inputs=read('runtime-proof/inputs.json')['files'];package_inputs=read('package/inputs.json')
    for snapshot in [runtime_inputs,package_inputs]:assert {n.removeprefix('install/'):v for n,v in snapshot.items() if n.startswith('install/')}==binding['installedFiles']
    assert runtime_inputs['consumer-build/InstalledConsumer']==binding['consumerSha256']
    producer=read('attempts/pill-build-v15/inputs.json')
    assert digest(directory/'attempts/pill-build-v15/inputs.json')==binding['producerSourceManifestSha256']
    for name,checksum in binding['producerCriticalFiles'].items():assert producer['sourceFiles'][name]==checksum
    package='pill-package-final-v4'
    for name,checksum in binding['consumerFiles'].items():assert package_inputs['consumer/'+name]==checksum
    assert read('package/environment.json')['consumerSha256']==binding['consumerSha256']
    assert {n.removeprefix('install/'):v for n,v in read('package/environment.json')['installedFiles'].items()}==binding['installedFiles']
    assert [r['exitCode'] for r in read('package/steps.json')]==[0,0,1]
    assert [r['expectedExitCode'] for r in read('package/steps.json')]==[0,0,1]
    assert '100% tests passed, 0 tests failed out of 29' in (directory/'qt/run.log').read_text()
    assert '100% tests passed, 0 tests failed out of 3' in (directory/'qt/focused/run.log').read_text()
    qt_binding=read('qt/artifact-binding.json')
    assert qt_binding['fullSuiteProducer']=='pill-build-v14' and qt_binding['finalProducer']=='pill-build-v15'
    assert qt_binding['focusedAttempt']=='pill-focused-v2'
    full_install=qt_binding['fullSuiteInstalledFiles']
    assert set(full_install)==set(binding['installedFiles'])
    common={n:v for n,v in full_install.items() if v==binding['installedFiles'][n]}
    assert len(common)==126 and qt_binding['commonInstalledFiles']==common
    assert set(full_install)-set(common)=={'bin/AvelinoCatalog'}
    assert qt_binding['fullSuiteComponentExecutableSha256']==qt_binding['finalComponentExecutableSha256']
    assert report['validation']['focusedQtTargets']==3 and report['validation']['commonInstalledFiles']==126
    qt=(directory/'qt/LastTest.log').read_text()
    for key in ['componentChecksDpr1','componentChecksDpr2']:assert f'Totals: {report["validation"][key]} passed, 0 failed, 0 skipped, 0 blacklisted' in qt
    assert sum('QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer' in s for s in (directory/'package/check-installed.sh').read_text().splitlines())==32
    assert 'Installed catalog: 131 fixture captures passed without source/build import paths' in (directory/'package/0.log').read_text()
    assert len(list((directory/'catalogs').glob('*.png')))==131
    projection=json.loads(implementation['tests/consumer/native-pill-witnesses.json'])
    marker=load('pill_marker_raster','verify-pill-marker-raster.py').projected()
    assert marker==read('native-marker-raster.json') and len(marker['observations'])==1024
    assert sum(r['fullyVisible'] for r in marker['observations'])==928
    capture=read('captures/capture-results.json');assert capture['cases']==2112 and len(capture['contexts'])==8
    assert capture['consumerSha256']==binding['consumerSha256']
    for context in capture['contexts']:
        assert context['process']['exitCode']==0 and len(context['records'])==264
        validate_pill_profile(read('captures/'+context['context']+'.json'),projection)
        for record in context['records']:
            assert digest(directory/'captures'/record['path'])==record['sha256']
            assert digest(directory/'captures'/(record['path']+'.json'))==record['metadataSha256']
        profile=read('captures/'+context['context']+'.json')
        for history in profile['histories']:
            stem=context['context']+'-'+history['configuration']['id']+'-history-step'
            assert not pixel_metrics(directory/'captures'/(stem+'0.png'),directory/'captures'/(stem+'1.png'))['matches']
            assert pixel_metrics(directory/'captures'/(stem+'0.png'),directory/'captures'/(stem+'5.png'))['matches']
            assert history['steps'][0]['accessibleText']!=history['steps'][1]['accessibleText']
    fixtures={r['configuration']['id'] for r in projection['closed']}
    for appearance,dpr,fixture in itertools.product(['light','dark'],[1,2],fixtures):
        first=directory/'captures'/f'{appearance}-text1-dpr{dpr}-{fixture}-mode0.png'
        second=directory/'captures'/f'{appearance}-text1.5-dpr{dpr}-{fixture}-mode0.png'
        assert pixel_metrics(first,second)['matches'],(appearance,dpr,fixture)
    comparison=read('comparison/comparison.json');assert comparison['accepted'] is False and comparison['status']=='failed'
    assert comparison['summary']==report['strictComparison'] and len(comparison['results'])==2112
    rows={r['path']:r for r in inputs.rows(projection)};results=comparison['results'];assert {r['fixture'] for r in results}==set(rows)
    for result in results:
        row=rows[result['fixture']];image=directory/'captures'/row['path'];meta=read('captures/'+row['path']+'.json')
        observed=inputs.observations(row,meta)
        for key,value in observed.items():assert result[key]==value,(row['path'],key)
        pixels=pixel_metrics(ROOT/row['reference'],image)
        for key in ['changedPixels','maximumChannelError']:assert result[key]==pixels[key]
        assert result['pixelStatus']==('passed' if pixels['matches'] else 'failed')
        same=pixels['matches'] and all(observed[k]=='passed' for k in ['partFramesStatus','baselineStatus','stateStatus'])
        assert result['status']==('passed' if same else 'failed')
    for key,field in [('exactMatches','status'),('pixelMatches','pixelStatus'),('partFrameMatches','partFramesStatus'),('baselineMatches','baselineStatus'),('stateMatches','stateStatus')]:assert report['strictComparison'][key]==sum(r[field]=='passed' for r in results)
    for kind in ['public','bare','history']:assert report['strictComparison']['byKind'][kind]['exactMatches']==sum(r['kind']==kind and r['status']=='passed' for r in results)
    profiles={prefix+protocol+'-'+backend+'-'+configuration+'.json' for prefix,protocol,backend,configuration in itertools.product(['','font-modifier-','surface-modifier-','pill-modifier-'],['xcb','wayland'],['software','opengl'],['standard','scaled'])}
    assert {p.name for p in (directory/'runtime').glob('*.json')}==profiles|{'environment.json'}
    for name in profiles:
        row=read('runtime/'+name);assert row['physicalDisplay'] is False and row['hardwareAcceleration'] is False
        assert digest(directory/'runtime'/row['sessionCapture'])==row['sessionCaptureSha256']
        assert digest(directory/'runtime'/(name.removesuffix('.json')+'.png'))==row['windowCaptureSha256']
        if name.startswith('pill-modifier-'):
            validate_pill_profile(row,projection)
            for history in row['histories']:
                stem=name.removesuffix('.json')+'-'+history['configuration']['id']+'-history-step'
                assert pixel_metrics(directory/'runtime'/(stem+'0.png'),directory/'runtime'/(stem+'5.png'))['matches']
            assert 'different thread' not in (directory/'runtime'/name.replace('.json','.log')).read_text()
    operator=read('operator/result.json');assert operator['status']=='passed' and operator['exitCode']==0 and operator['accepted'] is False
    assert (operator['controls'],operator['clicks'],operator['phases'])==(18,22,23)
    assert operator['sourceAndConsumerSourcesAbsent'] is True and operator['producerBuildAbsent'] is True and operator['physicalDisplay'] is False
    for row in operator['records']:
        assert row['passed'] is True
        with Image.open(directory/'operator'/row['reference']) as source:expected=source.convert('RGBA')
        for attempt in row['attempts']:
            path=directory/'operator'/attempt['path'];assert digest(path)==attempt['sha256']
            with Image.open(path) as actual:matches=actual.convert('RGBA').crop((24,200,664,600)).tobytes()==expected.tobytes()
            assert attempt['exactViewportMatch'] is matches
        assert row['attempts'][-1]['exactViewportMatch'] is True
    legacy=read('regression/catalogs.json');assert legacy['status']=='passed' and len(legacy['records'])==127 and legacy['currentCaptures']==131
    previous=ROOT/'evidence/development/surface-supplement-20261016/catalogs'
    for row in legacy['records']:
        assert row['pixelsIdentical'] is True and row['metadataIdentical'] is True
        for name in [row['path'],row['path']+'.json']:assert digest(previous/name)==digest(directory/'catalogs'/name)
    return report
if __name__=='__main__':
    report=verify();print('Pill candidate:',json.dumps(report['strictComparison'],sort_keys=True),'; native acceptance pending')
