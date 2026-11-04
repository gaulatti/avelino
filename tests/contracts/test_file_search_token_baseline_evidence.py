import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('search_token_baseline',ROOT/'scripts/verify-file-input-search-token-baseline.py')
EVIDENCE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(EVIDENCE)


class SearchTokenBaselineEvidence(unittest.TestCase):
    def test_captured_sources_and_runtime_bindings_recompute(self):
        with contextlib.redirect_stdout(io.StringIO()):EVIDENCE.verify()

    def reject_promotion(self,path):
        original=Path.read_text
        def changed(current,*args,**kwargs):
            value=original(current,*args,**kwargs)
            if current==path:
                value=json.loads(value);value['accepted']=True;return json.dumps(value)
            return value
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):EVIDENCE.verify()

    def test_linux_candidate_cannot_be_promoted_to_native_acceptance(self):
        self.reject_promotion(EVIDENCE.DIRECTORY/'validation.json')

    def test_native_control_cannot_be_promoted_to_full_acceptance(self):
        self.reject_promotion(EVIDENCE.NATIVE/'limits.json')

    def test_changed_raw_evidence_is_rejected(self):
        original=Path.read_bytes
        def changed(path):
            value=original(path)
            return value+b'changed' if path.parent==EVIDENCE.DIRECTORY/'blobs' else value
        with patch.object(Path,'read_bytes',changed),self.assertRaises(AssertionError):EVIDENCE.verify()


if __name__=='__main__':unittest.main()
