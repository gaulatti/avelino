#!/usr/bin/env python3
"""Exercise malformed Modal widths and dismissal owners through QML startup."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
runner, imports = sys.argv[1:]
cases = [('modalWidth:' + value, 'Modal width must be finite and nonnegative')
         for value in ['-1', 'NaN']]
# The proposal row consumes infinity before Component.onCompleted runs. Its
# construction guard refuses the input first, without a rendered fallback.
cases.append(('modalWidth:Infinity', 'Row maximum width must be nonnegative or -1'))
cases += [('dismissAction:' + value, 'Modal dismissal requires an action')
          for value in ['null', '42', '"close"']]
for declaration, message in cases:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-modal-') as directory:
        fixture = Path(directory) / 'tst_invalid.qml'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:500;height:300\n'
                           'BleeckerModal {title:"Review edition";' + declaration + '}\n'
                           'TestCase {when:windowShown;function test_refusal(){fail("Invalid producer accepted")}}}')
        result = subprocess.run([runner, '-import', imports, '-input', str(fixture)], capture_output=True, timeout=20)
        output = result.stdout + result.stderr
        assert result.returncode != 0 and message.encode() in output, (declaration, result.returncode, output.decode(errors='replace'))
print('Modal: six malformed width/dismissal configurations report explicit startup errors')
