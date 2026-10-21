import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('search_accessibility',ROOT/'scripts/verify-file-input-search-accessibility.py')
EVIDENCE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


class SearchAccessibilityEvidence(unittest.TestCase):
    def test_captured_source_and_runtime_evidence_recompute(self):
        with contextlib.redirect_stdout(io.StringIO()):
            EVIDENCE.verify()

    def test_cannot_turn_scoped_observations_into_acceptance(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            content=original(path,*args,**kwargs)
            if path==EVIDENCE.DIRECTORY/'validation.json':
                report=json.loads(content);report['accepted']=True
                return json.dumps(report)
            return content
        with patch.object(Path,'read_text',changed):
            with self.assertRaises(AssertionError):
                EVIDENCE.verify()

    def test_changed_capture_bytes_are_rejected(self):
        original=Path.read_bytes
        def changed(path):
            content=original(path)
            return content+b'changed' if path.parent==EVIDENCE.DIRECTORY/'blobs' else content
        with patch.object(Path,'read_bytes',changed):
            with self.assertRaises(AssertionError):
                EVIDENCE.verify()


if __name__=='__main__':unittest.main()
