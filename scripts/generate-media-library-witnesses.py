#!/usr/bin/env python3
"""Package every native media-grid context for independent Linux observation."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/reference-investigations/media-library-20261017'
OUTPUT=ROOT/'tests/consumer/native-media-library-witnesses.json'
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
def projected():
    read=lambda n:json.loads((SOURCE/n).read_text())
    def observed(row,paths):
        public,probe=row['states'][:2]
        return dict(configuration=row['configuration'],appearance=row.get('appearance',public.get('appearance')),textScale=row.get('textScale',public.get('textScale')),frame=dict(grid=probe['gridFrame'],caller=probe['callerFrame'],tiles=probe['tileFrames']),lifecycle=public['lifecycle'],reference=str((SOURCE/paths).relative_to(ROOT)))
    closed=[]
    for row in read('output/captures.json')['rows']:
        assert row['publicProbedIdentical'] and row['publicLiteralIdentical']
        closed.append(dict(observed(row,'output/'+row['paths'][0]),dpr=row['dpr']))
    histories=[]
    for row in read('history-output/histories.json')['histories']:
        steps=[]
        for step in row['steps']:
            assert step['publicProbedIdentical'] and step['publicLiteralIdentical']
            configured=dict(step,configuration=step['states'][0]['configuration'])
            steps.append(dict(observed(configured,'history-output/'+step['paths'][0]),step=step['step'],pointer=step['pointer'],matchesInitialPixels=step['matchesInitialPixels']))
        histories.append(dict(configuration=row['configuration'],appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],steps=steps))
    configurations={f['id']:f for f in read('edge-cases.json')};edges=[]
    for row in read('edge-results.json'):
        value=dict(configuration={k:v for k,v in configurations[row['fixture']].items() if v is not None},appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],nativeExitCode=row['exitCode'],nativeLog=str((SOURCE/row['log']).relative_to(ROOT)))
        if row['exitCode']==0:
            capture=read(row['output']+'/captures.json')['rows'][0];value.update(observed(capture,row['output']+'/'+capture['paths'][0]))
        else:value.update(reference=None,frame=None,lifecycle=None)
        edges.append(value)
    sizing=[dict(configuration=r['configuration'],appearance=r['appearance'],textScale=r['textScale'],dpr=r['dpr'],public=r['modes'][0]['proposals'],witnesses=[m['proposals'] for m in r['modes'][1:]]) for r in read('sizing-output/sizing.json')['rows']]
    assert (len(closed),len(histories),len(edges),len(sizing))==(496,48,112,496)
    return dict(reference=REFERENCE,accepted=False,sourceSha256=hashlib.sha256((SOURCE/'investigation.json').read_bytes()).hexdigest(),closed=closed,histories=histories,edges=edges,sizing=sizing,scope='Every public native image, transparent closed/history geometry, lifecycle, direct public sizing response and isolated edge outcome. The one sizing witness difference stays intact; no baseline approval.')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();value=json.dumps(projected(),indent=2,ensure_ascii=False)+'\n'
    if args.check:assert OUTPUT.read_text()==value,'Native MediaLibrary witness projection changed'
    else:OUTPUT.write_text(value)
    print('MediaLibrary witnesses: 496 closed, 48 histories, 112 edge and 496 sizing contexts; acceptance pending')
