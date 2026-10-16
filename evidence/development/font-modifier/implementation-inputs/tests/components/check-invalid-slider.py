#!/usr/bin/env python3
"""Exercise invalid slider configuration through isolated real QML startup."""
from pathlib import Path
import subprocess
import resource
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
runner, imports = sys.argv[1:]
for declaration in ['from: 1; to: 0', 'stepSize: -1', 'from: Number.NaN']:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-slider-') as directory:
        fixture = Path(directory) / 'tst_invalid.qml'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem { width: 400; height: 100\n'
            + 'BleeckerSlider { ' + declaration + ' }\n'
            + 'TestCase { when: windowShown; function test_refusal() { fail("Invalid slider was accepted") } }\n}')
        result = subprocess.run([runner, '-import', imports, '-input', str(fixture)], capture_output=True)
        assert result.returncode != 0, declaration
        assert b'Slider requires finite ascending bounds and nonnegative stepSize' in result.stdout+result.stderr, declaration
print('Slider startup refused reversed bounds, negative steps and non-finite bounds')
