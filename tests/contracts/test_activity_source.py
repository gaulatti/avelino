import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('activity_source', ROOT / 'scripts/verify-activity-source.py')
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


class ActivitySourceIntegrity(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='avelino-activity-source-')
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name) / 'evidence'
        shutil.copytree(verifier.DIRECTORY, self.directory)

    def change(self, name, mutation):
        path = self.directory / name
        data = json.loads(path.read_text())
        mutation(data)
        path.write_text(json.dumps(data, indent=2) + '\n')
        # Re-seal altered JSON and its claimed replay so semantic assertions,
        # rather than only the outer file digest, must reject the change.
        comparison = self.directory / 'clean-replay-comparison.json'
        if name != comparison.name:
            replay = json.loads(comparison.read_text())
            for row in replay['outputs']:
                if row['file'] == name:
                    row['originalSha256'] = row['replaySha256'] = verifier.digest(path)
            comparison.write_text(json.dumps(replay, indent=2) + '\n')
        manifest = self.directory / 'investigation.json'
        report = json.loads(manifest.read_text())
        report['files'][name] = verifier.digest(path)
        report['files'][comparison.name] = verifier.digest(comparison)
        manifest.write_text(json.dumps(report, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)

    def test_preserved_source_replay_is_intact(self):
        self.assertEqual(verifier.verify(self.directory)['cleanReplayIdenticalFiles'], 1753)

    def test_duplicate_capture_cannot_replace_a_context(self):
        self.change('captures/captures.json', lambda d: d['captures'].__setitem__(0, d['captures'][1]))
        self.rejected()

    def test_unknown_fixture_cannot_replace_a_required_fixture(self):
        def mutate(data):
            for row in data['captures']:
                if row['fixture'] == 'spaces':
                    row['fixture'] = 'invented-case'
        self.change('captures/captures.json', mutate)
        self.rejected()

    def test_requested_bitmap_scale_cannot_claim_physical_display(self):
        self.change('captures/captures.json', lambda d: d['captures'][0]['native'].update(backingDpr=1))
        self.rejected()

    def test_outer_font_cannot_replace_fixed_title_font(self):
        def mutate(data):
            row = next(r for r in data['captures'] if r['fixture'] == 'parent-font32')
            row['witness']['fonts']['title']['pointSize'] = 32
        self.change('captures/captures.json', mutate)
        self.rejected()

    def test_empty_labels_cannot_collapse_their_line_boxes(self):
        def mutate(data):
            row = next(r for r in data['captures'] if r['fixture'] == 'all-empty')
            row['witness']['parts']['detail']['height'] = 0
        self.change('captures/captures.json', mutate)
        self.rejected()

    def test_duplicate_dense_query_cannot_replace_an_offered_width(self):
        self.change('layout-queries.json', lambda d: d['queries'].__setitem__(0, d['queries'][1]))
        self.rejected()

    def test_dense_nested_overflow_cannot_be_clamped_to_offered_width(self):
        def mutate(data):
            for row in data['queries']:
                if row['actions'] == 'nested' and row['textScale'] == 1.5:
                    width = max(141, row['proposalWidth'])
                    for bounds in [row['componentRect'], row['witnessRoot'], row['witnessRects']['root']]:
                        bounds['width'] = width
        self.change('layout-queries.json', mutate)
        self.rejected()

    def test_body_click_cannot_invoke_caller_action(self):
        def mutate(data):
            trace = next(t for t in data['traces'] if t['fixture'] == 'ordinary')
            next(e for e in trace['events'] if e['action'] == 'click-title')['state']['calls'] = ['review']
        self.change('behavior/behavior.json', mutate)
        self.rejected()

    def test_disabled_during_press_cannot_invoke_release(self):
        def mutate(data):
            trace = next(t for t in data['traces'] if t['fixture'] == 'during-down-disable')
            trace['events'][-1]['state']['calls'] = ['review']
        self.change('behavior/behavior.json', mutate)
        self.rejected()

    def test_producer_update_cannot_reset_local_action_state(self):
        def mutate(data):
            trace = next(t for t in data['traces'] if t['fixture'] == 'counter')
            next(e for e in trace['events'] if e['action'] == 'producer-update')['state']['actionValues'] = {'counter': 0}
        self.change('behavior/behavior.json', mutate)
        self.rejected()

    def test_recreated_action_cannot_retain_destroyed_local_state(self):
        def mutate(data):
            trace = next(t for t in data['traces'] if t['fixture'] == 'counter')
            next(e for e in trace['events'] if e['action'] == 'restore-actions')['state']['actionValues'] = {'counter': 2}
        self.change('behavior/behavior.json', mutate)
        self.rejected()

    def test_compiled_product_cannot_replace_source_input(self):
        self.change('tooling-provenance.json', lambda d: d.update(compiledInputs=['Sabella.o']))
        self.rejected()

    def test_duplicate_replay_row_cannot_replace_missing_output(self):
        self.change('clean-replay-comparison.json', lambda d: d['outputs'].__setitem__(0, d['outputs'][1]))
        self.rejected()

    def test_source_investigation_cannot_approve_linux_parity(self):
        path = self.directory / 'investigation.json'
        report = json.loads(path.read_text())
        report['accepted'] = True
        path.write_text(json.dumps(report))
        self.rejected()


if __name__ == '__main__':
    unittest.main()
