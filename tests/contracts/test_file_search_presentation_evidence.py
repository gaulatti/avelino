import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('file_search_presentation', ROOT / 'scripts/verify-file-input-search-presentation.py')
EVIDENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


class FileSearchPresentationEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.limits = json.loads((EVIDENCE.DIRECTORY / 'validation.json').read_text())
        records = json.loads((EVIDENCE.DIRECTORY / 'records.json').read_text())
        entry = records['source50/validation/consumer/result.json']
        value = json.loads(gzip.decompress((EVIDENCE.DIRECTORY / entry['stored']).read_bytes()))
        cls.phase = next(row for row in value['availableReport']['phases'] if row['phase'] == 'compound-mixed')

    def test_preserved_native_observations_and_published_runtime_recompute(self):
        EVIDENCE.verify()

    def test_runtime_binding_cannot_be_reassigned_to_the_parent_revision(self):
        with mock.patch.object(EVIDENCE, 'PUBLISHED', EVIDENCE.PARENT), self.assertRaises(AssertionError):
            EVIDENCE.verify()

    def test_accessible_name_cannot_be_substituted_for_the_query_caption(self):
        value = copy.deepcopy(self.phase)
        cell = value['tokenPresentation']['cells'][0]
        cell['query'] = cell['accessibleName']
        with self.assertRaises(AssertionError):
            EVIDENCE.captions(value)

    def test_tokens_cannot_hide_the_search_glyph_or_lose_their_gap(self):
        value = copy.deepcopy(self.phase)
        value['tokenPresentation']['glyphVisible'] = False
        with self.assertRaises(AssertionError):
            EVIDENCE.captions(value)
        value = copy.deepcopy(self.phase)
        cells = value['tokenPresentation']['cells']
        cells[1]['x'] = cells[0]['x'] + cells[0]['width']
        with self.assertRaises(AssertionError):
            EVIDENCE.captions(value)

    def test_native_acceptance_and_historical_suite_relabeling_are_rejected(self):
        for key in ['accepted', 'nativeRasterAccepted', 'nativeGeometryAccepted', 'nativeReaderAccepted', 'physicalInputAccepted']:
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.limits(dict(self.limits, **{key: True}))
        with self.assertRaises(AssertionError):
            EVIDENCE.limits(dict(self.limits, fullSuiteSource=45))
        with self.assertRaises(AssertionError):
            EVIDENCE.limits(dict(self.limits, fullSuiteConclusion='success'))


if __name__ == '__main__':
    unittest.main()
