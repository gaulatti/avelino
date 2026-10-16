#!/usr/bin/env python3
"""Exercise the public QML OTP transformation boundary with malformed producers."""
from pathlib import Path
import subprocess
import sys
import tempfile

runner, imports = sys.argv[1:]
cases = [
    ('"12", -1', 'length must be a nonnegative safe integer'),
    ('"12", 1.5', 'length must be a nonnegative safe integer'),
    ('"12", NaN', 'length must be a nonnegative safe integer'),
    ('"12", Infinity', 'length must be a nonnegative safe integer'),
    ('"12", 9007199254740992', 'length must be a nonnegative safe integer'),
    ('"\\ud800", 6', 'requires valid Unicode scalars'),
    ('"\\udc00", 6', 'requires valid Unicode scalars'),
    ('"1\\ud800", 1', 'requires valid Unicode scalars'),
    ('"\\ud800", 0', 'requires valid Unicode scalars'),
]
for method in ['filter', 'validate']:
    for arguments, message in cases:
        with tempfile.TemporaryDirectory(prefix='avelino-invalid-otp-') as directory:
            fixture = Path(directory) / 'tst_invalid.qml'
            fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:300;height:100\n'
                               'TestCase {when:windowShown;function test_refusal(){BleeckerOTPTools.' +
                               method + '(' + arguments + ');fail("Invalid producer accepted")}}}')
            result = subprocess.run([runner, '-import', imports, '-input', str(fixture)], capture_output=True, timeout=20)
            output = result.stdout + result.stderr
            assert result.returncode < 0 and message.encode() in output, (method, arguments, result.returncode, output.decode(errors='replace'))
print('OTP transformation: 18 malformed Unicode/length inputs refused through the public QML singleton')
