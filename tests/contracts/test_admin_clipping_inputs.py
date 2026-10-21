import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('admin_clipping',ROOT/'scripts/verify-admin-clipping.py')
CLIPPING=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLIPPING)


class AdminClippingInputs(unittest.TestCase):
    def test_clipping_audit_retains_the_captured_colour_verifier(self):
        with contextlib.redirect_stdout(io.StringIO()):
            CLIPPING.verify()

    def test_changed_captured_colour_verifier_is_rejected(self):
        original=CLIPPING.git_bytes
        def changed(expression):
            content=original(expression)
            return content+b'\n# changed historical input\n' if expression.endswith(':scripts/verify-admin-source-colour-fixture.py') else content
        with patch.object(CLIPPING,'git_bytes',changed):
            with self.assertRaisesRegex(AssertionError,'scripts/verify-admin-source-colour-fixture.py'):
                CLIPPING.verify()


if __name__=='__main__':
    unittest.main()
