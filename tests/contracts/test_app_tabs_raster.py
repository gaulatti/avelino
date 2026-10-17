"""Keep a successful local raster repair separate from mirror acceptance."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('app_tab_raster', ROOT / 'scripts/verify-app-tabs-raster.py')
raster = importlib.util.module_from_spec(spec)
spec.loader.exec_module(raster)


class AppTabRasterEvidence(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((raster.DIRECTORY / 'candidate.json').read_text())

    def refused(self):
        with self.assertRaises(AssertionError):
            raster.validate_report(self.report)

    def test_local_fix_is_not_native_acceptance(self):
        self.report['accepted'] = True
        self.refused()

    def test_cannot_hide_native_pixel_failures(self):
        self.report['strictComparison']['pixelMatches'] = 1208
        self.refused()

    def test_cannot_invent_sizing_results(self):
        self.report['strictComparison']['sizingObservations'] = 5160
        self.refused()

    def test_cannot_skip_second_pixel_ratio(self):
        self.report['validation']['dprs'] = [1]
        self.refused()

    def test_cannot_replace_physical_input_with_xtest(self):
        self.report['validation']['physicalDisplay'] = True
        self.refused()

    def test_cannot_relax_the_failed_native_comparison(self):
        self.report['tolerance'] = 'one channel value'
        self.refused()


if __name__ == '__main__':
    unittest.main()
