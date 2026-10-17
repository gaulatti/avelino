#!/usr/bin/env python3
"""Invalid data shapes fail explicitly; numeric non-finite inputs remain supported."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

executable,imports=map(Path,sys.argv[1:])
cases=[('BleeckerLineChart','points:42'),('BleeckerLineChart','points:[1]'),('BleeckerLineChart','points:[{x:0}]'),('BleeckerBarChart','points:[{x:0,y:"1"}]'),('BleeckerPieChart','points:[{x:0,y:1,series:4}]'),('BleeckerScatterChart','points:[{x:true,y:1}]'),('BleeckerSparkline','values:"1,2"'),('BleeckerSparkline','values:[1,"2"]')]
with tempfile.TemporaryDirectory(prefix='avelino-chart-invalid-') as temporary:
    folder=Path(temporary)
    for index,(kind,properties) in enumerate(cases):
        path=folder/f'tst_invalid_{index}.qml';path.write_text('import QtQuick\nimport QtTest\nimport Avelino\nTestCase {when:windowShown; '+kind+' { '+properties+' } function test_invalid(){wait(10)} }\n')
        result=subprocess.run([str(executable),'-input',str(path),'-import',str(imports)],env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'),capture_output=True)
        log=(result.stdout+result.stderr).decode(errors='replace');assert result.returncode!=0 and any(s in log for s in ['Chart','Sparkline']),(index,result.returncode,log)
print('Charts: eight invalid input shapes rejected; numeric NaN and infinities are separate source cases')
