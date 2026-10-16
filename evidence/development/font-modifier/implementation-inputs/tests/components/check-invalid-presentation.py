#!/usr/bin/env python3
"""Refuse invalid text layout proposals through actual QML startup."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
runner, imports = sys.argv[1:]
cases = [('BleeckerButton { text: "Create"; maximumWidth: '+value+' }',
          b'Text maximum width must be nonnegative or -1') for value in ['-2', 'Number.NaN', 'Number.POSITIVE_INFINITY']]
cases.append(('ButtonLabel { text: "Message"; horizontalAlignment: Qt.AlignJustify }',
              b'Label horizontal alignment must be left, center or right'))
cases.append(('BleeckerLoadingSpinner { size: "unknown" }', b'Unknown Bleecker loading-spinner size'))
cases.append(('BleeckerAlert { title: "Review"; content: null; type: "unknown" }', b'Unknown Bleecker alert type'))
for value in ['-2','Number.NaN','Number.POSITIVE_INFINITY']:
    cases.append(('BleeckerAlert { title: "Review"; content: null; maximumWidth: '+value+' }',b'Text maximum width must be nonnegative or -1'))
for declaration, expected in cases:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-presentation-') as directory:
        path = Path(directory) / 'tst_invalid.qml'
        path.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem { width:400; height:300\n'+declaration+
                        '\nTestCase { when:windowShown; function test_refusal() { fail("Invalid layout was accepted") } } }')
        result = subprocess.run([runner, '-import', imports, '-input', str(path)], capture_output=True)
        assert result.returncode != 0 and expected in result.stdout+result.stderr, (declaration, result.stdout+result.stderr)
print('Presentation startup refused nine invalid button/alert proposals, alignment, spinner size and alert type inputs')
