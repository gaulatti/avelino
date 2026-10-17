"""Protect source witnesses and preserve unresolved chooser acceptance gates."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('file_input_source', ROOT / 'scripts/verify-file-input-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class FileInputSource(unittest.TestCase):
    def setUp(self):
        self.read = lambda name: json.loads((source.DIRECTORY / name).read_text())
        self.report = self.read('investigation.json')
        self.fixtures = {r['id']: r for r in self.read('fixtures.json')}

    def test_complete_source_record_recomputes(self):
        source.verify()

    def test_cannot_claim_acceptance_or_change_expectations(self):
        for key, value in [('accepted', True), ('expectedImagesChanged', True), ('tolerance', 'one-pixel')]:
            report = copy.deepcopy(self.report)
            report[key] = value
            with self.subTest(key=key), self.assertRaises(AssertionError):
                source.validate_report(report)

    def test_cannot_close_unmeasured_behavior_or_physical_gates(self):
        for key in ['behaviorSourceReplayStatus', 'physicalInputAcceptance', 'openPanelRasterAcceptance']:
            report = copy.deepcopy(self.report)
            report[key] = 'passed'
            with self.subTest(key=key), self.assertRaises(AssertionError):
                source.validate_report(report)

    def test_cannot_drop_type_conformance_gate(self):
        self.report['remainingAcceptance'].remove('typeConformanceAndOwnerUpdates')
        with self.assertRaises(AssertionError):
            source.validate_report(self.report)

    def test_cannot_claim_independent_machine_availability(self):
        self.report['sourceOnlyArtifact']['downloadAvailability'] = 'passed'
        with self.assertRaises(AssertionError):
            source.validate_report(self.report)

    def test_missing_native_context_is_rejected(self):
        data = self.read('output/captures.json')
        data['rows'].pop()
        with self.assertRaises(AssertionError):
            source.closed_observations(source.DIRECTORY, self.fixtures, data)

    def test_duplicate_native_context_is_rejected(self):
        data = self.read('output/captures.json')
        data['rows'].append(copy.deepcopy(data['rows'][0]))
        with self.assertRaises(AssertionError):
            source.closed_observations(source.DIRECTORY, self.fixtures, data)

    def test_sizing_cannot_be_replaced_by_caller_frames(self):
        data = self.read('sizing-output/sizing.json')
        for mode in data['rows'][0]['modes']:
            mode['proposals'] = {'caller': {'width': 116, 'height': 40}}
        with self.assertRaises(AssertionError):
            source.sizing_observations(self.fixtures, data)

    def test_literal_sizing_disagreement_is_rejected(self):
        data = self.read('sizing-output/sizing.json')
        data['rows'][0]['modes'][2]['proposals']['width-30']['height'] += 1
        with self.assertRaises(AssertionError):
            source.sizing_observations(self.fixtures, data)


if __name__ == '__main__':
    unittest.main()
