"""Keep candidate coverage distinct from native parity acceptance."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('dropdown_candidate', ROOT / 'scripts/verify-dropdown-menu-candidate.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


class DropdownMenuCandidate(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((candidate.DIRECTORY / 'report.json').read_text())

    def test_complete_candidate_recomputes(self):
        candidate.verify()

    def test_no_acceptance(self):
        self.report['accepted'] = True
        with self.assertRaises(AssertionError):
            candidate.validate_report(self.report)

    def test_no_context_removed(self):
        self.report['strictComparison']['cases'] = 255
        with self.assertRaises(AssertionError):
            candidate.validate_report(self.report)

    def test_no_tolerance_approved(self):
        self.report['tolerance'] = 'one pixel'
        with self.assertRaises(AssertionError):
            candidate.validate_report(self.report)

    def test_physical_gate_required(self):
        self.report['remainingAcceptance'].remove('physicalInputDisplay')
        with self.assertRaises(AssertionError):
            candidate.validate_report(self.report)

    def test_no_physical_display_claim(self):
        self.report['validation']['physicalDisplay'] = True
        with self.assertRaises(AssertionError):
            candidate.validate_report(self.report)


if __name__ == '__main__':
    unittest.main()
