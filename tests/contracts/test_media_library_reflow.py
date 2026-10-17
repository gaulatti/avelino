"""Prevent a lifecycle correction from hiding unresolved mirror evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('media_reflow', ROOT / 'scripts/verify-media-library-reflow.py')
reflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reflow)

class MediaLibraryReflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((reflow.DIRECTORY / 'candidate.json').read_text())
    def setUp(self):
        self.report = copy.deepcopy(self.original)
    def refused(self):
        with self.assertRaises(AssertionError):
            reflow.validate_report(self.report)
    def test_complete_correction_recomputes(self):
        reflow.verify()
    def test_cannot_accept_component(self):
        self.report['accepted'] = True
        self.refused()
    def test_cannot_replace_reference(self):
        self.report['reference'] = 'other'
        self.refused()
    def test_cannot_replace_previous_candidate(self):
        self.report['previousCandidateSha256'] = 'other'
        self.refused()
    def test_cannot_claim_all_pixels_match(self):
        self.report['strictComparison']['pixelMatches'] = 1608
        self.refused()
    def test_cannot_lose_native_lifecycle_observations(self):
        self.report['strictComparison']['nativeLifecycleMatches'] = 1607
        self.refused()
    def test_cannot_claim_unobserved_sizing(self):
        self.report['strictComparison']['sizingObservations'] = 7440
        self.refused()
    def test_cannot_hide_glyph_failures(self):
        self.report['validation']['operatorExactStates'] = 24
        self.refused()
    def test_cannot_drop_raster_stability_gate(self):
        self.report['remainingAcceptance'].remove('retainedCallerRasterStability')
        self.refused()
    def test_cannot_drop_source_witness_gate(self):
        self.report['remainingAcceptance'].remove('nativeSizingAndWitnessDifference')
        self.refused()
    def test_cannot_claim_physical_display(self):
        self.report['validation']['physicalDisplay'] = True
        self.refused()
    def test_cannot_claim_hardware_acceleration(self):
        self.report['validation']['hardwareAcceleration'] = True
        self.refused()
    def test_cannot_hide_restore_failure(self):
        self.report['validation']['virtualRestorePixelMatches'] = 47
        self.refused()
    def test_cannot_accept_tolerance(self):
        self.report['tolerance'] = 'one pixel'
        self.refused()
    def test_cannot_approve_exception(self):
        self.report['approvedExceptions'] = ['glyphs']
        self.refused()
    def test_cannot_replace_expected_images(self):
        self.report['expectedImagesChanged'] = True
        self.refused()

if __name__ == '__main__':
    unittest.main()
