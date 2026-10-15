import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("presentation_source", ROOT / "scripts/verify-presentation-state-source.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class PresentationSourceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "source"
        shutil.copytree(verifier.DIRECTORY, self.directory)

    def rewrite_manifest(self, change):
        path = self.directory / "captures.json"
        manifest = json.loads(path.read_text())
        change(manifest)
        path.write_text(json.dumps(manifest))
        report_path = self.directory / "investigation.json"
        report = json.loads(report_path.read_text())
        report["files"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        report_path.write_text(json.dumps(report))

    def test_self_approval_is_refused(self):
        path = self.directory / "investigation.json"
        report = json.loads(path.read_text())
        report["accepted"] = True
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(AssertionError, "self-approve"):
            verifier.verify(self.directory)

    def test_source_evidence_cannot_inflate_linux_coverage(self):
        path = self.directory / "investigation.json"
        report = json.loads(path.read_text())
        report["linuxImplementationStarted"] = True
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(AssertionError, "cannot start Linux coverage"):
            verifier.verify(self.directory)

    def test_overlay_result_requires_successful_positive_control(self):
        def change(manifest):
            case = next(b for b in manifest["behavior"] if b["api"] == "BleeckerLoadingOverlay")
            case["underlyingPositiveControl"] = 0
        self.rewrite_manifest(change)
        with self.assertRaisesRegex(AssertionError, "positive control"):
            verifier.verify(self.directory)

    def test_overlay_cannot_claim_pointer_pass_through(self):
        def change(manifest):
            case = next(b for b in manifest["behavior"] if b["api"] == "BleeckerLoadingOverlay" and b["action"] == "center")
            case["underlying"] = 1
        self.rewrite_manifest(change)
        with self.assertRaisesRegex(AssertionError, "overlay hit behavior"):
            verifier.verify(self.directory)

    def test_producer_update_must_preserve_action_state(self):
        def change(manifest):
            case = next(b for b in manifest["behavior"] if b["api"] == "BleeckerEmptyState" and b["action"] == "producer-update")
            case["counter"] = 0
        self.rewrite_manifest(change)
        with self.assertRaisesRegex(AssertionError, "action counter"):
            verifier.verify(self.directory)

    def test_missing_native_input_case_is_refused(self):
        self.rewrite_manifest(lambda manifest: manifest["behavior"].pop())
        with self.assertRaisesRegex(AssertionError, "pointer/lifecycle matrix"):
            verifier.verify(self.directory)

    def test_reopened_actions_must_be_a_fresh_subtree(self):
        def change(manifest):
            case = next(b for b in manifest["behavior"] if b["api"] == "BleeckerErrorState" and b["action"] == "reopen")
            case["mounts"] = 1
        self.rewrite_manifest(change)
        with self.assertRaisesRegex(AssertionError, "subtree lifecycle"):
            verifier.verify(self.directory)

    def test_changed_text_probe_cannot_be_declared_identical(self):
        def change(manifest):
            case = next(p for p in manifest["centeredTextLines"] if not p["probePngByteIdentical"])
            case["probePngByteIdentical"] = True
        self.rewrite_manifest(change)
        with self.assertRaisesRegex(AssertionError, "identity claim"):
            verifier.verify(self.directory)


if __name__ == "__main__":
    unittest.main()
