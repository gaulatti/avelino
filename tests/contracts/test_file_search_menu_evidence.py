import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('search_menu',ROOT/'scripts/verify-file-input-search-menu.py')
EVIDENCE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


class SearchMenuEvidence(unittest.TestCase):
    def test_source_runtime_and_controlled_observations_recompute(self):
        with contextlib.redirect_stdout(io.StringIO()):EVIDENCE.verify()

    def test_cannot_promote_candidate_evidence_to_acceptance(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            content=original(path,*args,**kwargs)
            if path==EVIDENCE.DIRECTORY/'validation.json':
                report=json.loads(content);report['accepted']=True;return json.dumps(report)
            return content
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):EVIDENCE.verify()

    def test_corrupt_raw_record_is_rejected(self):
        original=Path.read_bytes
        def changed(path):
            content=original(path)
            return content+b'changed' if path.parent==EVIDENCE.DIRECTORY/'blobs' else content
        with patch.object(Path,'read_bytes',changed),self.assertRaises(AssertionError):EVIDENCE.verify()

    def test_missing_native_owner_delivery_is_rejected(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            content=original(path,*args,**kwargs)
            if path==EVIDENCE.NATIVE/'swiftui/output/ui-trace.json':
                trace=json.loads(content);trace['steps'][-1]['results'].pop();return json.dumps(trace)
            return content
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):EVIDENCE.verify_native()

    def test_owned_menu_parser_preserves_unexpected_third_choice(self):
        text='\t1 menu button Filename: avelinoulnacerulean\n\t\t2 menu Secondary Actions: Cancel\n\t\t\t3 Filename\n\t\t\t4 Everything\n\t\t\t5 Name and content\n\t6 button cancel'
        self.assertEqual(EVIDENCE.native_menu_choices(text),['Filename','Everything','Name and content'])


if __name__=='__main__':unittest.main()
