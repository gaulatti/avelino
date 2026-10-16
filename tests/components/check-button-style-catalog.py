#!/usr/bin/env python3
"""Check every ButtonStyle definition, measured parts and malformed inputs."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog,imports,root=map(Path,sys.argv[1:])
spec=importlib.util.spec_from_file_location('button_style_capture',root/'scripts/capture-button-style-cases.py')
capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
source=json.loads((capture.SOURCE/'captures/captures.json').read_text());definitions=capture.definitions(source)
with tempfile.TemporaryDirectory(prefix='avelino-button-style-catalog-') as temporary:
    directory=Path(temporary);inputs=directory/'fixtures.json';inputs.write_text(json.dumps(definitions,ensure_ascii=False))
    environment=dict(os.environ,QML_IMPORT_PATH=str(imports),QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1')
    for index,row in enumerate(definitions['fixtures']):
        name=row['fixture'];image=directory/f'{index}.png'
        native=next(r for r in source['captures'] if r['configuration']['fixture']==name and r['appearance']=='light' and r['textScale']==1 and r['dpr']==1)
        result=subprocess.run([str(catalog),'--fixture','reference-case','--case',name,'--case-definitions',str(inputs),'--capture',str(image)],env=environment,capture_output=True)
        assert result.returncode==0,(name,result.stderr.decode(errors='replace'))
        actual=json.loads(Path(str(image)+'.json').read_text())
        assert actual['renderedVariant']==row['variant'] and actual['renderedSize']==row['size']
        assert actual['renderedDisabled']==row['disabled'] and actual['renderedRtl']==row['rtl']
        assert actual['renderedWidthOffer']==(-1 if row['offer'] is None else row['offer'])
        assert actual['buttonStyleState']=={key:native['states'][1][key] for key in ['count','calls','mountValues']}
        if name not in ['content-system-font','text-unicode','text-bidi']:
            assert actual['buttonStylePartInstances']==native['states'][1]['partInstances'],name
        assert len(actual['renderedLabelObjects'])==(0 if row['content']=='empty' else 2 if row['content']=='multi' else 1)
    default=definitions['fixtures'][0]
    invalid=[dict(default,expectedEmpty=True),dict(default,content='unknown'),dict(default,variant='unknown'),dict(default,size='unknown'),
             dict(default,offer=-1),dict(default,parentLayout='grid'),dict(default,disabled='yes'),dict(default,parentFont=-1),
             dict(default,text=[]),dict(default,width=320),dict(default,destructiveRole=None)]
    for index,forged in enumerate(invalid):
        inputs.write_text(json.dumps({'fixtures':[forged]}))
        result=subprocess.run([str(catalog),'--fixture','reference-case','--case',forged['fixture'],'--case-definitions',str(inputs),'--capture',str(directory/f'invalid-{index}.png')],env=environment,capture_output=True)
        assert result.returncode==6,(forged,result.returncode,result.stderr)
print('ButtonStyle catalog: 88 actual initial states, 85 native frame sets and 11 malformed definitions checked')
