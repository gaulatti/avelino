import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("verify", ROOT / "scripts/verify-references.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class ImmutableArtifactTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / "reference/source-manifest.json").read_text())["references"]["desktop"]

    def test_modified_expected_source_bytes_fail_clean_verification(self):
        self.record["files"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as clean, self.assertRaises(AssertionError):
            verify.verify_reference(self.record, Path(clean))

    def test_omitted_expected_member_fails_clean_verification(self):
        self.record["files"].pop()
        with tempfile.TemporaryDirectory() as clean, self.assertRaises(AssertionError):
            verify.verify_reference(self.record, Path(clean))

    def test_modified_archive_hash_fails_before_extracting(self):
        self.record["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as clean, self.assertRaises(AssertionError):
            verify.verify_reference(self.record, Path(clean))
            self.assertEqual(list(Path(clean).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
