import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("navigation_proposal", ROOT / "scripts/verify-proposals.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class NavigationProposalIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/navigation-layout-20261015", self.directory)

    def change(self, filename, operation):
        path = self.directory / filename
        data = json.loads(path.read_text())
        operation(data)
        path.write_text(json.dumps(data))
        path = self.directory / "proposal.json"
        data = json.loads(path.read_text())
        data["files"][filename] = hashlib.sha256((self.directory / filename).read_bytes()).hexdigest()
        path.write_text(json.dumps(data))

    def test_single_empty_title_cannot_gain_geometry(self):
        self.change("captures.json", lambda m: next(c for c in m["captures"] if c["fixture"] == "breadcrumb-single-empty")["componentSize"].update(width=1))
        with self.assertRaisesRegex(AssertionError, "Invalid navigation empty geometry"):
            verifier.verify(self.directory)

    def test_source_callback_cannot_change_with_a_new_manifest_hash(self):
        self.change("captures.json", lambda m: next(c for c in m["behavior"] if c["api"] == "BleeckerBreadcrumb" and c["action"] == "activate").update(selected=[0, 0]))
        with self.assertRaisesRegex(AssertionError, "Navigation source witnesses differ"):
            verifier.verify(self.directory)


if __name__ == "__main__":
    unittest.main()
