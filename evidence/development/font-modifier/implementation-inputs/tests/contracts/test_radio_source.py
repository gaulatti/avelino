import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('radio_source', ROOT / 'scripts/verify-radio-source.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class RadioSourceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'source'
        shutil.copytree(verifier.DIRECTORY, self.directory)

    def change(self, name, operation):
        path = self.directory / name
        data = json.loads(path.read_text())
        operation(data)
        path.write_text(json.dumps(data))
        manifest = self.directory / 'investigation.json'
        report = json.loads(manifest.read_text())
        report['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(report))

    def test_preserved_native_source_replay_is_intact(self):
        self.assertEqual(verifier.verify(self.directory)['sourceReplayIdenticalFiles'], 1358)

    def test_duplicate_capture_cannot_replace_required_fixture(self):
        self.change('captures/captures.json', lambda data: data['captures'].__setitem__(0, data['captures'][1]))
        with self.assertRaisesRegex(AssertionError, 'capture coverage'):
            verifier.verify(self.directory)

    def test_bitmap_scale_cannot_claim_physical_display(self):
        self.change('captures/captures.json', lambda data: data['captures'][0]['nativeWindowState'].update(backingDpr=1))
        with self.assertRaisesRegex(AssertionError, 'Physical/focus state'):
            verifier.verify(self.directory)

    def test_cached_object_cannot_claim_fresh_source_replay(self):
        self.change('tooling-provenance.json', lambda data: data.update(compiledInputs=['Sabella.o']))
        with self.assertRaisesRegex(AssertionError, 'Compiled inputs'):
            verifier.verify(self.directory)

    def test_native_canonical_value_cannot_become_unselected(self):
        def mutate(data):
            row = next(r for r in data['captures'] if r['fixture'] == 'canonical-value')
            row['options'][0]['selected'] = False
        self.change('captures/captures.json', mutate)
        with self.assertRaisesRegex(AssertionError, 'canonical String identity'):
            verifier.verify(self.directory)

    def test_qt_unicode_mismatch_cannot_be_reported_as_success(self):
        self.change('qt-string-identity.json', lambda data: data.update(mismatches=0))
        with self.assertRaisesRegex(AssertionError, 'normalization mismatch'):
            verifier.verify(self.directory)

    def test_compatibility_character_cannot_be_canonically_equal(self):
        def mutate(data):
            row = next(r for r in data['results'] if r['kind'] == 'explicit-string' and r['left'] == [64257])
            row['equal'] = True
        self.change('native-string-identity.json', mutate)
        with self.assertRaisesRegex(AssertionError, 'canonical identity'):
            verifier.verify(self.directory)

    def test_selected_click_cannot_drop_native_setter(self):
        def mutate(data):
            trace = next(t for t in data['traces'] if t['fixture'] == 'vertical')
            trace['actions'][0]['requests'] = []
        self.change('behavior/behavior.json', mutate)
        with self.assertRaisesRegex(AssertionError, 'request changed'):
            verifier.verify(self.directory)

    def test_observe_only_binding_cannot_be_claimed_as_model_write(self):
        def mutate(data):
            trace = next(t for t in data['traces'] if t['fixture'] == 'observe-only')
            trace['actions'][0]['modelWrites'] = trace['actions'][0]['requests']
        self.change('behavior/behavior.json', mutate)
        with self.assertRaisesRegex(AssertionError, 'Binding ownership'):
            verifier.verify(self.directory)

    def test_disabled_during_press_cannot_emit_release_request(self):
        def mutate(data):
            phase = next(p for p in data['pointerPhases'] if p['fixture'] == 'disable-during-down')
            phase['afterUp']['requests'] = ['daily']
        self.change('behavior/behavior.json', mutate)
        with self.assertRaisesRegex(AssertionError, 'release cancellation'):
            verifier.verify(self.directory)

    def test_inactive_gap_cannot_become_clickable(self):
        def mutate(data):
            trace = next(t for t in data['traces'] if t['fixture'] == 'vertical')
            trace['actions'][3]['requests'] = ['weekly']
        self.change('behavior/behavior.json', mutate)
        with self.assertRaisesRegex(AssertionError, 'request changed'):
            verifier.verify(self.directory)

    def test_hosting_ax_group_cannot_claim_reader_acceptance(self):
        self.change('native-accessibility.json', lambda data: data.update(screenReaderVerified=True))
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)

    def test_duplicate_replay_output_cannot_replace_missing_output(self):
        self.change('clean-replay.json', lambda data: data['results'].__setitem__(0, data['results'][1]))
        with self.assertRaisesRegex(AssertionError, 'Replay output coverage'):
            verifier.verify(self.directory)


if __name__ == '__main__':
    unittest.main()
