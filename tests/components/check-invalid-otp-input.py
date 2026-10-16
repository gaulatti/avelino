#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

runner, imports = sys.argv[1:]
cases = [
    ('code:"";length:-1', 'length must be a nonnegative safe integer'),
    ('code:"";length:1.25', 'length must be a nonnegative safe integer'),
    ('code:"";length:NaN', 'length must be a nonnegative safe integer'),
    ('code:"";length:Infinity', 'length must be a nonnegative safe integer'),
    ('code:"";length:9007199254740992', 'length must be a nonnegative safe integer'),
    ('code:"\\ud800"', 'requires valid Unicode scalars'),
    ('code:"\\udc00"', 'requires valid Unicode scalars'),
    ('code:"1\\ud800";length:0', 'requires valid Unicode scalars'),
]
for declaration, message in cases:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-otp-input-') as directory:
        fixture = Path(directory) / 'tst_invalid.qml'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:300;height:100\n'
                           'BleeckerOTPInput {' + declaration + '}\n'
                           'TestCase {when:windowShown;function test_refusal(){wait(20);fail("Invalid producer accepted")}}}')
        result = subprocess.run([runner, '-import', imports, '-input', str(fixture)], capture_output=True, timeout=20)
        output = result.stdout + result.stderr
        assert result.returncode < 0 and message.encode() in output, (declaration, result.returncode, output.decode(errors='replace'))
print('OTP input: eight malformed producer getter/length configurations refused at construction')
