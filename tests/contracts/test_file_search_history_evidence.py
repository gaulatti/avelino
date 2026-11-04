import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('search_history',ROOT/'scripts/verify-file-input-search-history.py')
EVIDENCE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(EVIDENCE)


class SearchHistoryEvidence(unittest.TestCase):
    def test_raw_controlled_observations_recompute(self):
        with contextlib.redirect_stdout(io.StringIO()):EVIDENCE.verify()

    def test_cannot_promote_observations_to_native_acceptance(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            value=original(path,*args,**kwargs)
            if path==EVIDENCE.DIRECTORY/'observations.json':
                report=json.loads(value);report['accepted']=True;return json.dumps(report)
            return value
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):EVIDENCE.verify()

    def test_changed_capture_bytes_are_rejected(self):
        original=Path.read_bytes
        def changed(path):
            value=original(path)
            return value+b'changed' if path.name=='interaction-07.json' else value
        with patch.object(Path,'read_bytes',changed),self.assertRaises(AssertionError):EVIDENCE.verify()


if __name__=='__main__':unittest.main()
