"""Prevent scoped mechanism receipts from silently admitting stronger claims."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('search_atomic',ROOT/'scripts/verify-file-input-search-atomic.py')
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)


class AtomicEvidenceTests(unittest.TestCase):
    def test_published_observations_recompute(self):
        result=MODULE.verify()
        self.assertFalse(result['productionIntegrated'])
        self.assertEqual(result['prototypePhases'],104)

    def test_restored_contents_without_token_selection_are_insufficient(self):
        runtime=json.loads((MODULE.LINUX/'prototype3/output/runtime.json').read_text())
        phase=next(p for p in runtime['variants'][0]['observations'] if p['phase']=='deletion-undo')
        phase['selectedText']=''
        with self.assertRaises(AssertionError):MODULE.mechanism(runtime,3)

    def test_broader_compound_membership_is_not_the_captured_conjunction(self):
        projections=json.loads((MODULE.NATIVE/'field-projections.json').read_text())
        phase=next(p for p in projections['phases'] if p['phase']=='compound-mixed')
        phase['controlledResultLines']=copy.deepcopy(next(p for p in projections['phases'] if p['phase']=='compound-everything')['controlledResultLines'])
        with self.assertRaises(AssertionError):MODULE.native_phases(projections)

    def test_mechanism_pass_cannot_be_promoted_to_native_acceptance(self):
        runtime=json.loads((MODULE.LINUX/'prototype3/output/runtime.json').read_text())
        runtime['nativeMatchingAccepted']=True
        with self.assertRaises(AssertionError):MODULE.mechanism(runtime,3)


if __name__=='__main__':unittest.main()
