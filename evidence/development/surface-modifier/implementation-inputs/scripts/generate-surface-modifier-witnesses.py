#!/usr/bin/env python3
"""Project every sealed surface observation into the independent package consumer."""
import argparse
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('surface_modifier_inputs',ROOT/'scripts/capture-surface-modifier-cases.py')
inputs=importlib.util.module_from_spec(spec);spec.loader.exec_module(inputs)
def projected():
    source=json.loads((inputs.DIRECTORY/'captures/captures.json').read_text())
    histories=[dict(content=h['content'],dpr=h['dpr'],steps=[dict(configuration=inputs.definition(step['configuration']),appearance=step['appearance'],textScale=step['textScale'],parts=step['state']['partInstances'],state={k:step['state'][k] for k in ['appearances','disappearances','callerInstances','actions','counter']}) for step in h['steps']]) for h in source['histories'] if h['mode']==1]
    assert len(histories)==10 and all(len(h['steps'])==6 for h in histories)
    return json.dumps(dict(histories=histories,reference=inputs.REFERENCE,accepted=False,baselineAcceptance='pending; centered source contexts did not request baseline guides',contexts=[dict(configuration=r['definition'],
        appearance=r['source']['appearance'],textScale=r['source']['textScale'],dpr=r['source']['dpr'],
        parts=r['source']['states'][1]['partInstances'],baselines=r['source']['states'][1]['baselines'],
        state={k:r['source']['states'][1][k] for k in ['appearances','disappearances','callerInstances','actions','counter']}) for r in inputs.rows()]),indent=2,ensure_ascii=False)+'\n'
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    target=ROOT/'tests/consumer/native-surface-modifier-witnesses.json';expected=projected()
    if args.check:assert target.read_text()==expected,'Surface projection differs from sealed native observations'
    else:target.write_text(expected)
    print('Surface consumer witnesses: 416 closed contexts; 52 per profile; acceptance pending')
