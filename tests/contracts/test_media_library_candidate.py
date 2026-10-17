"""Keep the grid's evidence and unresolved mirror gates explicit."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('media_library_candidate', ROOT / 'scripts/verify-media-library-candidate.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)

class MediaLibraryCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((candidate.DIRECTORY / 'candidate.json').read_text())
    def setUp(self):
        self.report = copy.deepcopy(self.original)
    def refused(self):
        with self.assertRaises(AssertionError):
            candidate.validate_report(self.report)
    def test_complete_candidate_recomputes(self):
        candidate.verify()
    def test_frozen_producer_keeps_generated_cache_inputs(self):
        binding = json.loads((candidate.DIRECTORY / 'package/artifact-binding.json').read_text())
        producer = json.loads((candidate.DIRECTORY / 'qt/inputs.json').read_text())['sourceFiles']
        self.assertTrue(any('__pycache__' in Path(name).parts for name in binding['producerCriticalFiles']))
        candidate.validate_producer_inputs(binding, producer)
    def test_cannot_omit_frozen_producer_input(self):
        binding = json.loads((candidate.DIRECTORY / 'package/artifact-binding.json').read_text())
        producer = json.loads((candidate.DIRECTORY / 'qt/inputs.json').read_text())['sourceFiles']
        binding['producerCriticalFiles'].pop('src/Avelino/BleeckerMediaLibrary.qml')
        with self.assertRaises(AssertionError):
            candidate.validate_producer_inputs(binding, producer)
    def test_cannot_change_frozen_producer_checksum(self):
        binding = json.loads((candidate.DIRECTORY / 'package/artifact-binding.json').read_text())
        producer = json.loads((candidate.DIRECTORY / 'qt/inputs.json').read_text())['sourceFiles']
        binding['producerCriticalFiles']['src/Avelino/BleeckerMediaLibrary.qml'] = 'other'
        with self.assertRaises(AssertionError):
            candidate.validate_producer_inputs(binding, producer)
    def test_cannot_claim_acceptance(self):
        self.report['accepted'] = True
        self.refused()
    def test_cannot_change_pin(self):
        self.report['reference'] = 'other'
        self.refused()
    def test_cannot_change_base(self):
        self.report['baseRevision'] = 'other'
        self.refused()
    def test_cannot_claim_strict_success(self):
        self.report['strictComparisonStatus'] = 'passed'
        self.refused()
    def test_cannot_claim_unobserved_sizing(self):
        self.report['strictComparison']['sizingObservations'] = 7440
        self.refused()
    def test_cannot_drop_query_contexts(self):
        self.report['strictComparison']['nativeSizingContexts'] = 495
        self.refused()
    def test_cannot_drop_history_steps(self):
        self.report['strictComparison']['byKind']['history']['cases'] = 1007
        self.refused()
    def test_cannot_drop_fatal_inputs(self):
        self.report['validation']['fatalProcesses'] = 0
        self.refused()
    def test_cannot_drop_raster_stability_gate(self):
        self.report['remainingAcceptance'].remove('retainedCallerRasterStability')
        self.refused()
    def test_cannot_drop_physical_gate(self):
        self.report['remainingAcceptance'].remove('physicalDisplaysInput')
        self.refused()
    def test_cannot_drop_reader_gate(self):
        self.report['remainingAcceptance'].remove('readers')
        self.refused()
    def test_cannot_hide_operator_phases(self):
        self.report['validation']['operatorStates'] = 17
        self.refused()
    def test_cannot_add_tolerance(self):
        self.report['tolerance'] = 'one pixel'
        self.refused()
    def test_cannot_approve_exception(self):
        self.report['approvedExceptions'] = ['caption']
        self.refused()
    def test_cannot_rewrite_expected(self):
        self.report['expectedImagesChanged'] = True
        self.refused()

if __name__ == '__main__':
    unittest.main()
