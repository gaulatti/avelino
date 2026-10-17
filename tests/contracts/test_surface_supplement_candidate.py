"""Guard native failures and completeness at the evidence boundary."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('surface_supplement_candidate', ROOT / 'scripts/verify-surface-supplement-candidate.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class SurfaceSupplementCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((source.DIRECTORY / 'candidate.json').read_text())
        cls.projected = json.loads((ROOT / 'tests/consumer/native-surface-supplement-witnesses.json').read_text())
        cls.input = json.loads((source.DIRECTORY / 'runtime/surface-input-xcb-software-standard.json').read_text())
        cls.baseline = json.loads((source.DIRECTORY / 'runtime/surface-baseline-xcb-software-standard.json').read_text())

    def test_sealed_candidate_recomputes_all_native_results(self):
        self.assertEqual(source.verify(), self.report['strictComparison'])

    def reject_report(self, key, value):
        report = copy.deepcopy(self.report)
        report[key] = value
        with self.assertRaises(AssertionError):
            source.validate_report(report)

    def test_acceptance_cannot_be_forged(self):
        self.reject_report('accepted', True)

    def test_new_tolerance_is_rejected(self):
        self.reject_report('tolerance', 'one pixel')

    def test_curve_boundary_exception_cannot_be_self_approved(self):
        self.reject_report('approvedExceptions', ['curve tangencies'])

    def test_requested_baseline_gate_cannot_be_silently_closed(self):
        self.reject_report('remainingAcceptance', [g for g in source.GATES if g != 'nativeFirstBaseline'])

    def test_strict_failure_cannot_be_reported_as_success(self):
        report = copy.deepcopy(self.report)
        report['validation']['strictInputExitCode'] = 0
        with self.assertRaises(AssertionError):
            source.validate_report(report)

    def test_virtual_profiles_cannot_be_dropped(self):
        report = copy.deepcopy(self.report)
        report['validation']['virtualProfiles'] = 31
        with self.assertRaises(AssertionError):
            source.validate_report(report)

    def test_fractional_samples_cannot_be_skipped(self):
        row = copy.deepcopy(self.input)
        row['rows'][0]['modes'][0]['sequences'].pop()
        with self.assertRaises(AssertionError):
            source.validate_profile(row, 'input', self.projected)

    def test_input_failure_totals_cannot_hide_differences(self):
        row = copy.deepcopy(self.input)
        row['activationMismatches'] = 0
        with self.assertRaises(AssertionError):
            source.validate_profile(row, 'input', self.projected)

    def test_baseline_context_cannot_be_dropped(self):
        row = copy.deepcopy(self.baseline)
        row['rows'].pop()
        with self.assertRaises(AssertionError):
            source.validate_profile(row, 'baseline', self.projected)

    def test_font_guide_failure_cannot_be_marked_matching(self):
        row = copy.deepcopy(self.baseline)
        next(r for r in row['rows'] if not r['nativeGuidesMatch'])['nativeGuidesMatch'] = True
        with self.assertRaises(AssertionError):
            source.validate_profile(row, 'baseline', self.projected)

    def test_synthetic_runtime_cannot_be_claimed_as_physical(self):
        row = copy.deepcopy(self.input)
        row['physicalInputAcceptance'] = 'passed'
        with self.assertRaises(AssertionError):
            source.validate_profile(row, 'input', self.projected)


if __name__ == '__main__':
    unittest.main()
