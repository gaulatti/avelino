import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('search_token_editing',ROOT/'scripts/verify-file-input-search-token-editing.py')
EVIDENCE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(EVIDENCE)


class SearchTokenEditingEvidence(unittest.TestCase):
    def test_captured_sources_and_real_runtime_recompute(self):
        with contextlib.redirect_stdout(io.StringIO()):EVIDENCE.verify()

    def test_cannot_promote_candidate_to_native_acceptance(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            value=original(path,*args,**kwargs)
            if path==EVIDENCE.DIRECTORY/'validation.json':
                report=json.loads(value);report['accepted']=True;return json.dumps(report)
            return value
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):EVIDENCE.verify()

    def test_changed_raw_record_is_rejected(self):
        original=Path.read_bytes
        def changed(path):
            value=original(path)
            return value+b'changed' if path.parent==EVIDENCE.DIRECTORY/'blobs' else value
        with patch.object(Path,'read_bytes',changed),self.assertRaises(AssertionError):EVIDENCE.verify()


if __name__=='__main__':unittest.main()
