import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('file_search_pointer', ROOT / 'scripts/verify-file-input-search-pointer.py')
EVIDENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


class FileSearchPointerEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.limits = json.loads((EVIDENCE.DIRECTORY / 'validation.json').read_text())
        records = json.loads((EVIDENCE.DIRECTORY / 'records.json').read_text())
        entry = records['source56/validation/consumer/result.json']
        cls.report = json.loads(gzip.decompress((EVIDENCE.DIRECTORY / entry['stored']).read_bytes()))['availableReport']

    def test_preserved_calls_failures_and_current_runtime_recompute(self):
        EVIDENCE.verify()

    def test_historical_runtime_cannot_be_reassigned_to_its_parent(self):
        with mock.patch.object(EVIDENCE, 'PUBLISHED', EVIDENCE.PARENT), self.assertRaises(AssertionError):
            EVIDENCE.verify()

    def test_query_selection_cannot_be_replaced_by_menu_activation(self):
        value = copy.deepcopy(self.report)
        next(row for row in value['phases'] if row['phase'] == 'query-selected')['selectedText'] = ''
        with self.assertRaises(AssertionError):
            EVIDENCE.phases(value)

    def test_expansion_cannot_drop_neighbor_or_broaden_compound_results(self):
        for key, replacement in [('expression', [{'kind': 'text', 'text': 'avelinoulnacerulean'}]),
                                 ('names', ['pine-only.txt', 'pine-peer.txt'])]:
            value = copy.deepcopy(self.report)
            next(row for row in value['phases'] if row['phase'] == 'compound-query-expanded')[key] = replacement
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.phases(value)

    def test_undo_selection_and_redo_caret_are_required(self):
        for phase, key, replacement in [('query-expand-undo', 'selectedText', ''),
                                        ('query-expand-redo', 'cursorPosition', 0)]:
            value = copy.deepcopy(self.report)
            next(row for row in value['phases'] if row['phase'] == phase)[key] = replacement
            with self.subTest(phase=phase), self.assertRaises(AssertionError):
                EVIDENCE.phases(value)

    def test_old_suite_and_native_acceptance_cannot_be_promoted(self):
        for key in ['accepted', 'nativeRasterAccepted', 'nativeGeometryAccepted',
                    'nativeReaderAccepted', 'physicalInputAccepted', 'independentMachineAccepted']:
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.limits(dict(self.limits, **{key: True}))
        with self.assertRaises(AssertionError):
            EVIDENCE.limits(dict(self.limits, fullSuiteSource=50))

    def test_development_sources_are_absent_from_portable_runtime(self):
        for key in ['libraryProjectMounted', 'consumerProjectMounted', 'productBuildMounted']:
            value = dict.fromkeys(['libraryProjectMounted', 'consumerProjectMounted', 'productBuildMounted'], False)
            value[key] = True
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.absent(value)


if __name__ == '__main__':
    unittest.main()
