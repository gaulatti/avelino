#!/usr/bin/env python3
"""Strictly compare all font-modifier pixels, emitted rectangles and baseline guides."""
import argparse
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
inputs=module('font_modifier_inputs','capture-font-modifier-cases.py')
observations=module('font_modifier_observations','font-modifier-observations.py').observations
def compare(candidate,output):
    pixels=module('font_modifier_pixels','compare-captures.py')
    candidate,output=Path(candidate),Path(output);assert not output.exists();output.mkdir(parents=True)
    corpus=inputs.rows();results=[]
    for kind in inputs.CORPORA:
        subset=[r for r in corpus if r['kind']==kind];directory=subset[0]['directory']/'captures'
        # The pixel comparator accepts a separate source/candidate path per entry.
        # Prefixes distinguish the same native fixture in different parent contexts.
        manifest={'captures':[dict(r['definition'],appearance=r['source']['appearance'],textScale=r['source']['textScale'],dpr=r['source']['dpr'],
            path=r['path'],sha256=inputs.digest(directory/r['source']['paths'][0])) for r in subset]}
        import tempfile
        with tempfile.TemporaryDirectory(prefix='avelino-font-reference-') as temporary:
            refs=Path(temporary)
            for r in subset:(refs/r['path']).symlink_to((directory/r['source']['paths'][0]).resolve())
            pixels.compare(refs,candidate,output/kind,manifest=manifest)
        report=json.loads((output/kind/'comparison.json').read_text());byname={r['path']:r for r in subset}
        for result in report['results']:
            row=byname[result['fixture']];result['reference']=str(directory/row['source']['paths'][0]);meta=json.loads((candidate/(row['path']+'.json')).read_text())
            result.update(observations(row,meta));result['corpus']=kind
            if result['partFramesStatus']=='failed' or result['baselineStatus']=='failed' or result['stateErrors']:result['status']='failed'
            results.append(result)
        (output/kind/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    summary=dict(cases=len(results),exactPixelAndGeometryMatches=sum(r['status']=='passed' for r in results),
        partFrameMatches=sum(r['partFramesStatus']=='passed' for r in results),baselineMatches=sum(r['baselineStatus']=='passed' for r in results),
        stateMatches=sum(r['stateStatus']=='passed' for r in results))
    report=dict(accepted=False,status='passed' if all(r['status']=='passed' for r in results) else 'failed',summary=summary,results=results,
        acceptance='Complete closed contexts only. Native fonts/raster, dynamic type, legibility, nonfinite Text layout, physical and reader acceptance remain pending.')
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(summary,indent=2))
    return 0 if report['status']=='passed' else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('candidate',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();raise SystemExit(compare(args.candidate,args.output))
