#!/usr/bin/env python3
"""Audit the native media grid without accepting its Linux peer or query gaps."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/media-library-20261017'
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
CONTEXTS=set(itertools.product(['light','dark'],[1,1.5],[1,2]))
STEPS=['initial','value-update','reorder','insert','remove','minimum-width','size','appearance','text-scale','direction','disabled','disabled-click','empty','restore','zero-width','width-restored','scroll-bottom','scroll-top','wait-0.2','wait-1.0','click-first']
GATES=['LinuxImplementation','nativeSizingWitnessDifference','nativeLazyViewportTiming','nativeGenericIDContexts','nativeTileFontAndRaster','nativeInputTiming','physicalDisplaysInput','readers','independentMachineReplayAvailability']
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def context(row):return row['appearance'],row['textScale'],row['dpr']
def configuration(value):return {k:v for k,v in value.items() if v is not None}
def validate_report(value):
    assert value['reference']==REFERENCE and value['accepted'] is False
    assert value['status']=='source-investigation; Linux implementation pending'
    assert value['expectedImagesChanged'] is False and value['approvedExceptions']==[] and value['tolerance']=='none'
    assert value['remainingAcceptance']==GATES
    expected=dict(fixtures=62,closedContexts=496,closedImages=1488,closedPixelWitnessMatches=496,closedGeometryWitnessMatches=496,closedLifecycleWitnessMatches=496,sizingContexts=496,sizingQueriesPerBranch=7440,sizingBranchQueries=22320,sizingWitnessMatches=495,histories=48,historySteps=1008,historyImages=3024,historyPixelWitnessMatches=1008,historyGeometryWitnessMatches=1008,historyLifecycleWitnessMatches=1008,ordinaryImages=4512,edgeFixtures=14,edgeContexts=112,edgeImages=312,edgeTerminalFailures=8,sourceRawFiles=4931)
    for key,count in expected.items():assert value['summary'][key]==count,key
    assert value['sourceReplayStatus'] in ['passed','failed']
    assert value['sourceOnlyArtifact']['files']==10 and value['sourceOnlyArtifact']['containsPinnedSourceFiles']==89
    assert value['sourceOnlyArtifact']['downloadAvailability']=='pending independent-machine replay'
def wrapper(state):
    assert state['windowVisible'] is True and state['windowKey'] is False and state['applicationActive'] is False
    assert state['backingDpr']==2 and state['accessibility']['truncated'] is False
    life=state['lifecycle'];assert (life['appearances'],life['disappearances'],life['wrapperInstances'])==(1,0,1)
    for frame in [state['gridFrame'],state['callerFrame'],*state['tileFrames'].values()]:
        if frame:
            assert set(frame)=={'x','y','width','height'} and all(type(v) in [int,float] and math.isfinite(v) for v in frame.values())
            assert frame['width']>=0 and frame['height']>=0
def observations(directory=DIRECTORY):
    directory=Path(directory);read=lambda n:json.loads((directory/n).read_text());fixtures=read('fixtures.json');by_id={f['id']:f for f in fixtures}
    assert len(fixtures)==len(by_id)==62 and {f['slot'] for f in fixtures}=={'fill','fixed','text','button'}
    images=set();pixel_matches=geometry_matches=lifecycle_matches=0
    def png(name,dpr):
        assert name not in images;images.add(name);path=directory/name
        assert struct.unpack('>II',path.read_bytes()[16:24])==(640*dpr,400*dpr)
        return path.read_bytes()
    closed=read('output/captures.json');assert closed['reference']==REFERENCE and closed['accepted'] is False and len(closed['rows'])==496
    assert {(r['configuration']['id'],*context(r)) for r in closed['rows']}==set(itertools.product(by_id,['light','dark'],[1,1.5],[1,2]))
    for row in closed['rows']:
        assert row['configuration']==configuration(by_id[row['configuration']['id']]) and row['modes']==[0,1,2]
        assert row['publicProbedIdentical'] is True and row['publicLiteralIdentical'] is True
        values=[png('output/'+p,row['dpr']) for p in row['paths']];assert values[0]==values[1]==values[2];pixel_matches+=1
        for state in row['states']:wrapper(state)
        public,probed,literal=row['states'];assert public['gridFrame']==public['callerFrame']==public['tileFrames']=={}
        assert all(probed[k]==literal[k] for k in ['gridFrame','callerFrame','tileFrames']);geometry_matches+=1
        assert public['lifecycle']==probed['lifecycle']==literal['lifecycle'];lifecycle_matches+=1
        f=row['configuration']
        if f['width']==0:assert probed['gridFrame']['height']==0 and probed['tileFrames']=={} and probed['lifecycle']['tileInstances']=={}
        if not f['items']:assert probed['gridFrame']['height']==0 and probed['tileFrames']=={}
    sizing=read('sizing-output/sizing.json');assert sizing['reference']==REFERENCE and sizing['accepted'] is False and len(sizing['rows'])==496
    assert {(r['configuration']['id'],*context(r)) for r in sizing['rows']}==set(itertools.product(by_id,['light','dark'],[1,1.5],[1,2]))
    differences=[];queries=0
    for row in sizing['rows']:
        assert row['configuration']==configuration(by_id[row['configuration']['id']])
        modes=row['modes'];assert [m['mode'] for m in modes]==[0,1,2]
        for mode in modes:
            assert len(mode['proposals'])==15 and mode['windowKey'] is False and mode['applicationActive'] is False and mode['backingDpr']==2;queries+=15
        changed={k:[m['proposals'][k] for m in modes] for k in modes[0]['proposals'] if not modes[0]['proposals'][k]==modes[1]['proposals'][k]==modes[2]['proposals'][k]}
        if changed:differences.append(dict(fixture=row['configuration']['id'],appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],proposals=changed))
    assert read('sizing-witness-differences.json')==differences and len(differences)==1
    history=read('history-output/histories.json');assert history['reference']==REFERENCE and history['accepted'] is False and len(history['histories'])==48
    names={f['id'] for f in read('histories.json')};assert names=={'width-337','fixed-count-8','text-long','button-count-8','scroll-dense','unicode'}
    assert {(h['configuration']['id'],*context(h)) for h in history['histories']}==set(itertools.product(names,['light','dark'],[1,1.5],[1,2]))
    history_pixels=history_geometry=history_lifecycle=0
    for row in history['histories']:
        assert row['configuration']==configuration(by_id[row['configuration']['id']]) and [s['step'] for s in row['steps']]==STEPS
        named={s['step']:s for s in row['steps']}
        for mode in range(3):
            lifecycle=lambda name:named[name]['states'][mode]['lifecycle']
            assert all(not states for states in lifecycle('zero-width')['activeTileStates'].values())
            assert lifecycle('restore')['tileInstances']==lifecycle('zero-width')['tileInstances']==lifecycle('width-restored')['tileInstances']
            if not row['configuration']['scroll']:
                assert lifecycle('initial')['tileInstances']==lifecycle('value-update')['tileInstances']==lifecycle('reorder')['tileInstances']
                assert all(count==1 for count in lifecycle('initial')['tileInstances'].values())
                for identifier in lifecycle('initial')['tileInstances']:assert lifecycle('restore')['tileInstances'][identifier]==2
        initial=None
        for step in row['steps']:
            values=[png('history-output/'+p,row['dpr']) for p in step['paths']]
            if initial is None:initial=values
            assert step['publicProbedIdentical'] is (values[0]==values[1]) and step['publicLiteralIdentical'] is (values[0]==values[2])
            assert step['matchesInitialPixels'] is (values==initial)
            for state in step['states']:wrapper(state)
            a,b,c=step['states'];history_pixels+=values[0]==values[1]==values[2]
            history_geometry+=all(b[k]==c[k] for k in ['gridFrame','callerFrame','tileFrames'])
            history_lifecycle+=a['lifecycle']==b['lifecycle']==c['lifecycle']
            if step['step']=='disabled-click':assert all(s['lifecycle']['actions']==[] for s in step['states'])
            if step['step']=='click-first' and row['configuration']['slot']=='button':assert all(s['lifecycle']['actions']==[row['configuration']['items'][0]['id']] for s in step['states'])
    assert len(images)==4512
    return dict(closedPixelWitnessMatches=pixel_matches,closedGeometryWitnessMatches=geometry_matches,closedLifecycleWitnessMatches=lifecycle_matches,sizingBranchQueries=queries,sizingWitnessMatches=496-len(differences),historyPixelWitnessMatches=history_pixels,historyGeometryWitnessMatches=history_geometry,historyLifecycleWitnessMatches=history_lifecycle)
def verify(directory=DIRECTORY):
    directory=Path(directory);read=lambda n:json.loads((directory/n).read_text());report=read('investigation.json');validate_report(report)
    assert set(report['files'])=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name not in ['investigation.json','README.md']}
    for name,checksum in report['files'].items():assert digest(directory/name)==checksum,name
    for key,value in observations(directory).items():assert report['summary'][key]==value,key
    identity=json.loads((ROOT/'evidence/reference-investigations/charts-20261017/source-identity.json').read_text())
    assert read('provenance/initial-inputs.json')['sourceFiles']=={r['path']:r['sha256'] for r in identity['files']}
    assert read('provenance/fresh-inputs.json')['files']['reference-source.tar']==identity['fullArchiveSha256']
    assert read('provenance/fresh-result.json')==dict(exitCode=0,sourceFilesUnchanged=89,prebuiltLibraryInputs=False,accepted=False)
    assert read('provenance/fresh-execution-result.json')['exitCode']==0
    commands=read('provenance/fresh-commands.json');assert len(commands)==5 and all(r['exitCode']==0 for r in commands)
    edges=read('edge-results.json');replayed_edges=read('provenance/fresh-edge-results.json');assert len(edges)==len(replayed_edges)==112
    edge_fixtures={f['id']:f for f in read('edge-cases.json')};assert len(edge_fixtures)==14
    assert {(r['fixture'],*context(r)) for r in edges}==set(itertools.product(edge_fixtures,['light','dark'],[1,1.5],[1,2]))
    outcome_matches=0
    for first,second in zip(edges,replayed_edges):
        for key in ['fixture','appearance','textScale','dpr']:assert first[key]==second[key]
        outcome_matches+=first['exitCode']==second['exitCode']
        assert first['exitCode']==(-5 if edge_fixtures[first['fixture']]['minimumTileWidth']==-16 else 0)
        if first['exitCode']==0:
            capture=read(first['output']+'/captures.json');assert capture['reference']==REFERENCE and capture['accepted'] is False and len(capture['rows'])==1
            row=capture['rows'][0];assert row['configuration']==configuration(edge_fixtures[first['fixture']]) and context(row)==context(first) and row['modes']==[0,1,2]
            assert len(row['paths'])==len(row['states'])==3
            images=[(directory/first['output']/name).read_bytes() for name in row['paths']]
            assert row['publicProbedIdentical'] is (images[0]==images[1]) and row['publicLiteralIdentical'] is (images[0]==images[2])
            for state in row['states']:wrapper(state)
        for path in (directory/first['output']).glob('*.png'):assert struct.unpack('>II',path.read_bytes()[16:24])==(640*first['dpr'],400*first['dpr'])
    assert report['summary']['edgeReplayOutcomeMatches']==outcome_matches
    replay=read('replay.json');assert replay['accepted'] is False and replay['prebuiltLibraryInputs'] is False and replay['sourceFilesUnchanged']==89
    raw={str(p.relative_to(directory)) for name in ['output','sizing-output','history-output','edges'] for p in (directory/name).rglob('*') if p.is_file() and p.suffix in ['.png','.json']}
    assert {r['path'] for r in replay['results']}==raw and len(replay['results'])==len(raw)
    exact=0
    for row in replay['results']:
        assert row['firstSha256']==digest(directory/row['path'])
        if row['replaySha256'] is None:assert row['replayPath'] is None
        else:assert row['replaySha256']==digest(directory/row['replayPath'])
        same=row['firstSha256']==row['replaySha256'];assert row['status']==('passed' if same else 'failed');exact+=same
    for row in replay['extraFiles']:
        assert row['path'] not in raw and row['sha256']==digest(directory/row['replayPath'])
    assert exact==report['summary']['sourceReplayExactFiles']
    assert report['sourceReplayStatus']==('passed' if exact==len(raw) and outcome_matches==112 and not replay['extraFiles'] else 'failed')
    if 'hostVerification' in report:
        assert report['hostVerification']['commands']==6 and report['hostVerification']['contractTests']==16 and report['hostVerification']['exitCode']==0
        commands=read('provenance/host/results.json');assert len(commands)==6 and all(r['exitCode']==0 for r in commands)
    print('Native MediaLibrary: 496 closed contexts, 22320 sizing queries, 1008 history steps; native sizing witness, lazy timing and Linux acceptance remain pending')
    return report
if __name__=='__main__':verify()
