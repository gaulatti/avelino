#!/usr/bin/env python3
"""Exercise invalid sidebar/brand proposals through actual QML startup."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
runner,imports=sys.argv[1:]
cases=[('BleeckerBrandMark {size:'+value+'}',b'Brand size must be finite and nonnegative') for value in ['-1','Number.NaN','Number.POSITIVE_INFINITY']]
cases.append(('BleeckerBrandLockup {name:"Bleecker";maximumWidth:-2}',b'Text maximum width must be nonnegative or -1'))
cases.append(('BleeckerSidebarItem {title:"Editions";selected:false;maximumWidth:-2;icon:Component {Item {implicitWidth:20;implicitHeight:18}}}',b'Text maximum width must be nonnegative or -1'))
for declaration,expected in cases:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-sidebar-brand-') as folder:
        path=Path(folder)/'tst_invalid.qml'
        path.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:400;height:300\n'+declaration+'\nTestCase {when:windowShown;function test_refusal(){fail("Invalid proposal accepted")}}}')
        result=subprocess.run([runner,'-import',imports,'-input',str(path)],capture_output=True)
        assert result.returncode!=0 and expected in result.stdout+result.stderr,(declaration,result.stdout+result.stderr)
print('Sidebar/brand startup refused five invalid size and width proposals')
