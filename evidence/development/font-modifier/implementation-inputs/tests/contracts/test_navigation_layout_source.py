import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("navigation_source", ROOT / "scripts/verify-navigation-layout-source.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class NavigationSourceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "source"
        shutil.copytree(verifier.DIRECTORY, self.directory)

    def change(self, name, operation):
        path = self.directory / name
        data = json.loads(path.read_text())
        operation(data)
        path.write_text(json.dumps(data))
        report = self.directory / "investigation.json"
        data = json.loads(report.read_text())
        data["files"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        report.write_text(json.dumps(data))

    def test_public_component_instrumentation_cannot_change_pixels(self):
        self.change("captures.json", lambda m: m["captures"][0].update(instrumentedPngByteIdentical=False))
        with self.assertRaisesRegex(AssertionError, "instrumentation identity"):
            verifier.verify(self.directory)

    def test_reconstructed_layout_cannot_replace_the_public_source(self):
        self.change("captures.json", lambda m: m["captures"][0].update(layoutWitnessPngByteIdentical=False))
        with self.assertRaisesRegex(AssertionError, "layout witness identity"):
            verifier.verify(self.directory)

    def test_empty_breadcrumb_array_keeps_its_zero_geometry(self):
        def change(m):
            case = next(c for c in m["captures"] if c["fixture"] == "breadcrumb-empty")
            case["componentSize"]["width"] = 1
            case["componentRect"]["width"] = 1
        self.change("captures.json", change)
        with self.assertRaisesRegex(AssertionError, "Empty source breadcrumb geometry"):
            verifier.verify(self.directory)

    def test_last_breadcrumb_remains_an_index_callback(self):
        self.change("captures.json", lambda m: next(b for b in m["behavior"] if b["api"] == "BleeckerBreadcrumb" and b["action"] == "activate").update(selected=[0, 0]))
        with self.assertRaisesRegex(AssertionError, "index callback"):
            verifier.verify(self.directory)

    def test_disabled_header_action_cannot_activate(self):
        self.change("captures.json", lambda m: next(b for b in m["behavior"] if b["api"] == "BleeckerPageHeader" and b["action"] == "disabled-click").update(counter=1))
        with self.assertRaisesRegex(AssertionError, "header lifecycle"):
            verifier.verify(self.directory)

    def test_untrusted_text_renderer_cannot_supply_line_evidence(self):
        self.change("text-layout/measurements.json", lambda m: next(r for r in m if not r["lineEvidenceTrusted"]).update(lineEvidenceTrusted=True))
        with self.assertRaisesRegex(AssertionError, "Untrusted text renderer"):
            verifier.verify(self.directory)

    def test_changed_native_replay_cannot_be_claimed_identical(self):
        self.change("clean-replay.json", lambda m: m["results"][0].update(replaySha256="0" * 64))
        with self.assertRaisesRegex(AssertionError, "replay file mismatch"):
            verifier.verify(self.directory)


if __name__ == "__main__":
    unittest.main()
