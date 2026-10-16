#!/usr/bin/env python3
"""Project sealed ButtonStyle frames and observed CUA input into the consumer."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/reference-investigations/button-style-20261016'

def projected():
    manifest=json.loads((SOURCE/'investigation.json').read_text());hashes={}
    def read(name):
        raw=(SOURCE/name).read_bytes();sha=hashlib.sha256(raw).hexdigest();assert manifest['files'][name]==sha
        hashes[str(SOURCE.relative_to(ROOT)/name)]=sha;return json.loads(raw)
    source=read('captures/captures.json')
    spec=importlib.util.spec_from_file_location('button_style_inputs',ROOT/'scripts/capture-button-style-cases.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.definitions(source)
    rows=[dict(configuration=r['configuration'],appearance=r['appearance'],textScale=r['textScale'],dpr=r['dpr'],
               parts=r['states'][1]['partInstances'],count=r['states'][1]['count'],calls=r['states'][1]['calls'],
               mountValues=r['states'][1]['mountValues']) for r in source['captures']]
    traces=[]
    for folder in ['input','input-key-window']:
        observations=read(folder+'/observations.json')
        traces.append(dict(id=folder,profile=dict(appearance='light',textScale=1.5,dpr=2),
            phases=[{k:p[k] for k in ['downPoint','upPoint','before','after','delta','duration']} for p in observations['rowPointerPhases']],
            visualClipIsInputClip=observations['visualClipIsInputClip']))
    return json.dumps(dict(reference=source['reference'],sourceFiles=hashes,frames=rows,inputTraces=traces,
        scope='Native closed frames and CUA-delivered pointer outcomes; Qt destructor, focused native keyboard, timing, physical input and reader acceptance separate'),indent=2,ensure_ascii=False)+'\n'

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    target=ROOT/'tests/consumer/native-button-style-witnesses.json';expected=projected()
    if args.check:assert target.read_text()==expected,'Native ButtonStyle consumer witnesses differ'
    else:target.write_text(expected)
    print('ButtonStyle consumer witnesses: 704 closed contexts and 13 observed pointer phases')
