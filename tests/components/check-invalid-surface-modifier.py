#!/usr/bin/env python3
"""Require explicit diagnostics for nonfinite Linux modifier radii."""
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
runner, imports = sys.argv[1:]
for radius in ["NaN", "Infinity", "-Infinity"]:
    with tempfile.TemporaryDirectory(prefix="avelino-invalid-surface-") as temporary:
        fixture = Path(temporary) / "tst_invalid.qml"
        fixture.write_text(
            "import QtQuick\nimport QtTest\nimport Avelino\n"
            "Item {width:200;height:120\nBleeckerSurfaceModifier {radius:"
            + radius
            + ";Rectangle {width:96;height:64}}\n"
            'TestCase {when:windowShown;function test_refusal(){wait(30);fail("Invalid radius accepted")}}}'
        )
        result = subprocess.run([runner, "-import", imports, "-input", str(fixture)], capture_output=True)
        output = result.stdout + result.stderr
        assert result.returncode != 0 and b"BleeckerSurfaceModifier radius must be finite" in output, (
            radius, result.returncode, output.decode(errors="replace")
        )
print("Surface modifier: three nonfinite radii explicitly diagnosed; native nonfinite equivalence remains pending")
