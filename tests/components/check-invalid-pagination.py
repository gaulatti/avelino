#!/usr/bin/env python3
"""Exercise invalid pagination integer configuration through isolated real QML startup."""
from pathlib import Path
import subprocess
import resource
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
runner, imports = sys.argv[1:]
for declaration in ['page: 9007199254740992; pageCount: 9', 'page: 1.25; pageCount: 8', 'page: Number.NaN; pageCount: 8', 'page: true; pageCount: 8', 'page: "9223372036854775808"; pageCount: "9"', 'page: "-9223372036854775809"; pageCount: "9"', 'page: "01"; pageCount: "8"', 'page: "4"; pageCount: " 8"']:
    with tempfile.TemporaryDirectory(prefix='avelino-invalid-pagination-') as directory:
        fixture = Path(directory) / 'tst_invalid.qml'
        fixture.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem { width: 1000; height: 100\n'
            + 'BleeckerPagination { ' + declaration + ' }\n'
            + 'TestCase { when: windowShown; function test_refusal() { fail("Invalid pagination integer was accepted") } }\n}')
        result = subprocess.run([runner, '-import', imports, '-input', str(fixture)], capture_output=True)
        assert result.returncode != 0, declaration
        assert b'Pagination requires signed 64-bit integers' in result.stdout+result.stderr, declaration
print('Pagination startup refused unsafe/fractional/non-finite/bool numbers, out-of-range and noncanonical decimal strings')
