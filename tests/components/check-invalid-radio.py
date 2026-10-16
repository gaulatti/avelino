#!/usr/bin/env python3
"""Reject malformed RadioGroup producers and ambiguous option identities."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
runner, imports = sys.argv[1:]
cases = [
    ('options: 3', 'options must be an array'),
    ('options: ["Daily"]', 'options require value and string label'),
    ('options: [{label:"Daily"}]', 'options require value and string label'),
    ('options: [{value:"daily",label:3}]', 'options require value and string label'),
    ('options: [{value:"daily",label:"Daily",disabled:null}]', 'disabled flags must be Boolean'),
    ('options: [{value:"daily",label:"Daily",disabled:1}]', 'disabled flags must be Boolean'),
    ('options: [{value:"é",label:"One"},{value:"e\\u0301",label:"Two"}]', 'distinct stable value identities'),
    ('options: [{value:0,label:"One"},{value:-0,label:"Two"}]', 'distinct stable value identities'),
    ('options: [{value:({key:1}),label:"Object"}]', 'values require primitive identity'),
    ('valueIdentity: 1', 'valueIdentity must be a function or null'),
    ('valueIdentity: value => ({key:value})', 'values require primitive identity'),
    ('valueIdentity: value => {throw new Error("invalid")}', 'valueIdentity callback failed'),
    ('selection: "\\ud800"', 'requires valid Unicode scalars'),
    ('orientation: 3', 'orientation must be Qt.Horizontal or Qt.Vertical'),
    ('maximumWidth: -2', 'maximum width must be nonnegative or -1'),
]
for declaration, message in cases:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-radio-') as directory:
        fixture = Path(directory) / 'tst_invalid.qml'
        selection = '' if declaration.startswith('selection:') else 'selection: "daily";'
        options = '' if declaration.startswith('options:') else 'options: [{value:"daily",label:"Daily"}];'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:300;height:100\nBleeckerRadioGroup {' + selection + options + declaration + '}\nTestCase {when:windowShown;function test_refusal(){wait(20);fail("Invalid producer accepted")}}}')
        result = subprocess.run([runner, '-import', imports, '-input', str(fixture)], capture_output=True, timeout=20)
        output = result.stdout + result.stderr
        assert result.returncode < 0 and message.encode() in output, (declaration, result.returncode, output.decode(errors='replace'))
print('RadioGroup: 15 malformed producer and ambiguous identity configurations refused')
