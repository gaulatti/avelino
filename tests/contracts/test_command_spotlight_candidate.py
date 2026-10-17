"""Protect the complete evidence corpus and the remaining mirror gates."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('spotlight_candidate', ROOT / 'scripts/verify-command-spotlight-candidate.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


class CommandSpotlightCandidate(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((candidate.DIRECTORY / 'report.json').read_text())

    def refused(self):
        with self.assertRaises(AssertionError):
            candidate.validate_report(self.report)

    def test_complete_candidate_recomputes(self):
        candidate.verify()

    def test_cannot_claim_acceptance(self):
        self.report['accepted'] = True
        self.refused()

    def test_cannot_drop_native_contexts(self):
        self.report['strictComparison']['cases'] = 1791
        self.refused()

    def test_cannot_approve_tolerance(self):
        self.report['tolerance'] = 'one channel value'
        self.refused()

    def test_cannot_drop_input_timing_gate(self):
        self.report['remainingAcceptance'].remove('nativeQueryCallbackAndFocusTiming')
        self.refused()

    def test_cannot_claim_physical_display(self):
        self.report['validation']['physicalDisplay'] = True
        self.refused()

    def test_cannot_replace_expected_images(self):
        self.report['expectedImagesChanged'] = True
        self.refused()

    def test_cannot_hide_virtual_restore_failures(self):
        self.report['validation']['virtualRestoreMatchesNative'] = 64
        self.refused()


if __name__ == '__main__':
    unittest.main()
