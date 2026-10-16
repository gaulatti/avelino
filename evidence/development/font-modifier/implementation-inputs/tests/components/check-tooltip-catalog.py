#!/usr/bin/env python3
"""Exercise closed Tooltip adapter states and validate native-owned geometry."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog,imports,root=map(Path,sys.argv[1:])
spec=importlib.util.spec_from_file_location('tooltip_capture_inputs',root/'scripts/capture-tooltip-cases.py');capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
source=json.loads((capture.SOURCE/'closed/captures.json').read_text());definitions=capture.definitions(source)
with tempfile.TemporaryDirectory(prefix='avelino-tooltip-catalog-') as temporary:
    directory=Path(temporary);inputs=directory/'fixtures.json';inputs.write_text(json.dumps(definitions,ensure_ascii=False))
    environment=dict(os.environ,QML_IMPORT_PATH=str(imports),QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1')
    pending={'content-inherited','parent-font32','parent-red'}
    for index,row in enumerate(definitions['fixtures']):
        name=row['fixture'];image=directory/f'{index}.png'
        native=next(r for r in source['captures'] if r['configuration']['fixture']==name and r['appearance']=='light' and r['textScale']==1 and r['dpr']==1)
        subprocess.run([str(catalog),'--fixture','reference-case','--case',name,'--case-definitions',str(inputs),'--capture',str(image)],env=environment,capture_output=True,check=True,timeout=20)
        actual=json.loads(image.with_name(image.name+'.json').read_text())
        assert actual['renderedHint']==row['hint'] and actual['renderedContent']==row['content']
        assert actual['renderedDisabled']==row['disabled'] and actual['renderedRtl']==row['rtl']
        assert actual['tooltipVisible'] is False and actual['helpAttached'] is True
        if name not in pending:assert actual['tooltipCallerRects']==native['states'][1]['parts'],name
    default=definitions['fixtures'][0]
    invalid=[dict(default,expectedEmpty=True),dict(default,content='unsupported'),dict(default,hint=[]),dict(default,disabled='yes'),dict(default,helpAttached=None),dict(default,parentFont=-1)]
    for index,forged in enumerate(invalid):
        inputs.write_text(json.dumps({'fixtures':[forged]}));result=subprocess.run([str(catalog),'--fixture','reference-case','--case',forged['fixture'],'--case-definitions',str(inputs),'--capture',str(directory/f'invalid-{index}.png')],env=environment,capture_output=True,timeout=20)
        assert result.returncode==6,(forged,result.returncode,result.stderr)
print('Tooltip catalog: 21 states, 18 native frame sets and six malformed definitions checked; inherited native fonts remain pending')
