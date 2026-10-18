#!/usr/bin/env python3
"""Validate native observations without accepting a Linux HeroCarousel mirror."""
import hashlib
import itertools
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/hero-carousel-20261018'
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'


def verify():
    read=lambda name:json.loads((DIRECTORY/name).read_text())
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    report=read('investigation.json')
    assert report['accepted'] is False and report['reference']==REFERENCE
    assert report['status']=='native investigation; Linux implementation pending'
    assert report['expectedImagesChanged'] is False and report['tolerance']=='none'and report['approvedExceptions']==[]
    assert report['desktopCandidateCoverage']==[75,80]and report['acceptedDesktopEntries']==0
    assert report['remainingAcceptance']==['LinuxImplementationCatalogConsumer','nativeWheelMomentumAndSettling','nativeDynamicIdentityAndLazyTiming','nativeSizingAfterOtherHistories','nativeGenericIDContexts','readers','physicalDisplaysInput','independentMachineReplayAvailability']
    files=read('files.json')
    assert set(files)=={str(p.relative_to(DIRECTORY))for p in DIRECTORY.rglob('*')if p.is_file()and p.name!='files.json'}
    for name,row in files.items():
        path=DIRECTORY/name;assert path.stat().st_size==row['bytes']and digest(path)==row['sha256'],name
    fixtures=read('fixtures.json');by_id={f['id']:{k:v for k,v in f.items()if v is not None}for f in fixtures};assert len(fixtures)==len(by_id)==20
    captures=read('output/captures.json');rows=captures['rows'];assert captures['accepted'] is False and captures['reference']==REFERENCE and len(rows)==160
    contexts=set(itertools.product(by_id,['light','dark'],[1,1.5],[1,2]))
    assert {(r['configuration']['id'],r['appearance'],r['textScale'],r['dpr'])for r in rows}==contexts
    for row in rows:
        assert row['configuration']==by_id[row['configuration']['id']]and row['modes']==[0,1,2]
        images=[(DIRECTORY/'output'/name).read_bytes()for name in row['paths']]
        assert images[0]==images[1]==images[2]and row['publicProbedIdentical'] is row['publicLiteralIdentical'] is True
        assert all(struct.unpack('>II',raw[16:24])==(640*row['dpr'],400*row['dpr'])for raw in images)
        public,probed,literal=row['states']
        assert all(probed[key]==literal[key]for key in ('carouselFrame','callerFrame','slideFrames'))
        assert public['lifecycle']==probed['lifecycle']==literal['lifecycle']
        for state in row['states']:
            assert state['windowVisible'] is True and state['windowKey'] is state['applicationActive'] is False
            assert state['accessibility']['truncated'] is False
        if not row['configuration']['items']or row['configuration']['width']==0:
            assert probed['slideFrames']=={}and probed['lifecycle']['slideInstances']=={}
    sizing=read('sizing-output/sizing.json');assert len(sizing['rows'])==160
    assert {(r['configuration']['id'],r['appearance'],r['textScale'],r['dpr'])for r in sizing['rows']}==contexts
    queries=0
    for row in sizing['rows']:
        assert row['configuration']==by_id[row['configuration']['id']]
        assert row['modes'][0]['proposals']==row['modes'][1]['proposals']==row['modes'][2]['proposals']
        for mode in row['modes']:assert len(mode['proposals'])==15;queries+=15
    assert queries==report['summary']['sizingQueries']==7200
    for prefix,placement in [('window',False),('placement',True)]:
        data=read(f'diagnostics/{prefix}/{prefix}-sizing.json');assert data['accepted'] is False and len(data['rows'])==12
        assert len(read(f'diagnostics/{prefix}/commands.json'))==2
        assert all(c['exitCode']==0 for c in read(f'diagnostics/{prefix}/commands.json'))
        for row in data['rows']:
            modes=row['modes'];assert modes[0]['proposals']==modes[1]['proposals']==modes[2]['proposals']
            assert all(len(mode['proposals'])==15 for mode in modes)
            width=row['placementWidth']if placement else 200
            expected=0 if row['fixture']=='empty'else 3*width+32
            assert modes[0]['proposals']['unspecified']['width']==expected
            assert all(mode['hostBounds']['width']==row['windowWidth']for mode in modes)
    for prefix in ('fresh','replay'):
        result=read(f'provenance/{prefix}/result.json');assert result['exitCode']==0 and result['sourceFilesUnchanged']==89 and result['prebuiltLibraryInputs'] is False
        commands=read(f'provenance/{prefix}/commands.json');assert len(commands)==4 and all(c['exitCode']==0 for c in commands)
        identity=read('provenance/source-identity.json')
        assert read(f'provenance/{prefix}/inputs.json')['sourceFiles']=={row['path']:row['sha256']for row in identity['files']}
    artifact=read('provenance/source-only-artifact.json');assert report['sourceOnlyArtifact']==artifact
    assert artifact['files']==10 and artifact['containsPinnedSourceFiles']==89 and artifact['downloadAvailability']=='pending independent-machine replay'
    assert read('pilot/pilot-result.json')['exitCode']==-5
    assert 'unable to find bundle named Sabella_Sabella'in(DIRECTORY/'pilot/pilot.log').read_text()
    assert read('pilot/pilot-v2-result.json')['exitCode']==0 and len(read('pilot/output/captures.json')['rows'])==11
    interactive=read('interactive/observations.json')
    assert interactive['accepted'] is interactive['animationsSuppressed'] is interactive['physicalInput'] is False
    assert interactive['probeTerminatedViaQuitMenu'] is interactive['processAbsent'] is True
    assert interactive['wheelAndMomentumAcceptance']==interactive['readerAcceptance']=='pending'
    states=[json.loads(line)for line in(DIRECTORY/'interactive/states.jsonl').read_text().splitlines()]
    events=[json.loads(line)for line in(DIRECTORY/'interactive/input-events.jsonl').read_text().splitlines()]
    assert len(states)==interactive['samples']and len(events)==interactive['events']
    assert sum(e['eventType']==22 for e in events)==interactive['wheelEventsObserved']==0
    assert sum(e['eventType']==10 and e['keyCode']==124 for e in events)==3
    for key,x in [('initial',0),('accessibleLast',706),('accessibleRestored',0)]:
        state=interactive[key];assert state in states
        scroll=state['scrollViews'][0];assert scroll['visibleRect']['x']==x and scroll['visibleRect']['width']==337
        assert scroll['documentFrame']['width']==1043 and scroll['horizontalScroller'] is scroll['verticalScroller'] is False
    first=interactive['initial']['lifecycle']['slideInstances']['0'];restored=interactive['accessibleRestored']['lifecycle']['slideInstances']['0'];assert first==restored==1
    replay=read('replay.json');assert replay['accepted'] is False and replay['prebuiltLibraryInputs'] is False and replay['sourceFilesUnchanged']==89
    assert len(replay['results'])==report['summary']['replayFiles']==482
    exact=0
    for row in replay['results']:
        first=DIRECTORY/row['path'];second=DIRECTORY/'replay'/row['path']
        assert digest(first)==row['firstSha256']and digest(second)==row['replaySha256']
        same=first.read_bytes()==second.read_bytes();assert row['status']==('passed'if same else'failed');exact+=same
    assert exact==report['summary']['replayExactFiles']
    assert report['sourceReplayStatus']==('passed'if exact==482 and not replay['extraFiles']else'failed')
    print(f'Native HeroCarousel: 160 closed contexts, 7200 sizing queries, placement diagnostics, source replay {exact}/482; Linux and input/reader/physical acceptance pending')


if __name__=='__main__':verify()
