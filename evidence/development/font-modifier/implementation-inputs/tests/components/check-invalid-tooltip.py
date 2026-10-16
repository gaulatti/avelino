#!/usr/bin/env python3
"""Reject missing Tooltip producers and conflicting accessible help owners."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE,(0,0))
runner,imports=sys.argv[1:]
cases=[('BleeckerTooltip {text:"Hint"}','Required property target was not initialized'),
       ('BleeckerTooltip {target:null}','Required property text was not initialized'),
       ('Rectangle {id:caller;width:80;height:40;Accessible.role:Accessible.Button}\n'
        'BleeckerTooltip {target:caller;text:"First"}\nBleeckerTooltip {target:caller;text:"Second"}',
        'A Tooltip accessible target cannot have multiple help owners')]
for declaration,message in cases:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-tooltip-') as temporary:
        fixture=Path(temporary)/'tst_invalid.qml'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:400;height:240\n'+declaration+'\nTestCase {when:windowShown;function test_refusal(){wait(30);fail("Invalid help producer accepted")}}}')
        result=subprocess.run([runner,'-import',imports,'-input',str(fixture)],capture_output=True,timeout=20)
        output=result.stdout+result.stderr
        assert result.returncode!=0 and message.encode() in output,(declaration,result.returncode,output.decode(errors='replace'))
print('Tooltip: missing target/text and conflicting accessible owners are explicitly rejected')
