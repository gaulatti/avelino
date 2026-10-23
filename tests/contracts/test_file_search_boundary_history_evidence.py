import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('boundary_history', ROOT / 'scripts/verify-file-input-search-boundary-history.py')
EVIDENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


class FileSearchBoundaryHistoryEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validation = json.loads((EVIDENCE.DIRECTORY / 'validation.json').read_text())
        cls.records = json.loads((EVIDENCE.DIRECTORY / 'records.json').read_text())
        cls.report = cls.record('source62/validation/consumer/result.json')['availableReport']

    @classmethod
    def raw(cls, name):
        entry = cls.records[name]
        value = (EVIDENCE.DIRECTORY / entry['stored']).read_bytes()
        return gzip.decompress(value) if entry['stored'].endswith('.gz') else value

    @classmethod
    def record(cls, name):
        return json.loads(cls.raw(name))

    def test_native_failed_attempts_and_current_runtime_recompute(self):
        EVIDENCE.verify()

    def test_published_pointer_parent_cannot_replace_current_history_parent(self):
        with mock.patch.object(EVIDENCE, 'PARENT', '4f720b5eee7623e57f0dc263514eba85c464cffb'), self.assertRaises(AssertionError):
            EVIDENCE.limits(self.validation)

    def test_first_undo_cannot_be_relabelled_as_restoring_the_token(self):
        value = copy.deepcopy(self.report)
        row = next(row for row in value['phases'] if row['phase'] == 'history-first-undo')
        row['editorText'] = 'oak \ufffc cedar'
        with self.assertRaises(AssertionError):
            EVIDENCE.phases(value)

    def test_complete_later_redo_history_is_required(self):
        value = copy.deepcopy(self.report)
        value['phases'] = [row for row in value['phases'] if row['phase'] != 'history-later-redo-3']
        with self.assertRaises(AssertionError):
            EVIDENCE.phases(value)

    def test_prefix_caret_cannot_move_after_query(self):
        value = copy.deepcopy(self.report)
        next(row for row in value['phases'] if row['phase'] == 'prefix-redo')['cursorPosition'] = 9
        with self.assertRaises(AssertionError):
            EVIDENCE.phases(value)

    def test_prefix_undo_retains_everything_mode(self):
        value = copy.deepcopy(self.report)
        row = next(row for row in value['phases'] if row['phase'] == 'prefix-first-undo')
        row['expression'][1]['mode'] = 'filename'
        with self.assertRaises(AssertionError):
            EVIDENCE.phases(value)

    def test_native_projection_cannot_change_without_changing_its_raw_call(self):
        value = self.record('native9/case-projections.json')
        value['dataset']['rows'][2]['value'] = 'oak \ufffc cedar'
        name = 'native9/captured/' + value['rawCall']
        with self.assertRaises(AssertionError):
            EVIDENCE.projection(value, self.record(name), self.raw(name))

    def test_decomposed_unicode_cannot_be_normalized_in_the_projection(self):
        value = self.record('native8/case-projections.json')
        value['dataset']['cases'][0]['query'] = 'avelinoé'
        name = 'native8/captured/' + value['rawCall']
        with self.assertRaises(AssertionError):
            EVIDENCE.projection(value, self.record(name), self.raw(name))

    def test_reused_full_suite_cannot_be_relabelled_as_current_execution(self):
        value = self.record('source62/source61-comparability.json')
        value['qtSuiteRerunOn62'] = True
        with self.assertRaises(AssertionError):
            EVIDENCE.comparability(value)

    def test_full_suite_reuse_rejects_library_changes(self):
        value = self.record('source62/source61-comparability.json')
        value['runtimeInputDifferences'].append('src/Avelino/filechoosersearchtext.cpp')
        with self.assertRaises(AssertionError):
            EVIDENCE.comparability(value)

    def test_runtime_checks_do_not_promote_native_acceptance(self):
        for key in ['accepted', 'nativeRasterAccepted', 'nativeGeometryAccepted',
                    'nativeReaderAccepted', 'physicalInputAccepted',
                    'independentMachineAccepted', 'generalNativeHistoryAccepted',
                    'nativeImePreeditAccepted']:
            value = copy.deepcopy(self.validation)
            value[key] = True
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.limits(value)


if __name__ == '__main__':
    unittest.main()
