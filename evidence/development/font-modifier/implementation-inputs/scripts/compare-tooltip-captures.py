#!/usr/bin/env python3
"""Compare original closed Tooltip pixels, actual caller geometry and state."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/reference-investigations/tooltip-20261016'
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
pixels=module('tooltip_pixels','compare-captures.py')
native=module('tooltip_native','verify-tooltip-source.py')
inputs=module('tooltip_inputs','capture-tooltip-cases.py')
frames=module('tooltip_frames','compare-modal-captures.py')

def compare(candidate,output):
    native.verify();candidate,output=Path(candidate),Path(output)
    assert not output.exists(), 'Comparison output must be new'
    source=json.loads((SOURCE/'closed/captures.json').read_text());investigation=json.loads((SOURCE/'investigation.json').read_text())
    definitions={r['fixture']:r for r in inputs.definitions(source)['fixtures']}
    fixtures=[{**definitions[r['configuration']['fixture']], 'appearance':r['appearance'],'textScale':r['textScale'],'dpr':r['dpr'],
        'path':r['paths'][0],'sha256':investigation['files']['closed/'+r['paths'][0]],
        'componentSize':{k:r['states'][1]['parts'].get('root',{}).get(k,0) for k in ['width','height']}} for r in source['captures']]
    pixels.compare(SOURCE/'closed',candidate,output,manifest={'captures':fixtures})
    report=json.loads((output/'comparison.json').read_text());byname={r['paths'][0]:r for r in source['captures']}
    for result in report['results']:
        row=byname[result['fixture']];meta=json.loads((candidate/(row['paths'][0]+'.json')).read_text());f=row['configuration']
        expected_parts=row['states'][1]['parts'];actual_parts=meta.get('tooltipCallerRects',{})
        result['callerFrames']={key:frames.bounds(value,actual_parts.get(key)) for key,value in expected_parts.items()}
        result['callerFramesStatus']='passed' if set(expected_parts)==set(actual_parts) and all(r['status']=='passed' for r in result['callerFrames'].values()) else 'failed'
        expected={'renderedHint':f['hint'],'renderedContent':f['content'],'renderedDisabled':f['disabled'],'renderedRtl':f['rtl'],'tooltipVisible':False,'counterValue':0,'mountValues':[0] if f['content']=='button' else []}
        result['stateErrors']={key:{'reference':value,'candidate':meta.get(key)} for key,value in expected.items() if meta.get(key)!=value}
        result['stateStatus']='passed' if not result['stateErrors'] else 'failed'
        if result['callerFramesStatus']=='failed' or result['stateErrors']:result['status']='failed'
    results=report['results'];report.update(accepted=False,status='passed' if all(r['status']=='passed' for r in results) else 'failed',
        acceptance='Closed-body diagnostic only; shown popup, native timing/font/compositor, real session/input and readers remain separate pending gates',
        summary={'cases':len(results),'exactPixelAndGeometryMatches':sum(r['status']=='passed' for r in results),
                 'callerFramesMatches':sum(r['callerFramesStatus']=='passed' for r in results),'stateMatches':sum(r['stateStatus']=='passed' for r in results)})
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary'],indent=2))
    return 0 if report['status']=='passed' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('candidate',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();raise SystemExit(compare(args.candidate,args.output))
