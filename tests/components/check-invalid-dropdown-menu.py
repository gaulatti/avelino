#!/usr/bin/env python3
"""Reject malformed dropdown models and label builders in isolated processes."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

executable, imports = map(Path, sys.argv[1:])
cases = [('', 'items:42'), ('', 'items:[1]'), ('', 'items:[{}]'),
    ('QtObject {id:foreignItem;property string title:"Open"}', 'items:[foreignItem]'),
    ('BleeckerMenuItem {id:one;title:"Open"}', 'items:[one,one]'),
    ('BleeckerMenuItem {id:one;title:"Open";systemImage:42}', 'items:[one]'),
    ('', 'label:Component {QtObject {}}'), ('', 'missing-label'),
    ('', 'controlSize:"unknown"')]
with tempfile.TemporaryDirectory(prefix='avelino-dropdown-menu-invalid-') as temporary:
    for index, (objects, properties) in enumerate(cases):
        label = '' if properties in ['missing-label'] or properties.startswith('label:') else 'label:Component {BleeckerText {text:"Actions"}}\n'
        if properties == 'missing-label':
            properties = ''
        path = Path(temporary) / f'tst_invalid_{index}.qml'
        path.write_text('import QtQuick\nimport QtTest\nimport Avelino\n'
            'TestCase {when:windowShown;visible:true;width:600;height:300;'
            + objects + '\nBleeckerDropdownMenu {' + label + properties + '}'
            'function test_invalid(){wait(100)}}\n')
        result = subprocess.run([str(executable), '-input', str(path), '-import', str(imports)],
            env=dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software'), capture_output=True)
        log = (result.stdout + result.stderr).decode(errors='replace')
        assert result.returncode != 0 and any(name in log for name in ['DropdownMenu', 'MenuItem', 'Required property label']), (index, result.returncode, log)
print(f'DropdownMenu: {len(cases)} malformed inputs rejected')
