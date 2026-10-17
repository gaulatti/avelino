#!/usr/bin/env python3
"""Compare every captured surface guide, action sequence and unmodified RGBA image."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'evidence/reference-investigations/surface-baseline-input-20261016'
PROJECTION=ROOT/'tests/consumer/native-surface-supplement-witnesses.json'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def identity(row):return row['configuration']['fixture'],row['appearance'],row['textScale'],row['dpr']


def pixel_metrics(reference,candidate):
    from PIL import Image,ImageChops
    with Image.open(reference) as left,Image.open(candidate) as right:
        if left.size!=right.size:return dict(status='failed',sizeMatch=False,referenceSize=list(left.size),candidateSize=list(right.size))
        difference=ImageChops.difference(left.convert('RGBA'),right.convert('RGBA'))
        channels=difference.split();mask=channels[0]
        for channel in channels[1:]:mask=ImageChops.lighter(mask,channel)
        histogram=mask.histogram();changed=sum(histogram[1:]);count=left.width*left.height*4
        histograms=[channel.histogram() for channel in channels]
        absolute=sum(i*n for h in histograms for i,n in enumerate(h))
        squared=sum(i*i*n for h in histograms for i,n in enumerate(h))
        box=mask.getbbox()
        return dict(status='passed' if not changed else 'failed',sizeMatch=True,size=list(left.size),
            changedPixels=changed,maxChannelDelta=max((i for i,n in enumerate(histogram) if n),default=0),
            meanAbsoluteError=absolute/count,rootMeanSquareError=math.sqrt(squared/count),boundingBox=list(box) if box else None)


def compare(captures,output):
    captures=Path(captures);output=Path(output);output.mkdir()
    projected=json.loads(PROJECTION.read_text())
    baseline={identity(r):r for r in projected['nativeBaselineContexts']}
    pointer={identity(r):r for r in projected['nativeInputProfiles']}
    native_baseline={identity(r):r for r in json.loads((NATIVE/'baseline/baselines.json').read_text())['captures']}
    native_pointer={identity(r):r for r in json.loads((NATIVE/'input/input.json').read_text())['profiles']}
    manifest=json.loads((captures/'captures.json').read_text());assert manifest['complete'] is True and manifest['accepted'] is False
    assert set(manifest['files'])=={p.name for p in captures.iterdir() if p.is_file()}-{'captures.json'}
    assert all(digest(captures/n)==v for n,v in manifest['files'].items())
    results=[];seen_baselines=set();seen_inputs=set();sample_count=activation_differences=sequence_differences=0
    for command in manifest['commands']:
        assert command['exitCode']==0
        path=captures/command['report'];report=json.loads(path.read_text())
        assert report['accepted'] is False and report['structuralChecks']=='passed'
        first_result=len(results)
        kind='baseline' if report['fixture']=='surface-baseline' else 'input'
        for row in report['rows']:
            context=(row['configuration']['fixture'],report['appearance'],report['textScale'],report['dpr'])
            expected=(baseline if kind=='baseline' else pointer)[context]
            assert row['configuration']==expected['configuration']
            if kind=='baseline':
                assert context not in seen_baselines;seen_baselines.add(context)
                values=[(None,row,native_baseline[context]['paths'][0])]
            else:
                assert context not in seen_inputs;seen_inputs.add(context)
                assert [r['mode'] for r in row['modes']]==[0,3]
                values=[(mode['mode'],mode,native_pointer[context]['paths'][mode['mode']]) for mode in row['modes']]
            for mode,actual,native_name in values:
                name=Path(command['report']).stem+'-'+context[0]+('' if mode is None else '-mode'+str(mode))+'.png'
                source=NATIVE/kind/native_name;target=captures/name
                frames=actual['parts']==expected['parts']
                errors=[]
                if mode is None:
                    guides=actual['guides']==expected['guides'];state=actual['state']==expected['state']
                    assert actual['nativeFramesMatch'] is frames and actual['nativeGuidesMatch'] is guides
                    if not guides:errors.append('guides')
                    if not state:errors.append('state')
                    measured=dict(parts=actual['parts'],guides=actual['guides'],state=actual['state'])
                else:
                    native_mode=next(r for r in expected['modes'] if r['mode']==mode)
                    assert len(actual['activations'])==len(actual['sequences'])==len(expected['points'])
                    different=[i for i,(a,b) in enumerate(zip(actual['activations'],native_mode['activations'])) if a!=b]
                    sequences=[i for i,(a,b) in enumerate(zip(actual['sequences'],native_mode['sequences'])) if a!=b]
                    assert actual['differentActivationPoints']==different and actual['differentSequencePoints']==sequences
                    assert actual['nativeInputMatch'] is (not different and not sequences and frames)
                    assert actual['callerRetained'] is True
                    sample_count+=len(expected['points']);activation_differences+=len(different);sequence_differences+=len(sequences)
                    if different:errors.append('activations')
                    if sequences:errors.append('sequences')
                    measured=dict(parts=actual['parts'],initialState=actual['initialState'],finalState=actual['finalState'],
                        differentActivationPoints=different,differentSequencePoints=sequences)
                if not frames:errors.append('frames')
                pixels=pixel_metrics(source,target)
                if pixels['status']!='passed':errors.append('pixels')
                results.append(dict(context=list(context),kind=kind,mode=mode,accepted=False,status='failed' if errors else 'passed',
                    errors=errors,reference=str(source.relative_to(ROOT)),referenceSha256=digest(source),candidate=name,
                    candidateSha256=digest(target),report=command['report'],reportSha256=digest(path),pixelMetrics=pixels,observations=measured))
        recorded=results[first_result:]
        assert report['exactFrameSets']==sum('frames' not in r['errors'] for r in recorded)
        assert report['exactGuideSets']==sum(r['kind']=='baseline' and 'guides' not in r['errors'] for r in recorded)
        assert report['exactInputModes']==sum(r['kind']=='input' and not set(r['errors'])&{'frames','activations','sequences'} for r in recorded)
        native_matches=all(not set(r['errors'])&{'frames','guides','activations','sequences'} for r in recorded)
        assert report['nativeComparisonStatus']==('passed' if native_matches else 'failed')
    assert seen_baselines==set(baseline) and seen_inputs==set(pointer)
    summary=dict(baselineContexts=len(seen_baselines),baselineFrameMatches=sum(r['kind']=='baseline' and 'frames' not in r['errors'] for r in results),
        baselineGuideMatches=sum(r['kind']=='baseline' and 'guides' not in r['errors'] for r in results),inputProfiles=len(seen_inputs),inputModes=576,
        inputFrameMatches=sum(r['kind']=='input' and 'frames' not in r['errors'] for r in results),inputPoints=sample_count,
        activationMismatches=activation_differences,sequenceMismatches=sequence_differences,
        exactPixelMatches=sum(r['pixelMetrics']['status']=='passed' for r in results),exactCombinedMatches=sum(r['status']=='passed' for r in results),images=len(results))
    report=dict(reference=projected['reference'],accepted=False,status='passed' if all(r['status']=='passed' for r in results) else 'failed',
        comparison='Exact native frames, requested guides, full down/up/settled counters and RGBA bytes; no resize, mask, color conversion or tolerance',summary=summary,results=results)
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(summary,indent=2));return 0 if report['status']=='passed' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('captures');parser.add_argument('output');args=parser.parse_args()
    raise SystemExit(compare(args.captures,args.output))
