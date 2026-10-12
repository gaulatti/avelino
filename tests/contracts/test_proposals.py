import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("verify_proposals", ROOT / "scripts/verify-proposals.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class ProposalIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/desktop-20261012", self.directory)

    def test_proposal_cannot_self_approve(self):
        path = self.directory / "proposal.json"
        data = json.loads(path.read_text())
        data["accepted"] = True
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(AssertionError, "self-approve"):
            verifier.verify(self.directory)

    def test_changed_pixels_fail_checksums(self):
        path = next(self.directory.glob("*.png"))
        data = bytearray(path.read_bytes())
        data[-1] ^= 1
        path.write_bytes(data)
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)

    def test_false_environment_dpr_fails_even_with_new_manifest_checksum(self):
        captures = self.directory / "captures.json"
        data = json.loads(captures.read_text())
        data["captures"][0]["environmentDisplayScale"] = 9
        captures.write_text(json.dumps(data))
        path = self.directory / "proposal.json"
        proposal = json.loads(path.read_text())
        proposal["files"]["captures.json"] = hashlib.sha256(captures.read_bytes()).hexdigest()
        path.write_text(json.dumps(proposal))
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)

    def test_discovered_card_variant_cannot_be_omitted_from_valid_capture_matrix(self):
        captures_path = self.directory / "captures.json"
        captures = json.loads(captures_path.read_text())
        removed = [c for c in captures["captures"] if c["api"] == "BleeckerCard" and c["variant"] == "outlined"]
        removed_paths = {c["path"] for c in removed}
        captures["captures"] = [c for c in captures["captures"] if c["path"] not in removed_paths]
        captures_path.write_text(json.dumps(captures))
        fixtures_path = self.directory / "fixtures.json"
        fixtures = json.loads(fixtures_path.read_text())
        fixtures["fixtures"] = [f for f in fixtures["fixtures"] if not (f["api"] == "BleeckerCard" and f["variant"] == "outlined")]
        fixtures_path.write_text(json.dumps(fixtures))
        index_path = self.directory / "api-index.json"
        index = json.loads(index_path.read_text())
        index["BleeckerCard"]["captures"] = [p for p in index["BleeckerCard"]["captures"] if p not in removed_paths]
        index["BleeckerCard"]["fixtures"] = [f for f in index["BleeckerCard"]["fixtures"] if f not in {c["fixture"] for c in removed}]
        index_path.write_text(json.dumps(index))
        path = self.directory / "proposal.json"
        proposal = json.loads(path.read_text())
        proposal["captures"] = len(captures["captures"])
        proposal["fixtureDefinitions"] = len(fixtures["fixtures"])
        for name in removed_paths:
            (self.directory / name).unlink()
            del proposal["files"][name]
        for modified in [captures_path, fixtures_path, index_path]:
            proposal["files"][modified.name] = hashlib.sha256(modified.read_bytes()).hexdigest()
        path.write_text(json.dumps(proposal))
        with self.assertRaisesRegex(AssertionError, "Missing discovered contract combinations"):
            verifier.verify(self.directory)
