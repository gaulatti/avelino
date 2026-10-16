#!/usr/bin/env python3
"""Strictly compare ButtonStyle pixels, all per-view rectangles and initial state."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/reference-investigations/button-style-20261016'
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
pixels=module('button_style_pixels','compare-captures.py')
native=module('button_style_native','verify-button-style-source.py')
frames=module('button_style_bounds','compare-modal-captures.py')
inputs=module('button_style_inputs','capture-button-style-cases.py')

def observations(row,meta):
    f=row['configuration'];expected=row['states'][1]['partInstances'];actual=meta.get('buttonStylePartInstances',{})
    measured={key:[frames.bounds(rect,actual.get(key,[])[i] if i<len(actual.get(key,[])) else None)
                   for i,rect in enumerate(values)] for key,values in expected.items()}
    passed=set(expected)==set(actual) and all(len(actual[k])==len(values) for k,values in expected.items()) and all(v['status']=='passed' for values in measured.values() for v in values)
    expected_state={'renderedVariant':f['variant'],'renderedSize':f['size'],'renderedDisabled':f['disabled'],
        'renderedRtl':f['rtl'],'renderedWidthOffer':-1 if f['offer'] is None else f['offer'],
        'renderedMaximumWidth':640 if f['parentLayout']=='zstack' else -1,
        'buttonStyleState':{k:row['states'][1][k] for k in ['count','calls','mountValues']}}
    errors={k:{'reference':v,'candidate':meta.get(k)} for k,v in expected_state.items() if meta.get(k)!=v}
    objects=meta.get('renderedLabelObjects',[])
    names=[] if f['content']=='empty' else ['buttonStyleFirst','buttonStyleSecond'] if f['content']=='multi' else ['buttonStyleLabel']
    if [r.get('objectName') for r in objects]!=names:errors['renderedLabelObjects']={'expectedNames':names,'candidate':objects}
    return dict(partFrames=measured,partFramesStatus='passed' if passed else 'failed',stateErrors=errors,stateStatus='failed' if errors else 'passed')

def compare(candidate,output):
    native.verify();candidate,output=Path(candidate),Path(output);assert not output.exists()
    source=json.loads((SOURCE/'captures/captures.json').read_text());sealed=json.loads((SOURCE/'investigation.json').read_text())
    fixtures=[dict(**r['configuration'],api='BleeckerButtonStyle',source=inputs.REFERENCE,appearance=r['appearance'],textScale=r['textScale'],dpr=r['dpr'],path=r['paths'][0],
                   sha256=sealed['files']['captures/'+r['paths'][0]]) for r in source['captures']]
    pixels.compare(SOURCE/'captures',candidate,output,manifest={'captures':fixtures})
    report=json.loads((output/'comparison.json').read_text());byname={r['paths'][0]:r for r in source['captures']}
    for result in report['results']:
        row=byname[result['fixture']];meta=json.loads((candidate/(row['paths'][0]+'.json')).read_text())
        result.update(observations(row,meta))
        if result['partFramesStatus']=='failed' or result['stateErrors']:result['status']='failed'
    results=report['results'];report.update(accepted=False,status='passed' if all(r['status']=='passed' for r in results) else 'failed',
        acceptance='Closed-body diagnostics; fonts/raster, live sessions, focused native keyboard, physical input and readers remain separate pending gates',
        summary=dict(cases=len(results),exactPixelAndGeometryMatches=sum(r['status']=='passed' for r in results),
                     partFrameMatches=sum(r['partFramesStatus']=='passed' for r in results),stateMatches=sum(r['stateStatus']=='passed' for r in results)))
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary'],indent=2))
    return 0 if report['status']=='passed' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('candidate',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();raise SystemExit(compare(args.candidate,args.output))
