#!/usr/bin/env python3
"""Exercise malformed caller data and row builders in isolated Qt processes."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

executable, imports = map(Path, sys.argv[1:])
cases = ['items:42', 'items:[1]', 'items:[{}]', 'items:[{id:undefined}]',
    'items:[{id:{key:"a"}}]', 'items:[{id:[]}]', 'items:[{id:()=>0}]',
    'items:[{id:"é"},{id:"é"}]', 'itemIdentity:42',
    'itemIdentity:value=>({key:value.id});items:[{id:"a"}]',
    'itemIdentity:value=>{throw new Error("invalid identity")};items:[{id:"a"}]',
    'row:Component {QtObject {}};items:[{id:"a"}]',
    'row:Component {Item {implicitWidth:NaN}};items:[{id:"a"}]',
    'row:Component {Item {implicitWidth:10;implicitHeight:-1}};items:[{id:"a"}]']
with tempfile.TemporaryDirectory(prefix='avelino-command-spotlight-invalid-') as temporary:
    for index, properties in enumerate(cases):
        properties = properties.replace('};items:', '}\nitems:')
        row = '' if 'row:' in properties else 'row:Component {Item {implicitWidth:10;implicitHeight:20}}\n'
        path = Path(temporary) / f'tst_invalid_{index}.qml'
        path.write_text('import QtQuick\nimport QtTest\nimport Avelino\n'
            'TestCase {when:windowShown;visible:true;width:720;height:520;'
            'BleeckerCommandSpotlight {query:"";' + row + properties + '}'
            'function test_invalid(){wait(100)}}\n')
        result = subprocess.run([str(executable), '-input', str(path), '-import', str(imports)],
            env=dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software'), capture_output=True)
        log = (result.stdout + result.stderr).decode(errors='replace')
        assert result.returncode != 0 and 'CommandSpotlight' in log, (index, result.returncode, log)
print(f'CommandSpotlight: {len(cases)} malformed caller inputs rejected')
