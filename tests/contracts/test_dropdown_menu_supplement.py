"""Keep native diagnostics distinct from Linux and physical acceptance."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('dropdown_supplement', ROOT / 'scripts/verify-dropdown-menu-supplement.py')
supplement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supplement)


class DropdownMenuSupplement(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((supplement.DIRECTORY / 'investigation.json').read_text())

    def test_complete_replay_recomputes(self):
        supplement.verify()

    def test_no_acceptance(self):
        self.report['accepted'] = True
        with self.assertRaises(AssertionError):
            supplement.validate_report(self.report)

    def test_no_hidden_replay_differences(self):
        self.report['exactFiles'] = 62
        with self.assertRaises(AssertionError):
            supplement.validate_report(self.report)

    def test_no_pixel_tolerance(self):
        self.report['tolerance'] = '15 pixels'
        with self.assertRaises(AssertionError):
            supplement.validate_report(self.report)

    def test_physical_input_gate_required(self):
        self.report['remainingAcceptance'].remove('physicalPointerKeyboard')
        with self.assertRaises(AssertionError):
            supplement.validate_report(self.report)


if __name__ == '__main__':
    unittest.main()
