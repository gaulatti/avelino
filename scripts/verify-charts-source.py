#!/usr/bin/env python3
"""Audit public native charts, plot probes, edge inputs and fresh-source replay."""
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/charts-20261017'
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
KINDS=['line','bar','pie','scatter','sparkline']
CONTEXTS=set(itertools.product(['light','dark'],[1,1.5],[1,2]))
STEPS=['initial','data','size','appearance','text-scale','direction','disabled','restore']
GATES=['LinuxImplementation','nativeRasterFontsSymbols','nativeInputTiming','nativeNonfiniteInputDeterminism','physicalDisplaysInput','readers','independentMachineReplayAvailability']
PALETTES={
    'light':[(44,87,132),(193,129,77),(166,93,87),(198,167,96),(118,50,63)],
    'dark':[(91,163,245),(224,172,105),(212,123,117),(212,175,55),(118,50,63)]}
HISTORIES={'line-default','line-area-default','bar-default','pie-default','scatter-default','sparkline-default'}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def context(row):return row['appearance'],row['textScale'],row['dpr']
def validate_report(report):
    assert report['reference']==REFERENCE and report['accepted'] is False
    assert report['status']=='source-investigation; Linux implementation pending'
    assert report['expectedImagesChanged'] is False and report['approvedExceptions']==[] and report['tolerance']=='none'
    assert report['remainingAcceptance']==GATES
    assert report['sourceReplayComparisonStatus']=='failed' and report['archiveReplayComparisonStatus'] in ['passed','failed']
    for key,value in dict(fixtures=120,closedContexts=960,closedImages=3840,sizingContexts=960,sizingQueries=12480,histories=48,historySteps=384,historyImages=1152,edgeCases=50,nonfiniteCases=45,finiteControls=5,edgeContexts=400,edgeImages=400,images=5392,replayedFiles=5688).items():assert report['summary'][key]==value,key

def wrapper(state):
    assert (state['appearances'],state['disappearances'],state['wrapperInstances'])==(1,0,1)
    assert state['windowVisible'] is True and state['windowKey'] is False and state['applicationActive'] is False
    assert state['backingDpr']==2
    assert state['accessibility']['truncated'] is False
    for frame in [state['frame'],state['metrics'].get('plotFrame',{})]:
        if frame:
            assert set(frame)=={'x','y','width','height'}
            assert all(isinstance(v,(int,float)) and math.isfinite(v) for v in frame.values())
            assert frame['width']>=0 and frame['height']>=0

