"""Native panel observations must retain the unresolved mirror gates."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("file_input_panel", ROOT / "scripts/verify-file-input-panel.py")
PANEL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PANEL)


class FileInputPanel(unittest.TestCase):
    def test_preserved_panel_record(self):
        PANEL.verify()

    def test_cannot_accept_unverified_gates(self):
        original = json.loads((PANEL.DIRECTORY / "investigation.json").read_text())
        for field, value in [("accepted", True), ("physicalInputAcceptance", "passed"),
                             ("readerAcceptance", "passed"), ("independentBehaviorSourceReplay", "passed"),
                             ("nativeOpenPanelRaster", "accepted"), ("expectedImagesChanged", True),
                             ("tolerance", "one pixel"), ("presentationGaps", [])]:
            with self.subTest(field=field):
                changed = copy.deepcopy(original)
                changed[field] = value
                with self.assertRaises(AssertionError):
                    PANEL.validate(changed)

    def test_cannot_omit_observed_state(self):
        changed = json.loads((PANEL.DIRECTORY / "investigation.json").read_text())
        changed["screenshots"].pop()
        with self.assertRaises(AssertionError):
            PANEL.validate(changed)


if __name__ == "__main__":
    unittest.main()
