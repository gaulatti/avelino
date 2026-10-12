import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from reference_sources import resolve_reference


class ExternalReferenceStorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        subprocess.run(["git", "init", "-q", self.root], check=True)
        self.data = b"immutable external reference fixture"
        (self.root / "reference.tar.gz").write_bytes(self.data)
        subprocess.run(["git", "add", "reference.tar.gz"], cwd=self.root, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "fixture"], cwd=self.root, check=True)
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root).decode().strip()
        (self.root / "reference.tar.gz").unlink()
        self.record = dict(artifact=".cache/reference-sources/reference.tar.gz",
                           sha256=hashlib.sha256(self.data).hexdigest(),
                           storage=dict(kind="git-history", revision=revision, path="reference.tar.gz"))

    def test_recovers_exact_bytes_from_history_without_sibling_or_working_source(self):
        artifact = resolve_reference(self.record, self.root)
        self.assertEqual(artifact.read_bytes(), self.data)
        self.assertFalse((self.root / "reference.tar.gz").exists())

    def test_corrupt_cache_is_rejected_without_overwriting_it(self):
        artifact = resolve_reference(self.record, self.root)
        artifact.write_bytes(b"changed")
        with self.assertRaises(AssertionError):
            resolve_reference(self.record, self.root)
        self.assertEqual(artifact.read_bytes(), b"changed")

    def test_wrong_preserved_hash_is_rejected_before_caching(self):
        self.record["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            resolve_reference(self.record, self.root)
        self.assertFalse((self.root / self.record["artifact"]).exists())

    def test_missing_history_requires_explicit_fetch(self):
        self.record["storage"]["revision"] = "0" * 40
        with self.assertRaisesRegex(RuntimeError, "git fetch origin"):
            resolve_reference(self.record, self.root)


if __name__ == "__main__":
    unittest.main()
