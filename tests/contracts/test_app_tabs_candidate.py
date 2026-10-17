"""Keep app-tab evidence complete and distinguish observations from acceptance."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('app_tab_candidate', ROOT / 'scripts/verify-app-tabs-candidate.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


class AppTabsCandidate(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((candidate.DIRECTORY / 'candidate.json').read_text())

    def refused(self):
        with self.assertRaises(AssertionError):
            candidate.validate_report(self.report)

    def test_complete_candidate_recomputes(self):
        candidate.verify()

    def test_cannot_claim_acceptance(self):
        self.report['accepted'] = True
        self.refused()

    def test_cannot_hide_strict_failures(self):
        self.report['strictComparisonStatus'] = 'passed'
        self.refused()

    def test_cannot_drop_native_contexts(self):
        self.report['strictComparison']['cases'] = 1200
        self.refused()

    def test_cannot_claim_sizing(self):
        self.report['strictComparison']['sizingObservations'] = 5160
        self.refused()

    def test_cannot_claim_operator_success(self):
        self.report['validation']['operatorStatus'] = 'passed'
        self.report['validation']['operatorExactStates'] = 28
        self.refused()

    def test_cannot_hide_virtual_restore_failures(self):
        self.report['validation']['virtualRestorePixelMatches'] = 48
        self.refused()

    def test_cannot_drop_retained_raster_gate(self):
        self.report['remainingAcceptance'].remove('retainedCallerRasterStability')
        self.refused()

    def test_cannot_drop_native_accessibility_gate(self):
        self.report['remainingAcceptance'].remove('nativeAccessibility')
        self.refused()

    def test_cannot_add_tolerance(self):
        self.report['tolerance'] = 'one channel value'
        self.refused()

    def test_cannot_change_expected_images(self):
        self.report['expectedImagesChanged'] = True
        self.refused()

    def test_cannot_approve_exception(self):
        self.report['approvedExceptions'] = ['disabled raster']
        self.refused()

    def test_cannot_change_reference(self):
        self.report['reference'] = 'other'
        self.refused()

    def test_cannot_change_base(self):
        self.report['baseRevision'] = 'other'
        self.refused()

    def test_cannot_claim_physical_display(self):
        self.report['validation']['physicalDisplay'] = True
        self.refused()

    def test_cannot_omit_frozen_producer_input(self):
        binding = json.loads((candidate.DIRECTORY / 'package/artifact-binding.json').read_text())
        producer = json.loads((candidate.DIRECTORY / 'qt/inputs.json').read_text())['sourceFiles']
        candidate.validate_producer_inputs(binding, producer)
        altered = copy.deepcopy(binding)
        altered['producerCriticalFiles'].pop('src/Avelino/BleeckerAppTabBar.qml')
        with self.assertRaises(AssertionError):
            candidate.validate_producer_inputs(altered, producer)


if __name__ == '__main__':
    unittest.main()
