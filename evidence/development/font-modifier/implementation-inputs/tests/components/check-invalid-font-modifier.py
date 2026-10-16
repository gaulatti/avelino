#!/usr/bin/env python3
"""Refuse unsupported font families, weights and nonfinite size products."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
runner,imports=sys.argv[1:]
cases=[('family:"unknown";size:14','Unknown Bleecker font family'),
 ('family:"primary";size:14;weight:"unknown"','Unknown Bleecker font weight'),
 ('family:"primary";size:NaN','finite size'),('family:"mono";size:Infinity','finite size'),
 ('family:"secondary";size:14;textScale:Infinity','finite size')]
for properties,message in cases:
 with tempfile.TemporaryDirectory(prefix='avelino-invalid-font-') as temporary:
  fixture=Path(temporary)/'tst_invalid.qml'
  fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:400;height:240\nBleeckerFont {'+properties+';BleeckerText {text:"Keep edition"}}\nTestCase {when:windowShown;function test_refusal(){wait(30);fail("Invalid font accepted")}}}')
  result=subprocess.run([runner,'-import',imports,'-input',str(fixture)],capture_output=True)
  output=result.stdout+result.stderr
  assert result.returncode!=0 and message.encode() in output,(properties,result.returncode,output.decode(errors='replace'))
print('Font modifier: five invalid public configurations explicitly rejected; nonfinite native Text equivalence remains pending')
