#!/usr/bin/env python3
"""Project all native chart inputs and public observations for installed checks."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/reference-investigations/charts-20261017'
OUTPUT=ROOT/'tests/consumer/native-chart-witnesses.json'
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'

def projected():
    closed=[];histories=[];edges=[]
    for f in json.loads((SOURCE/'fixtures.json').read_text()):
        folder=SOURCE/('captures/closed-'+f['id'])
        for row in json.loads((folder/'captures.json').read_text())['rows']:
            public=row['states'][1]
            closed.append(dict(configuration=f,appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],frame=public['frame'],metrics=public['metrics'],reference=str((folder/row['paths'][0]).relative_to(ROOT))))
        folder=SOURCE/('captures/history-'+f['id'])
        if folder.exists():
            for row in json.loads((folder/'histories.json').read_text())['histories']:
                steps=[]
                for step in row['steps']:
                    public=step['states'][1]
                    steps.append(dict(step=step['step'],configuration=public['configuration'],appearance=public['appearance'],textScale=public['textScale'],frame=public['frame'],metrics=public['metrics'],reference=str((folder/step['paths'][0]).relative_to(ROOT))))
                histories.append(dict(configuration=f,appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],steps=steps))
    base=json.loads((SOURCE/'fixtures.json').read_text())[0]
    for spec in json.loads((SOURCE/'edge-cases.json').read_text()):
        configuration=copy.deepcopy(base);configuration.update(id=spec['id'],kind=spec['kind'])
        if spec['kind']=='sparkline':configuration.update(width=220,height=62)
        token={'nan':'__native_nan__','positive-infinity':'__native_positive_infinity__','negative-infinity':'__native_negative_infinity__'}.get(spec['token'])
        if spec['channel']=='radius':configuration['innerRadius']=token
        elif spec['channel']!='none':
            for i in range(len(configuration['points'])):
                if spec['distribution']=='all' or i==1:
                    if spec['channel']=='values':configuration['values'][i]=token
                    else:configuration['points'][i][spec['channel']]=token
        folder=SOURCE/'edges'/spec['id']
        for row in json.loads((folder/'edges.json').read_text())['rows']:
            edges.append(dict(configuration=configuration,specification=spec,appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],reference=str((folder/row['path']).relative_to(ROOT)),nativeNonfiniteDeterminism='pending' if spec['id']=='bar-y-nan-one' else 'observed source output; native acceptance pending'))
    assert len(closed)==960 and len(histories)==48 and len(edges)==400
    return dict(reference=REFERENCE,accepted=False,scope='Complete closed chart source inputs, retained histories and non-finite input traces. Tokens decode only in the fixture adapter; public chart APIs receive numeric NaN/infinities.',sourceSha256=hashlib.sha256((SOURCE/'investigation.json').read_bytes()).hexdigest(),closed=closed,histories=histories,edges=edges)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data=json.dumps(projected(),indent=2,ensure_ascii=False)+'\n'
    if args.check:assert OUTPUT.read_text()==data,'Native chart witness projection changed'
    else:OUTPUT.write_text(data)
    print('Chart witnesses: 960 closed contexts, 48 histories, 400 edge contexts; native parity pending')
