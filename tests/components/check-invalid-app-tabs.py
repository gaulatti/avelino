#!/usr/bin/env python3
"""Reject malformed native tab data, lossy integers and invalid visual slots."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

executable, imports = map(Path, sys.argv[1:])
cases = [
    'tabs:42', 'tabs:[1]', 'tabs:[{value:"a",label:"Home"}]',
    'tabs:[{value:undefined,label:"Home",systemImage:"house"}]',
    'tabs:[{value:{id:"a"},label:"Home",systemImage:"house"}]',
    'tabs:[{value:"é",label:"A",systemImage:"house"},{value:"é",label:"B",systemImage:"house"}]',
    'valueIdentity:42',
    'valueIdentity:value=>({id:value});tabs:[{value:"a",label:"Home",systemImage:"house"}]',
    'tabs:[{value:"a",label:"Home",systemImage:"house",disabled:"false"}]',
    'tabs:[{value:"a",label:"Home",systemImage:"house",accessibilityLabel:true}]',
    'tabs:[{value:"a",label:"Home",systemImage:"house",badge:0.5}]',
    'tabs:[{value:"a",label:"Home",systemImage:"house",badge:9007199254740992}]',
    'tabs:[{value:"a",label:"Home",systemImage:"house",badge:"01"}]',
    'tabs:[{value:"a",label:"Home",systemImage:"house",badge:"9223372036854775808"}]',
    'width:Infinity',
    'icon:Component {QtObject {}} tabs:[{value:"a",label:"Home",systemImage:"house"}]',
    'icon:Component {Item {implicitWidth:NaN}} tabs:[{value:"a",label:"Home",systemImage:"house"}]',
    'icon:Component {Item {implicitHeight:-1}} tabs:[{value:"a",label:"Home",systemImage:"house"}]',
]
with tempfile.TemporaryDirectory(prefix='avelino-app-tabs-invalid-') as temporary:
    folder = Path(temporary)
    for index, properties in enumerate(cases):
        icon = '' if 'icon:' in properties else 'icon:Component {Item {implicitWidth:24;implicitHeight:24}} '
        width = '' if 'width:' in properties else 'width:300;'
        path = folder / f'tst_invalid_{index}.qml'
        path.write_text('import QtQuick\nimport QtTest\nimport Avelino\n'
            'TestCase {when:windowShown;visible:true;width:640;height:400;'
            'BleeckerAppTabBar {selection:"a";' + width + icon + properties + '}'
            'function test_invalid(){wait(100)}}\n')
        result = subprocess.run([str(executable), '-input', str(path), '-import', str(imports)],
            env=dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software'), capture_output=True)
        log = (result.stdout + result.stderr).decode(errors='replace')
        assert result.returncode != 0 and 'AppTabBar' in log, (index, result.returncode, log)
print(f'AppTabBar: {len(cases)} malformed configurations rejected explicitly')
