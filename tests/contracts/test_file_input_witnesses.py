"""Preserve complete native observations and explicit type-adapter boundaries."""
import importlib.util
import itertools
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('file_input_witnesses', ROOT / 'scripts/generate-file-input-witnesses.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class FileInputWitnesses(unittest.TestCase):
    def test_projection_is_current_and_complete(self):
        actual = json.loads(source.OUTPUT.read_text())
        self.assertEqual(actual, source.projection())
        self.assertFalse(actual['accepted'])
        self.assertEqual(len(actual['fixtures']), 32)
        contexts = set(itertools.product(['light', 'dark'], [1, 1.5], [1, 2]))
        for key in ['closed', 'sizing']:
            rows = actual[key]
            self.assertEqual(len(rows), 256)
            self.assertEqual({(row['configuration']['id'], (row['appearance'], row['textScale'], row['dpr'])) for row in rows},
                set(itertools.product([row['configuration']['id'] for row in actual['fixtures']], contexts)))
        self.assertTrue(all(set(row['frames']) == {'body', 'caller'} and row['nativeState']['results'] == [] for row in actual['closed']))
        self.assertTrue(all(len(row['proposals']) == 15 for row in actual['sizing']))

    def test_unknown_native_type_requires_an_explicit_adapter(self):
        with self.assertRaises(AssertionError):
            source.content_types(['org.example.unmapped'])

    def test_undeclared_file_type_is_distinct_from_an_empty_type_array(self):
        self.assertEqual(source.content_types([]), [])
        custom = source.content_types(['org.avelino.fixture'])
        self.assertEqual(custom, [{'identifier': 'org.avelino.fixture', 'filenameExtensions': []}])
        self.assertNotIn('*/*', custom)

    def test_directory_and_all_file_types_remain_distinct(self):
        self.assertEqual(source.content_types(['public.folder']), ['inode/directory'])
        self.assertEqual(source.content_types(['public.item']), ['*/*'])
        self.assertEqual(source.content_types(['public.folder', 'public.plain-text']), ['inode/directory', 'text/plain'])


if __name__ == '__main__':
    unittest.main()
