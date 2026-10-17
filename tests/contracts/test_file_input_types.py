"""Fresh native selection cannot approve retained or physical FileInput parity."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('file_input_types', ROOT / 'scripts/verify-file-input-types.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class FileInputTypes(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((source.DIRECTORY / 'investigation.json').read_text())

    def test_native_supplement_recomputes(self):
        source.verify()

    def test_fresh_process_does_not_accept_retained_updates(self):
        self.report['retainedTypeUpdateAcceptance'] = 'passed'
        with self.assertRaises(AssertionError):
            source.validate_report(self.report)

    def test_recorded_library_is_not_an_independent_behavior_source_replay(self):
        self.report['freshSourceBehaviorReplay'] = 'passed'
        with self.assertRaises(AssertionError):
            source.validate_report(self.report)

    def test_normal_native_ui_is_not_physical_input_acceptance(self):
        self.report['physicalInputAcceptance'] = 'passed'
        with self.assertRaises(AssertionError):
            source.validate_report(self.report)

    def test_cannot_approve_linux_from_native_type_probes(self):
        self.report['accepted'] = True
        with self.assertRaises(AssertionError):
            source.validate_report(self.report)


if __name__ == '__main__':
    unittest.main()
