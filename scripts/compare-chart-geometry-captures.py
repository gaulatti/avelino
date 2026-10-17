#!/usr/bin/env python3
"""Compare every supplemental native/Qt chart pixel and plot-proxy value."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
capture=module('chart_geometry_capture','capture-chart-geometry-cases.py')
def compare(candidate,output):
    candidate,output=Path(candidate),Path(output);assert not output.exists();corpus=capture.rows();pixels=module('chart_geometry_pixels','compare-captures.py')
    manifest={'captures':[dict(path=r['path'],source=capture.inputs.REFERENCE,sha256=capture.inputs.digest(ROOT/r['reference']),api=capture.inputs.APIS[r['configuration']['kind']],fixture=r['path'],width=640,height=400,dpr=r['dpr'],appearance='light',textScale=1) for r in corpus]}
    with tempfile.TemporaryDirectory(prefix='avelino-chart-geometry-') as temporary:
        reference=Path(temporary)
        for row in corpus:(reference/row['path']).symlink_to((ROOT/row['reference']).resolve())
        pixels.compare(reference,candidate,output,manifest=manifest)
    report=json.loads((output/'comparison.json').read_text());rows={r['path']:r for r in corpus}
    for result in report['results']:
        expected=rows[result['fixture']];actual=json.loads((candidate/(result['fixture']+'.json')).read_text())
        result['pixelStatus']=result['status'];result['reference']=str(ROOT/expected['reference'])
        result['nativeFrameStatus']='passed' if actual['frame']==expected['frame'] else 'failed'
        result['nativeMetricsStatus']='passed' if capture.inputs.subset(actual['metrics'],expected['metrics']) else 'failed'
        result['stateStatus']='passed' if actual['configuration']==expected['configuration'] and actual['state']==dict(appearances=1,disappearances=0,wrapperInstances=1) else 'failed'
        if any(result[k]=='failed' for k in ['nativeFrameStatus','nativeMetricsStatus','stateStatus']):result['status']='failed'
    summary=dict(cases=125,exactMatches=sum(r['status']=='passed' for r in report['results']),pixelMatches=sum(r['pixelStatus']=='passed' for r in report['results']),nativeFrameMatches=sum(r['nativeFrameStatus']=='passed' for r in report['results']),nativeMetricMatches=sum(r['nativeMetricsStatus']=='passed' for r in report['results']),stateMatches=sum(r['stateStatus']=='passed' for r in report['results']))
    report.update(accepted=False,status='passed' if all(r['status']=='passed' for r in report['results']) else 'failed',summary=summary,scope='Every supplemental requested-scale/tiny/categorical/legend context. Native fonts, fractional layout, raster, physical displays/input and readers remain pending; no exclusions or tolerances.')
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(summary,indent=2));return 0 if report['status']=='passed' else 1
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raise SystemExit(compare(a.candidate,a.output))
