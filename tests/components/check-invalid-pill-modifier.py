#!/usr/bin/env python3
"""Require the public Text-only receiver and explicit formatting diagnostics."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
runner, imports = sys.argv[1:]
cases = [
    ('BleeckerPill {}', 'BleeckerPill requires exactly one BleeckerText caller'),
    ('BleeckerPill {Rectangle {width:20;height:10}}', 'BleeckerPill requires exactly one BleeckerText caller'),
    ('BleeckerPill {BleeckerText {text:"one"} BleeckerText {text:"two"}}', 'BleeckerPill requires exactly one BleeckerText caller'),
    ('BleeckerText {textFormat:999}', 'Unsupported BleeckerText format'),
    ('BleeckerText {maximumLineCount:0}', 'BleeckerText maximumLineCount must be a positive integer'),
]
for name in ['tracking', 'kerning', 'baselineShift']:
    for value in ['NaN', 'Infinity', '-Infinity']:
        cases.append(('BleeckerText {' + name + ':' + value + '}', 'BleeckerText spacing and baseline shift must be finite'))
for content, diagnostic in cases:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-pill-') as temporary:
        fixture = Path(temporary) / 'tst_invalid.qml'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:200;height:120\n' + content
            + '\nTestCase {when:windowShown;function test_refusal(){wait(30);fail("Invalid caller accepted")}}}')
        result = subprocess.run([runner, '-import', imports, '-input', str(fixture)], capture_output=True)
        output = result.stdout + result.stderr
        assert result.returncode != 0 and diagnostic.encode() in output, (content, result.returncode, output.decode(errors='replace'))
print('Pill/text: 14 invalid caller and formatting configurations explicitly diagnosed')
