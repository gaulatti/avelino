#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

runner, imports = sys.argv[1:]
for value in ['-2', 'NaN', 'Infinity']:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-activity-') as temporary:
        fixture = Path(temporary) / 'tst_invalid.qml'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:300;height:100\n'
                           'BleeckerActivityItem {title:"Title";detail:"Detail";timestamp:"Now";maximumWidth:' + value + '}\n'
                           'TestCase {when:windowShown;function test_refusal(){wait(20);fail("Invalid proposal accepted")}}}')
        result = subprocess.run([runner, '-import', imports, '-input', str(fixture)], capture_output=True, timeout=20)
        output = result.stdout + result.stderr
        assert result.returncode < 0 and b'Text maximum width must be nonnegative or -1' in output, (value, result.returncode, output.decode(errors='replace'))
print('ActivityItem: three malformed width proposals refused at construction')
