import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'search_atomic_integration', ROOT / 'scripts/verify-file-input-search-atomic-integration.py')
EVIDENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


class AtomicSearchIntegrationEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.limits = json.loads((EVIDENCE.DIRECTORY / 'validation.json').read_text())
        records = json.loads((EVIDENCE.DIRECTORY / 'records.json').read_text())
        row = records['portable9/output/available.json']
        cls.report = json.loads(gzip.decompress((EVIDENCE.DIRECTORY / row['stored']).read_bytes()))

    def test_recorded_expression_and_limits_satisfy_the_contract(self):
        EVIDENCE.candidate_limits(self.limits)
        EVIDENCE.phase_checks(self.report)

    def test_full_suite_cannot_be_relabelled_as_current_source(self):
        value = dict(self.limits, full58ExecutedOnSource=47)
        with self.assertRaises(AssertionError):
            EVIDENCE.candidate_limits(value)

    def test_published_source_binding_cannot_point_to_the_preintegration_commit(self):
        with patch.object(EVIDENCE, 'PUBLISHED', EVIDENCE.PARENT), self.assertRaises(AssertionError):
            EVIDENCE.verify()

    def test_candidate_cannot_claim_native_or_physical_acceptance(self):
        for key in ['accepted', 'nativeRasterAccepted', 'nativeReaderAccepted',
                    'completeA11yEventDeliveryAccepted', 'physicalInputAccepted',
                    'independentMachineAccepted']:
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.candidate_limits(dict(self.limits, **{key: True}))

    def test_two_source_scopes_cannot_be_collapsed(self):
        for key in ['libraryProjectMounted', 'consumerProjectMounted', 'productBuildMounted']:
            value = dict.fromkeys(['libraryProjectMounted', 'consumerProjectMounted', 'productBuildMounted'], False)
            value[key] = True
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.absent_projects(value)

    def test_conjunction_cannot_be_broadened(self):
        value = copy.deepcopy(self.report)
        next(p for p in value['phases'] if p['phase'] == 'compound-mixed')['names'].append('name-only.txt')
        with self.assertRaises(AssertionError):
            EVIDENCE.phase_checks(value)

    def test_other_token_and_selected_undo_cannot_be_dropped(self):
        for field, replacement in [('expression', []), ('selectedText', '')]:
            value = copy.deepcopy(self.report)
            next(p for p in value['phases'] if p['phase'] == 'compound-undo')[field] = replacement
            with self.subTest(field=field), self.assertRaises(AssertionError):
                EVIDENCE.phase_checks(value)

    def test_changed_raw_bytes_are_rejected(self):
        original = Path.read_bytes
        def changed(path):
            value = original(path)
            return value + b'changed' if path.parent == EVIDENCE.DIRECTORY / 'blobs' else value
        with patch.object(Path, 'read_bytes', changed), self.assertRaises(AssertionError):
            EVIDENCE.audit_files(EVIDENCE.DIRECTORY)


if __name__ == '__main__':
    unittest.main()
