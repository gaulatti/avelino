#!/usr/bin/env python3
"""Refuse malformed caller breadcrumb data through actual QML startup."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
runner, imports = sys.argv[1:]
cases = [
    ('BleeckerBreadcrumb {items:({title:"Home"})}', b'Breadcrumb items must be an array'),
    ('BleeckerBreadcrumb {items:[{title:3}]}', b'Breadcrumb items require string titles'),
    ('BleeckerBreadcrumb {items:[{title:"Home",icon:"house"}]}', b'Breadcrumb item icons must be Components or null'),
    ('BleeckerBreadcrumb {items:[];maximumWidth:-2}', b'Text maximum width must be nonnegative or -1'),
    ('ProposalRow {Item {implicitWidth:10;BleeckerLayout.minimumWidth:20}}', b'Content layout requires finite widths'),
]
for declaration, expected in cases:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-navigation-') as directory:
        path = Path(directory) / 'tst_invalid.qml'
        path.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:400;height:300\n' + declaration +
                        '\nTestCase {when:windowShown;function test_refusal(){fail("Invalid navigation was accepted")}}}')
        result = subprocess.run([runner, '-import', imports, '-input', str(path)], capture_output=True)
        assert result.returncode != 0 and expected in result.stdout + result.stderr, (declaration, result.stdout + result.stderr)
print('Navigation startup refused five malformed model, icon and layout inputs')
