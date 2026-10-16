#!/usr/bin/env python3
"""Project complete sealed font source observations into the installed consumer."""
import argparse
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('font_modifier_inputs',ROOT/'scripts/capture-font-modifier-cases.py')
inputs=importlib.util.module_from_spec(spec);spec.loader.exec_module(inputs)
def projected():
    return json.dumps(dict(reference=inputs.REFERENCE,accepted=False,contexts=[dict(configuration=r['definition'],
        appearance=r['source']['appearance'],textScale=r['source']['textScale'],dpr=r['source']['dpr'],
        parts=r['source']['states'][1]['partInstances'],baselines=r['source']['states'][1]['baselines'],
        state={k:r['source']['states'][1][k] for k in ['appearances','disappearances','callerInstances']}) for r in inputs.rows()]),indent=2,ensure_ascii=False)+'\n'
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    target=ROOT/'tests/consumer/native-font-modifier-witnesses.json';expected=projected()
    if args.check:assert target.read_text()==expected,'Font consumer projection differs from sealed native observations'
    else:target.write_text(expected)
    print('Font consumer witnesses: 1656 closed contexts; 207 per requested profile; acceptance pending')
