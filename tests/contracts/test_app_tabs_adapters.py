"""Keep every native tab-bar input, action and selected display state in replay."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('app_tabs_capture', ROOT / 'scripts/capture-app-tabs.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class AppTabsAdapters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(capture.PROJECTION.read_text())
        cls.rows = capture.rows(cls.data)

    def test_entire_native_corpus_retained(self):
        self.assertEqual(len(self.rows), 1208)
        self.assertEqual(sum(r['kind'] == 'closed' for r in self.rows), 344)
        self.assertEqual(sum(r['kind'] == 'history' for r in self.rows), 864)

    def test_every_context_has_151_observations(self):
        for context in capture.CONTEXTS:
            self.assertEqual(sum(r['context'] == capture.prefix(*context) for r in self.rows), 151)

    def test_missing_context_rejected(self):
        changed = copy.deepcopy(self.data)
        changed['closed'].pop()
        with self.assertRaises(AssertionError):
            capture.rows(changed)

    def test_caller_dimensions_stay_separate_from_window(self):
        definitions = capture.definitions(self.data)['fixtures']
        self.assertEqual(len(definitions), 43)
        self.assertTrue(all((r['width'], r['height']) == (640, 400) for r in definitions))
        zero = next(r for r in definitions if r['id'] == 'width-0')
        self.assertEqual(zero['tabWidth'], 0)
        self.assertIsNone(zero['tabHeight'])

    def test_badges_keep_signed_integer_precision(self):
        entries = [t for r in self.rows for t in r['configuration']['tabs']]
        badges = {t.get('badge') for t in entries}
        self.assertIn('-9223372036854775808', badges)
        self.assertIn('9223372036854775807', badges)

    def test_canonical_selection_has_original_tab_value(self):
        row = next(r for r in self.rows if r['configuration']['id'] == 'canonical' and r['kind'] == 'closed')
        self.assertEqual(row['selection'], 'e\u0301')
        self.assertEqual(row['selectedValues'], ['é'])

    def test_selected_display_state_is_compared(self):
        row = next(r for r in self.rows if r['configuration']['id'] == 'width-300' and r['kind'] == 'closed')
        actual = dict(row, selectedValues=[])
        observed = capture.observations(row, actual)
        self.assertEqual(observed['stateStatus'], 'failed')
        self.assertIn('selectedValues', observed['stateErrors'])

    def test_source_ax_press_is_not_fabricated_as_delivered(self):
        steps = [r for r in self.rows if r.get('step') == 'ax-press-second']
        self.assertEqual(len(steps), 48)
        self.assertTrue(all(not action['available'] and action['returned'] is None for r in steps for action in r['actions']))

    def test_owner_requests_not_replaced_by_expected_selection(self):
        row = next(r for r in self.rows if r['configuration']['id'] == 'owner-observe' and r.get('step') == 'click-second')
        self.assertEqual(row['requests'], ['b'])
        self.assertEqual(row['selection'], 'a')
        self.assertEqual(row['selectedValues'], ['a'])

    def test_empty_step_omits_removed_probe_frames(self):
        row = next(r for r in self.rows if r.get('step') == 'empty')
        self.assertEqual(set(row['frames']), {'bar', 'caller'})
        self.assertEqual(row['selectedValues'], [])


if __name__ == '__main__':
    unittest.main()
