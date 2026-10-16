import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('modal_input_source', ROOT / 'scripts/verify-modal-input-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class ModalInputSourceContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / 'source'
        shutil.copytree(source.DIRECTORY, self.directory)

    def edit(self, name, mutate):
        path = self.directory / name
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value, indent=2) + '\n')
        if name == 'investigation.json':
            return
        manifest = self.directory / 'investigation.json'
        report = json.loads(manifest.read_text())
        report['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        if name.startswith('outputs/'):
            replay_path = self.directory / 'clean-replay.json'
            replay = json.loads(replay_path.read_text())
            row = next(r for r in replay['outputs'] if r['file'] == name)
            self.assertTrue(row['identical'])
            row['originalSha256'] = row['replaySha256'] = report['files'][name]
            replay_path.write_text(json.dumps(replay, indent=2) + '\n')
            report['files']['clean-replay.json'] = hashlib.sha256(replay_path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(report, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            source.verify(self.directory)

    def edit_input(self, mutate):
        self.edit('outputs/input.json', mutate)

    def test_complete_input_facts_and_explicit_pixel_limits(self):
        result = source.verify(self.directory)
        self.assertEqual((result['clippingQueries'], result['glyphQueries'], result['quarantinedImages']), (170, 568, 2))

    def test_native_observations_cannot_approve_linux(self):
        self.edit('investigation.json', lambda d: d.update(accepted=True))
        self.rejected()

    def test_replay_differences_cannot_be_declared_identical(self):
        self.edit('clean-replay.json', lambda d: d.update(fullByteIdentity=True))
        self.rejected()

    def test_quarantine_cannot_be_dropped(self):
        self.edit('investigation.json', lambda d: d.update(pixelQuarantine=[]))
        self.rejected()

    def test_caller_field_witness_cannot_be_declared_transparent(self):
        self.edit('investigation.json', lambda d: d.update(sheetEditorWitnessTransparent=True))
        self.rejected()

    def test_header_identity_cannot_approve_the_field_body(self):
        self.edit('outputs/witness-limit.json', lambda d: d.update(suitableForFullSheetPixelAcceptance=True))
        self.rejected()

    def test_visual_clip_cannot_suppress_outside_actions(self):
        def suppress(data):
            row = next(q for q in data['queries'] if q['fixture'] == 'wide' and not q['insideModalRect'] and q['calls'])
            row['calls'] = []
        self.edit_input(suppress)
        self.rejected()

    def test_ghost_padding_cannot_become_an_activation_target(self):
        def expand(data):
            row = next(q for q in data['queries'] if q['fixture'] == 'close-480-ltr' and q['insideTargetRect'] and q['windowVisible'])
            row['windowVisible'] = False
        self.edit_input(expand)
        self.rejected()

    def test_missing_glyph_profile_is_rejected(self):
        self.edit('outputs/hit-profiles.json', lambda d: d['profiles'].pop())
        self.rejected()

    def test_glyph_hit_result_cannot_be_rewritten(self):
        self.edit('outputs/hit-profiles.json', lambda d: d['profiles'][0]['samples'][0].update(activated=False))
        self.rejected()

    def test_retained_window_cannot_reset_caller_state(self):
        self.edit_input(lambda d: d['traces'][0]['events'][4].update(calls=['counter:1', 'counter:1']))
        self.rejected()

    def test_reopened_sheet_must_start_fresh_local_state(self):
        self.edit_input(lambda d: d['traces'][1]['events'][4]['state'].update(calls=['counter:1', 'counter:2']))
        self.rejected()

    def test_owner_binding_must_survive_sheet_reopening(self):
        self.edit_input(lambda d: d['traces'][2]['events'][3].update(text='Draft edition'))
        self.rejected()

    def test_qobject_destruction_cannot_replace_source_disappear_callback(self):
        self.edit_input(lambda d: d['traces'][1]['events'][2]['state'].update(disappears=1))
        self.rejected()

    def test_unsealed_files_are_rejected(self):
        (self.directory / 'unexpected.json').write_text('{}\n')
        self.rejected()


if __name__ == '__main__':
    unittest.main()
