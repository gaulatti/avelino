import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('admin_colour_fixture',ROOT/'scripts/verify-admin-source-colour-fixture.py')
FIXTURE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURE)


class AdminColourFixture(unittest.TestCase):
    def test_recorded_fixture_survives_later_packaging_changes(self):
        FIXTURE.verify()

    def test_changed_recorded_packaging_bytes_are_rejected(self):
        original=FIXTURE.source_bytes
        def changed(name):
            content=original(name)
            return content+b'\n# changed producer input\n' if name=='scripts/check-linux.sh' else content
        with patch.object(FIXTURE,'source_bytes',side_effect=changed):
            with self.assertRaises(AssertionError):
                FIXTURE.verify()


if __name__=='__main__':
    unittest.main()
