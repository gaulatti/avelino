import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('button_style_source', ROOT / 'scripts/verify-button-style-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class ButtonStyleSourceContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / 'source'
        shutil.copytree(source.DIRECTORY, self.directory)

    def edit(self, name, mutate):
        path = self.directory / name
        data = json.loads(path.read_text())
        mutate(data)
        path.write_text(json.dumps(data, indent=2) + '\n')
        if name == 'investigation.json':
            return
        manifest = self.directory / 'investigation.json'
        report = json.loads(manifest.read_text())
        report['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        if name == 'captures/captures.json':
            replay_path = self.directory / 'clean-replay.json'
            replay = json.loads(replay_path.read_text())
            row = next(r for r in replay['outputs'] if r['file'] == 'captures.json')
            row['originalSha256'] = row['replaySha256'] = report['files'][name]
            replay_path.write_text(json.dumps(replay, indent=2) + '\n')
            report['files']['clean-replay.json'] = hashlib.sha256(replay_path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(report, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            source.verify(self.directory)

    def test_complete_source_corpus(self):
        self.assertEqual(source.verify(self.directory), dict(closedGroups=704, sourceReplayFiles=2113,
                                                           repeatedPartContexts=24, pointerPhases=13, accepted=False))

    def test_source_cannot_accept_linux(self):
        self.edit('investigation.json', lambda d: d.update(accepted=True))
        self.rejected()

    def test_missing_context(self):
        self.edit('captures/captures.json', lambda d: d['captures'].pop())
        self.rejected()

    def test_duplicate_context(self):
        self.edit('captures/captures.json', lambda d: d['captures'].__setitem__(1, d['captures'][0]))
        self.rejected()

    def test_flat_label_cannot_collapse_to_one_body(self):
        def collapsed(d):
            row = next(r for r in d['captures'] if r['configuration']['fixture'] == 'multi-parent-hstack')
            for state in row['states'][1:]:
                for key in ['body', 'root']:
                    state['partInstances'][key] = state['partInstances'][key][:1]
        self.edit('captures/captures.json', collapsed)
        self.rejected()

    def test_empty_label_cannot_allocate_control(self):
        def allocated(d):
            row = next(r for r in d['captures'] if r['configuration']['fixture'] == 'content-empty')
            for state in row['states'][1:]:
                state['partInstances']['body'] = [dict(x=302, y=180, width=36, height=40)]
        self.edit('captures/captures.json', allocated)
        self.rejected()

    def test_zero_offer_is_distinct_from_body_width(self):
        def forced(d):
            row = next(r for r in d['captures'] if r['configuration']['fixture'] == 'offer-0')
            for state in row['states'][1:]:
                state['partInstances']['root'] = state['partInstances']['body']
        self.edit('captures/captures.json', forced)
        self.rejected()

    def test_padding_cannot_drift(self):
        def padded(d):
            for state in d['captures'][0]['states'][1:]:
                state['partInstances']['body'][0]['width'] += 2
        self.edit('captures/captures.json', padded)
        self.rejected()

    def test_parent_layout_cannot_union_flat_children(self):
        def unioned(d):
            row = next(r for r in d['captures'] if r['configuration']['fixture'] == 'multi-parent-hstack')
            for state in row['states'][1:]:
                state['partInstances']['parent'][0]['width'] -= 11
        self.edit('captures/captures.json', unioned)
        self.rejected()

    def test_variant_update_cannot_reset_caller(self):
        def reset(d):
            next(c for c in d['commands'] if c['action'] == 'variant')['count'] = 0
        self.edit('input-key-window/state.json', reset)
        self.rejected()

    def test_prebuilt_input_rejected(self):
        self.edit('tooling-provenance.json', lambda d: d.update(compiledInputs=['Sabella.o']))
        self.rejected()

    def test_app_rebuild_cannot_claim_automatic_live_replay(self):
        self.edit('input-clean-build/source-build-result.json', lambda d: d.update(automaticLivePixelReplay=True))
        self.rejected()

    def test_inactive_held_samples_cannot_claim_active_input(self):
        self.edit('input/row-pressed-analysis.json', lambda d: d['phases'][0].update(applicationActive=True, windowKey=True))
        self.rejected()

    def test_active_input_needs_key_window_samples(self):
        def non_key(d):
            next(c for c in d['captures'] if c['path'] == 'sample-0019.png')['windowKey'] = False
        self.edit('input-key-window/state.json', non_key)
        self.rejected()

    def test_visual_clip_cannot_become_input_clip(self):
        self.edit('input-key-window/observations.json', lambda d: d.update(visualClipIsInputClip=True))
        self.rejected()

    def test_cross_label_drag_cannot_activate(self):
        self.edit('input-key-window/observations.json', lambda d: d['rowPointerPhases'][2].update(delta=1))
        self.rejected()

    def test_keyboard_acceptance_stays_pending(self):
        self.edit('investigation.json', lambda d: d.update(activeWindowKeyboardAcceptance='passed'))
        self.rejected()

    def test_incomplete_replay_rejected(self):
        self.edit('clean-replay.json', lambda d: d['outputs'].pop())
        self.rejected()

    def test_unsealed_file_rejected(self):
        (self.directory / 'unexpected.json').write_text('{}\n')
        self.rejected()


if __name__ == '__main__':
    unittest.main()
