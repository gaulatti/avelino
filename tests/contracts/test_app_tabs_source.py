"""Keep native tab-bar observations separate from Linux and reader acceptance."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('app_tabs_source', ROOT / 'scripts/verify-app-tabs-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class AppTabsSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((source.DIRECTORY / 'investigation.json').read_text())

    def rejected(self, edit):
        value = copy.deepcopy(self.report)
        edit(value)
        with self.assertRaises(AssertionError):
            source.validate_report(value)

    def test_sealed_native_record_recomputes(self):
        source.verify()

    def test_cannot_accept_without_linux(self):
        self.rejected(lambda r: r.update(accepted=True))

    def test_cannot_replace_reference(self):
        self.rejected(lambda r: r.update(reference='new'))

    def test_cannot_replace_source_tree(self):
        self.rejected(lambda r: r.update(tree='new'))

    def test_cannot_drop_binding_histories(self):
        self.rejected(lambda r: r['summary'].update(histories=8))

    def test_cannot_claim_unobserved_accessibility(self):
        self.rejected(lambda r: r['summary'].update(nativeAccessibilityButtons=3))

    def test_cannot_claim_unavailable_accessibility_press(self):
        self.rejected(lambda r: r['summary'].update(availableAccessibilityPresses=48))

    def test_cannot_drop_reader_gate(self):
        self.rejected(lambda r: r['remainingAcceptance'].remove('readers'))

    def test_cannot_approve_tolerance(self):
        self.rejected(lambda r: r.update(tolerance='one pixel'))

    def test_cannot_rewrite_expected_images(self):
        self.rejected(lambda r: r.update(expectedImagesChanged=True))

    def test_cannot_approve_exception(self):
        self.rejected(lambda r: r.update(approvedExceptions=['symbols']))

    def test_cannot_claim_independent_machine_replay(self):
        self.rejected(lambda r: r['sourceOnlyArtifact'].update(downloadAvailability='verified'))

    def test_removed_views_do_not_become_current_geometry(self):
        state = dict(configuration=dict(tabs=[]), frames={
            'bar': dict(x=0, y=0, width=0, height=5),
            'button-0': dict(x=0, y=0, width=100, height=54)})
        self.assertEqual(source.active_frames(state), {'bar': state['frames']['bar']})


if __name__ == '__main__':
    unittest.main()
