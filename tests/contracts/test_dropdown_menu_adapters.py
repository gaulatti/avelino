"""Retain the native dropdown inputs and complete caller geometry."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('dropdown_capture', ROOT / 'scripts/capture-dropdown-menu.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class DropdownMenuAdapters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(capture.PROJECTION.read_text())
        cls.rows = capture.rows(cls.data)

    def test_complete_native_corpus(self):
        self.assertEqual(len(self.rows), 256)
        for context in capture.CONTEXTS:
            self.assertEqual(sum(row['context'] == capture.prefix(*context) for row in self.rows), 32)
        self.assertEqual(sum(len(row['proposals']) for row in self.data['sizing']), 3840)
        self.assertEqual(len(self.data['dispatch']), 3)

    def test_missing_context_rejected(self):
        changed = copy.deepcopy(self.data)
        changed['closed'].pop()
        with self.assertRaises(AssertionError):
            capture.rows(changed)

    def test_no_acceptance_or_reference_update(self):
        for key, value in [('accepted', True), ('reference', 'unapproved')]:
            changed = copy.deepcopy(self.data)
            changed[key] = value
            with self.assertRaises(AssertionError):
                capture.rows(changed)

    def test_all_caller_definitions_retained(self):
        definitions = capture.definitions(self.data)['fixtures']
        self.assertEqual(len(definitions), 32)
        self.assertTrue(all((row['width'], row['height']) == (600, 300) for row in definitions))
        self.assertTrue(any(row['configuration'].get('height') == 0 for row in definitions))
        self.assertTrue(any(row['configuration']['itemMode'] == 'many' for row in definitions))

    def actual(self, row):
        return dict(row, actions=row['calls'], labelActions=0)

    def test_closed_state_compared(self):
        row = self.rows[0]
        self.assertEqual(capture.observations(row, self.actual(row))['stateStatus'], 'passed')
        for key in ['configuration', 'appearance', 'textScale', 'dpr', 'title', 'enabled', 'actions', 'labelActions']:
            actual = self.actual(row)
            actual[key] = None
            self.assertEqual(capture.observations(row, actual)['stateStatus'], 'failed', key)

    def test_metadata_frame_not_silently_discarded(self):
        row = self.rows[0]
        actual = self.actual(row)
        actual['frames'] = dict(row['frames'])
        del actual['frames']['label']
        observation = capture.observations(row, actual)
        self.assertEqual(observation['nativeFrameStatus'], 'failed')
        self.assertEqual(observation['bodyCallerFrameStatus'], 'passed')


if __name__ == '__main__':
    unittest.main()
