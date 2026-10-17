#!/usr/bin/env python3
"""Exercise every installed chart fixture and reject malformed definitions."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog,imports,root=map(Path,sys.argv[1:])
projection=json.loads((root/'tests/consumer/native-chart-witnesses.json').read_text())
apis=dict(line='BleeckerLineChart',bar='BleeckerBarChart',pie='BleeckerPieChart',scatter='BleeckerScatterChart',sparkline='BleeckerSparkline')
rows=[r for r in projection['closed']+projection['edges'] if (r['appearance'],r['textScale'],r['dpr'])==('light',1,1)]
assert len(rows)==170
definitions=[]
for row in rows:
    f=row['configuration']
    definitions.append(dict(f,api=apis[f['kind']],source=projection['reference'],fixture='chart-'+f['id'],chartWidth=f['width'],chartHeight=f['height'],width=640,height=400))
with tempfile.TemporaryDirectory(prefix='avelino-chart-catalog-') as temporary:
    folder=Path(temporary);inputs=folder/'fixtures.json';inputs.write_text(json.dumps(dict(fixtures=definitions),ensure_ascii=False))
    environment=dict(os.environ,QML_IMPORT_PATH=str(imports),QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1')
    def run(definition):
        image=folder/(definition['fixture']+'.png');result=subprocess.run([str(catalog),'--fixture','reference-case','--case',definition['fixture'],'--case-definitions',str(inputs),'--capture',str(image)],env=environment,capture_output=True)
        log=(result.stdout+result.stderr).decode(errors='replace');assert result.returncode==0,(definition['id'],result.returncode,log)
        assert not any(x in log for x in ['Unable to assign','ReferenceError','TypeError','Error:','Binding loop','QFont::']), (definition['id'],log)
        meta=json.loads(Path(str(image)+'.json').read_text());assert meta['chartState']==dict(appearances=1,disappearances=0,wrapperInstances=1)
        frame=meta['chartFrame'];assert frame['width']==max(1,definition['chartWidth']) and frame['height']==max(1,definition['chartHeight'])
        assert meta['chartMetrics']['kind']==definition['kind'] and meta['chartMetrics']['nativeRasterAcceptance']=='pending'
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(run,definitions))
    base=definitions[0];invalid=[dict(base,chartWidth=-1),dict(base,chartHeight='100'),dict(base,source='unapproved'),dict(base,kind='pie'),dict(base,width=320),dict(base,points='values'),dict(base,values={}),dict(base,area=1),dict(base,innerRadius='NaN'),dict(base,extra=True),dict(base,points=[dict(x=0,y='1',id='a',series='Value',label='')])]
    for key in base:
        if key=='api':continue
        value=dict(base);del value[key];invalid.append(value)
    for index,value in enumerate(invalid):
        inputs.write_text(json.dumps(dict(fixtures=[value])));result=subprocess.run([str(catalog),'--fixture','reference-case','--case',base['fixture'],'--case-definitions',str(inputs),'--capture',str(folder/f'invalid-{index}.png')],env=environment,capture_output=True)
        assert result.returncode==6,(value,result.returncode,result.stderr.decode(errors='replace'))
print(f'Charts catalog: 170 source inputs and {len(invalid)} malformed definitions; native parity pending')
