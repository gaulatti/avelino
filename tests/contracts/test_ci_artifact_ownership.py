import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('ci_ownership',ROOT/'scripts/verify-ci-artifact-ownership.py')
OWNERSHIP=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OWNERSHIP)


class CiArtifactOwnership(unittest.TestCase):
    def test_ownership_repair_survives_unrelated_workflow_steps(self):
        self.assertTrue(OWNERSHIP.verify()['liveWorkflowMatchesRepair'])

    def test_broader_root_mount_is_rejected(self):
        original=Path.read_bytes
        def changed(path):
            content=original(path)
            return content.replace(b'$PWD/artifacts/linux/toolchain:/evidence',b'$PWD/artifacts:/evidence',1) if path==ROOT/'.github/workflows/linux.yml' else content
        with patch.object(Path,'read_bytes',changed):
            with self.assertRaises(AssertionError):
                OWNERSHIP.verify()


if __name__=='__main__':
    unittest.main()
