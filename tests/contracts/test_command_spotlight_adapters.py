"""Keep native input, caller state and raw geometry visible in Linux replay."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('spotlight_capture', ROOT / 'scripts/capture-command-spotlight.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class CommandSpotlightAdapters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(capture.PROJECTION.read_text())
        cls.rows = capture.rows(cls.data)

    def test_entire_native_corpus_retained(self):
        self.assertEqual(len(self.rows), 1792)
        self.assertEqual(sum(row['kind'] == 'closed' for row in self.rows), 256)
        self.assertEqual(sum(row['kind'] == 'history' for row in self.rows), 1536)
        for context in capture.CONTEXTS:
            self.assertEqual(sum(row['context'] == capture.prefix(*context) for row in self.rows), 224)

    def test_missing_context_rejected(self):
        changed = copy.deepcopy(self.data)
        changed['closed'].pop()
        with self.assertRaises(AssertionError):
            capture.rows(changed)

    def test_caller_frame_stays_separate_from_fixed_surface(self):
        definitions = capture.definitions(self.data)['fixtures']
        self.assertEqual(len(definitions), 32)
        self.assertTrue(all((row['width'], row['height']) == (720, 520) for row in definitions))
        zero = next(row for row in definitions if row['id'] == 'width-zero')
        self.assertEqual(zero['callerWidth'], 0)
        self.assertIsNone(zero['callerHeight'])

    def test_owner_and_editor_are_separate(self):
        row = next(row for row in self.rows if row['configuration']['id'] == 'owner-observe' and row.get('step') == 'key-query')
        self.assertEqual(row['query'], 'No matching commands')
        self.assertEqual(row['editorText'], 'q')
        self.assertEqual(row['requests'], ['No matching commands', 'No matching commands', 'q'])
        actual = dict(row, requests=['q'])
        self.assertEqual(capture.observations(row, actual)['stateStatus'], 'failed')

    def test_local_state_differences_are_not_hidden(self):
        row = next(row for row in self.rows if row['configuration']['id'] == 'many-buttons' and row.get('step') == 'restore')
        self.assertFalse(row['matchesInitialPixels'])
        self.assertEqual(row['rowCounts']['0'], 2)
        self.assertEqual(capture.observations(row, row)['retainedRasterStatus'], 'passed')
        self.assertEqual(capture.observations(row, dict(row, matchesInitialPixels=True))['retainedRasterStatus'], 'failed')

    def test_row_state_and_lifecycle_are_compared(self):
        row = self.rows[0]
        for key in ['rowCounts', 'rowInstances', 'rowAppearances', 'rowDisappearances', 'appearedKeys', 'lifecycle']:
            actual = dict(row, **{key: None})
            self.assertIn(key, capture.observations(row, actual)['stateErrors'])

    def test_offscreen_probe_frames_remain_in_raw_observations(self):
        row = next(row for row in self.rows if row.get('step') == 'empty')
        self.assertFalse(any(key.startswith(('row-', 'content-')) for key in row['frames']))
        self.assertTrue(any(key.startswith(('row-', 'content-')) for key in row['rawFrames']))

    def test_full_range_ids_and_native_sizing_are_preserved(self):
        ids = {entry['id'] for row in self.rows for entry in row['configuration']['entries']}
        self.assertTrue({'-9223372036854775808', '9223372036854775807'} <= ids)
        self.assertEqual(sum(len(row['proposals']) for row in self.data['sizing']), 3840)


if __name__ == '__main__':
    unittest.main()
