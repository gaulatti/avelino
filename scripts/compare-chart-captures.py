#!/usr/bin/env python3
"""Compare every chart pixel and all observed source geometry without tolerances."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
inputs=module('chart_capture_inputs','capture-charts.py')
def compare(candidate,output):
    pixels=module('chart_pixels','compare-captures.py')
    candidate,output=Path(candidate),Path(output);assert not output.exists();corpus=inputs.rows()
    manifest={'captures':[dict(path=r['path'],source=inputs.REFERENCE,sha256=inputs.digest(ROOT/r['reference']),
        api=inputs.APIS[r['configuration']['kind']],fixture=r['path'],width=640,height=400,dpr=r['dpr'],textScale=r['textScale'],appearance=r['appearance']) for r in corpus]}
    with tempfile.TemporaryDirectory(prefix='avelino-chart-reference-') as temporary:
        refs=Path(temporary)
        for row in corpus:(refs/row['path']).symlink_to((ROOT/row['reference']).resolve())
        pixels.compare(refs,candidate,output,manifest=manifest)
    report=json.loads((output/'comparison.json').read_text());expected={r['path']:r for r in corpus}
    for result in report['results']:
        row=expected[result['fixture']];result['reference']=str(ROOT/row['reference']);result['kind']=row['kind']
        meta=candidate/(row['path']+'.json')
        result.update(inputs.observations(row,json.loads(meta.read_text()) if meta.is_file() else {}))
        result['pixelStatus']=result['status']
        if any(result[k]=='failed' for k in ['layoutStatus','nativeMetricsStatus','stateStatus']):result['status']='failed'
    results=report['results']
    summary=dict(cases=len(results),exactMatches=sum(r['status']=='passed' for r in results),pixelMatches=sum(r['pixelStatus']=='passed' for r in results),
        layoutMatches=sum(r['layoutStatus']=='passed' for r in results),nativeFrameObservations=1344,nativeFrameMatches=sum(r['nativeFrameStatus']=='passed' for r in results),
        nativeMetricObservations=1344,nativeMetricMatches=sum(r['nativeMetricsStatus']=='passed' for r in results),stateMatches=sum(r['stateStatus']=='passed' for r in results),
        byKind={kind:dict(cases=sum(r['kind']==kind for r in results),exactMatches=sum(r['kind']==kind and r['status']=='passed' for r in results)) for kind in ['closed','edge','history']})
    report.update(accepted=False,status='passed' if all(r['status']=='passed' for r in results) else 'failed',summary=summary,
        acceptance='Complete closed, edge and retained-history diagnostic only. Bar NaN source initialization, native fonts, geometry, raster, physical input and reader acceptance remain pending. No source variants are excluded.')
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(summary,indent=2));return 0 if report['status']=='passed' else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('candidate',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();raise SystemExit(compare(args.candidate,args.output))
