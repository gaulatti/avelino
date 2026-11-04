import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('qt_rectangle_context',ROOT/'scripts/verify-qt-rectangle-build-context.py')
CONTEXT=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTEXT)


class QtRectangleBuildContext(unittest.TestCase):
    def test_recorded_copy_audit_survives_later_dependency_changes(self):
        self.assertEqual(CONTEXT.verify()['exportedCopyInputs'],12)

    def test_additional_live_copy_is_rejected(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            content=original(path,*args,**kwargs)
            return content+'\nCOPY tools/unrecorded /extra\n' if path==ROOT/'tools/Dockerfile' else content
        with patch.object(Path,'read_text',changed):
            with self.assertRaises(AssertionError):
                CONTEXT.verify()


if __name__=='__main__':
    unittest.main()
