#!/usr/bin/env python3
"""Refuse invalid style variants, sizes and width proposals."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE,(0,0))
runner,imports=sys.argv[1:]
cases=[('variant:"unknown"','Unknown Bleecker button variant'),('size:"unknown"','Unknown Bleecker button size'),
       ('widthOffer:-2','ButtonStyle width offer must be nonnegative or -1'),
       ('maximumWidth:-2','ButtonStyle maximum width must be nonnegative or -1'),
       ('widthOffer:NaN','ButtonStyle width offer must be nonnegative or -1'),
       ('maximumWidth:Infinity','ButtonStyle maximum width must be nonnegative or -1')]
for properties,message in cases:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-button-style-') as temporary:
        fixture=Path(temporary)/'tst_invalid.qml'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:400;height:240\nBleeckerButtonStyle {'+properties+'}\nTestCase {when:windowShown;function test_refusal(){wait(30);fail("Invalid style accepted")}}}')
        result=subprocess.run([runner,'-import',imports,'-input',str(fixture)],capture_output=True)
        output=result.stdout+result.stderr
        assert result.returncode!=0 and message.encode() in output,(properties,result.returncode,output.decode(errors='replace'))
print('ButtonStyle: six invalid public configurations explicitly rejected')
