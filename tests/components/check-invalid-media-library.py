#!/usr/bin/env python3
"""Reject malformed caller data, identifiers, tiles and layout measurements."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

executable, imports = map(Path, sys.argv[1:])
cases = [
    'items:42', 'items:[1]', 'items:[{height:20}]',
    'items:[{id:undefined}]', 'items:[{id:{key:"a"}}]',
    'items:[{id:"é"},{id:"é"}]',
    'items:[{id:1},{id:1}]', 'itemIdentity:42',
    'items:[{id:"a"}];itemIdentity:(value)=>({key:value.id})',
    'minimumTileWidth:-16;items:[{id:"a"}]',
    'tile:Component {QtObject {}} items:[{id:"a"}]',
    'tile:Component {Item {implicitHeight:-1}} items:[{id:"a"}]',
    'tile:Component {Item {implicitWidth:NaN}} items:[{id:"a"}]',
]
with tempfile.TemporaryDirectory(prefix='avelino-media-invalid-') as temporary:
    folder = Path(temporary)
    for index, properties in enumerate(cases):
        tile = '' if 'tile:' in properties else 'tile:Component {Item {implicitWidth:10;implicitHeight:20}} '
        path = folder / f'tst_invalid_{index}.qml'
        path.write_text('import QtQuick\nimport QtTest\nimport Avelino\n'
            'TestCase {when:windowShown;visible:true;width:640;height:400;'
            'BleeckerMediaLibrary {width:460;' + tile + properties + '}'
            'function test_invalid(){wait(100)}}\n')
        result = subprocess.run([str(executable), '-input', str(path), '-import', str(imports)],
            env=dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software'), capture_output=True)
        log = (result.stdout + result.stderr).decode(errors='replace')
        assert result.returncode != 0 and 'MediaLibrary' in log, (index, result.returncode, log)
print(f'MediaLibrary: {len(cases)} malformed configurations rejected explicitly')