def verify(directory=DIRECTORY):
    from PIL import Image
    directory=Path(directory);read=lambda n:json.loads((directory/n).read_text())
    report=read('investigation.json');validate_report(report)
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name not in ['investigation.json','README.md']}
    assert set(report['files'])==actual
    for name,checksum in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory/name)==checksum,name
    fixtures=read('fixtures.json');by_id={f['id']:f for f in fixtures}
    assert len(fixtures)==len(by_id)==120 and {f['kind'] for f in fixtures}==set(KINDS)
    captures={};images=set();palette_rows=[];scale_pairs=0
    def png(folder,name,dpr):
        path=directory/folder/name;key=str(path.relative_to(directory));assert key not in images;images.add(key)
        with Image.open(path) as image:assert image.size==(640*dpr,400*dpr)
        return path.read_bytes()
    for fixture in fixtures:
        name=fixture['id'];folder='captures/closed-'+name;data=read(folder+'/captures.json')
        assert data['reference']==REFERENCE and data['accepted'] is False and len(data['rows'])==8
        assert {context(r) for r in data['rows']}==CONTEXTS
        for row in data['rows']:
            assert row['configuration']==fixture
            assert row['modes']==[0,1,2,3] and len(row['paths'])==len(row['states'])==4
            assert row['publicProbedIdentical'] is True and row['publicLiteralIdentical'] is True
            values=[png(folder,n,row['dpr']) for n in row['paths']]
            assert values[0]==values[1]==values[2]
            for state in row['states']:wrapper(state)
            public,probed,literal,styles=row['states']
            assert public['frame']==public['metrics']=={}
            assert probed['frame']==literal['frame']==styles['frame']
            assert probed['metrics']==literal['metrics']==styles['metrics']
            captures[(name,*context(row))]=(row,values)
            if name.endswith('-series-eight'):
                domain=styles['metrics']['seriesDomain'];palette=PALETTES[row['appearance']][:5 if fixture['kind']=='pie' else 3 if fixture['kind']=='scatter' else 4]
                assert len(domain)==(1 if fixture['kind']=='sparkline' else 8)
                frame=styles['frame'];dpr=row['dpr']
                with Image.open(directory/folder/row['paths'][3]) as image:
                    image=image.convert('RGBA')
                    observed=[image.getpixel((round((frame['x']+8+16*i)*dpr),round((frame['y']+8)*dpr))) for i in range(len(domain))]
                expected=[(*palette[i%len(palette)],255) for i in range(len(domain))]
                assert observed==expected,(name,context(row),observed,expected)
                palette_rows.append(dict(fixture=name,appearance=row['appearance'],textScale=row['textScale'],dpr=dpr,domain=domain,rgba=[list(c) for c in observed]))
        for appearance,dpr in itertools.product(['light','dark'],[1,2]):
            assert captures[(name,appearance,1,dpr)][1][0]==captures[(name,appearance,1.5,dpr)][1][0]
            scale_pairs+=1
        sizing=read('captures/sizing-'+name+'/sizing.json')
        assert sizing['reference']==REFERENCE and sizing['accepted'] is False
        assert len(sizing['rows'])==8 and {context(r) for r in sizing['rows']}==CONTEXTS
        expected={
            'unspecified':(100,100),'zero':(1,1),'infinity':('+Infinity','+Infinity'),
            'width-zero':(1,100),'height-zero':(100,1),'square-100':(100,100),'spark-220-62':(220,62),
            'chart-460-260':(460,260),'large-2000-1000':(2000,1000),'width-460':(460,100),'height-260':(100,260),
            'infinite-width':('+Infinity',100),'infinite-height':(100,'+Infinity')}
        for row in sizing['rows']:
            assert row['configuration']==fixture and set(row['proposals'])==set(expected)
            assert row['windowKey'] is False and row['applicationActive'] is False and row['backingDpr']==2
            assert {key:(r['width'],r['height']) for key,r in row['proposals'].items()}==expected
    assert len(palette_rows)==40 and read('observations.json')['paletteWitnesses']==palette_rows
    assert scale_pairs==480
    for first,second in [('pie-radius--0.2','pie-series-eight'),('pie-radius-1.2','pie-radius-1')]:
        for ctx in CONTEXTS:assert captures[(first,*ctx)][1][0]==captures[(second,*ctx)][1][0]
    for name in HISTORIES:
        folder='captures/history-'+name;data=read(folder+'/histories.json')
        assert data['reference']==REFERENCE and data['accepted'] is False and len(data['histories'])==8
        assert {context(r) for r in data['histories']}==CONTEXTS
        for row in data['histories']:
            assert row['configuration']==by_id[name] and [r['step'] for r in row['steps']]==STEPS
            steps=[]
            for step in row['steps']:
                assert step['publicProbedIdentical'] is True and step['publicLiteralIdentical'] is True
                assert len(step['paths'])==len(step['states'])==3
                values=[png(folder,n,row['dpr']) for n in step['paths']];assert values[0]==values[1]==values[2];steps.append(values)
                for state in step['states']:wrapper(state)
                assert step['states'][1]['metrics']==step['states'][2]['metrics'] and step['states'][1]['frame']==step['states'][2]['frame']
            assert steps[0]!=steps[1] and steps[0]==steps[-1] and row['steps'][-1]['restoredInitialPixels'] is True
            assert steps[3]==steps[4]
            for before,after in zip(row['steps'][0]['states'],row['steps'][-1]['states']):
                for key in ['configuration','appearance','textScale','frame','metrics']:assert before[key]==after[key]
    edge_specs=read('edge-cases.json');assert len(edge_specs)==50 and len({s['id'] for s in edge_specs})==50
    assert sum(s['channel']=='none' for s in edge_specs)==5
    for spec in edge_specs:
        folder='edges/'+spec['id'];data=read(folder+'/edges.json')
        assert data['reference']==REFERENCE and data['accepted'] is False and data['specification']==spec
        assert len(data['rows'])==8 and {context(r) for r in data['rows']}==CONTEXTS
        for row in data['rows']:
            image=png(folder,row['path'],row['dpr']);wrapper(row['state'])
            if spec['channel']=='none':assert image==captures[(spec['kind']+'-default',*context(row))][1][0]
            if spec['distribution']=='all' and spec['channel'] in ['y','values']:
                assert image!=captures[(spec['kind']+'-empty',*context(row))][1][0]
    assert len(images)==5392
    replay=read('replay.json');rows=replay['results']
    outputs={str(p.relative_to(directory)) for folder in ['captures','edges'] for p in (directory/folder).rglob('*') if p.is_file()}
    assert len(rows)==len(outputs)==5688 and {r['path'] for r in rows}==outputs
    for row in rows:
        assert row['firstSha256']==digest(directory/row['path']) and row['replaySha256']==digest(directory/row['replayPath'])
        same=row['firstSha256']==row['replaySha256'];assert row['status']==('passed' if same else 'failed')
        if row['path'].startswith('captures/'):assert same
    assert replay['status']=='failed' and sum(r['status']=='passed' for r in rows)==report['summary']['sourceReplayExactFiles']<5688
    identity=read('source-identity.json')
    spec=importlib.util.spec_from_file_location('charts_source_tree',ROOT/'scripts/verify-native-source-rebuild.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    reference=json.loads((ROOT/'reference/source-manifest.json').read_text())['references']['desktop']
    assert len(identity['files'])==89 and module.tree_hash(identity['files'])==reference['tree']
    build=read('build-provenance.json');assert build['compiledInputs']==[] and build['automaticResolution'] is False and build['target']=='arm64-apple-macosx26.0'
    assert build['sourceOnlyArtifact']['files']['reference-source.tar']==identity['fullArchiveSha256']
    archive_replay=read('artifact-replay.json')['results']
    assert len(archive_replay)==5688 and {r['path'] for r in archive_replay}==outputs
    for row in archive_replay:
        assert row['expectedSha256']==digest(directory/row['path']) and row['archiveReplaySha256']==digest(directory/row['archiveReplayPath'])
        same=row['expectedSha256']==row['archiveReplaySha256'];assert row['status']==('passed' if same else 'failed')
        if row['path'].startswith('captures/'):assert same
    assert read('artifact-replay.json')['status']==report['archiveReplayComparisonStatus']
    exact=sum(r['status']=='passed' for r in archive_replay)
    assert exact==report['summary']['archiveReplayExactFiles']
    assert report['archiveReplayComparisonStatus']==('passed' if exact==5688 else 'failed')
    stability=read('diagnostics/nan-stability/stability.json');assert len(stability['trials'])==8
    initial=set()
    for trial in stability['trials']:
        values=[(directory/'diagnostics/nan-stability'/n).read_bytes() for n in trial['paths']]
        assert len(values)==3 and values[0]==values[1]==values[2] and trial['identicalWithinTrial'] is True
        initial.add(hashlib.sha256(values[0]).hexdigest())
    assert len(initial)>1
    assert len(build['sourceOnlyArtifact']['files'])==15 and 'rebuild.py' in build['sourceOnlyArtifact']['files']
    assert build['sourceOnlyArtifact']['compiledInputs']==[]
    for key in ['first','replay','archive']:
        assert build[key]['sourceFilesUnchanged']==89 and build[key]['libraryBuiltFromSources'] is True and build[key]['prebuiltLibraryInputs'] is False
        commands=read('provenance/'+key+'-commands.json')
        assert len(commands)==129 and all(r['exitCode']==0 for r in commands)
        assert '--disable-automatic-resolution' in commands[0]['command'] and '--target' in commands[0]['command'] and 'Sabella' in commands[0]['command']
        closed=read('provenance/'+key+'-closed-results.json');assert len(closed)==120 and {r['fixture'] for r in closed}==set(by_id) and all(r['exitCode']==0 for r in closed)
        edges=read('provenance/'+key+'-edge-commands.json');assert len(edges)==50 and all(r['exitCode']==0 for r in edges) and {r['id'] for r in edges}=={s['id'] for s in edge_specs}
        assert read('provenance/'+key+'-execution-result.json')['exitCode']==0
        assert read('provenance/'+key+'-edge-execution-result.json')['exitCode']==0
    attempts=read('attempts/source-input-artifact.json');assert attempts['compiledInputs']==[]
    assert {p.split('/')[0] for p in attempts['files']}=={'v1','v2'}
    assert [r['exitCode'] for r in read('attempts/v1/commands.json')]==[0,0,0]
    assert [r['exitCode'] for r in read('attempts/v2/commands.json')]==[0,1]
    assert 'NSAccessibility' in (directory/'attempts/v2/helper-build.log').read_text()
    return report['summary']

if __name__=='__main__':print('Native chart source:',json.dumps(verify(),sort_keys=True),'; Linux and reader acceptance pending')
