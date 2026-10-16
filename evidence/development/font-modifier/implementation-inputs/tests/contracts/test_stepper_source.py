import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('stepper_source', ROOT / 'scripts/verify-stepper-source.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class StepperSourceIntegrity(unittest.TestCase):
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
        self.assertEqual(verifier.verify(self.directory)['sourceReplayIdenticalFiles'], 1168)

    def test_duplicate_capture_cannot_replace_a_required_fixture(self):
        self.change('captures/captures.json', lambda data: data['captures'].__setitem__(0, data['captures'][1]))
        with self.assertRaisesRegex(AssertionError, 'capture coverage'):
            verifier.verify(self.directory)

    def test_bitmap_scale_cannot_claim_a_physical_display(self):
        self.change('captures/captures.json', lambda data: data['captures'][0]['nativeWindowState'].update(backingDpr=1))
        with self.assertRaisesRegex(AssertionError, 'Physical/focus state'):
            verifier.verify(self.directory)

    def test_cached_object_cannot_claim_a_fresh_source_replay(self):
        self.change('tooling-provenance.json', lambda data: data.update(compiledInputs=['Sabella.o']))
        with self.assertRaisesRegex(AssertionError, 'Compiled inputs'):
            verifier.verify(self.directory)

    def test_lossy_integer_cannot_replace_a_native_value(self):
        self.change('captures/captures.json', lambda data: data['captures'][0].update(value=9007199254740992))
        with self.assertRaisesRegex(AssertionError, 'Lossless Int64'):
            verifier.verify(self.directory)

    def test_observe_only_binding_cannot_be_claimed_as_a_model_write(self):
        def mutate(data):
            trace = next(t for t in data['traces'] if t['fixture'] == 'observe-only')
            trace['actions'][0]['modelWrites'] = trace['actions'][0]['requests']
        self.change('behavior/behavior.json', mutate)
        with self.assertRaisesRegex(AssertionError, 'Binding ownership'):
            verifier.verify(self.directory)

    def test_zero_step_cannot_drop_the_native_setter_call(self):
        def mutate(data):
            trace = next(t for t in data['traces'] if t['fixture'] == 'step-zero')
            trace['actions'][0]['requests'] = []
        self.change('behavior/behavior.json', mutate)
        with self.assertRaisesRegex(AssertionError, 'Native request arithmetic'):
            verifier.verify(self.directory)

    def test_clamp_cannot_hide_native_action_overflow(self):
        def mutate(data):
            trap = next(t for t in data['cases'] if t['case'] == 'increment-overflow')
            trap.update(returnCode=0, trapped=False)
        self.change('traps/traps.json', mutate)
        with self.assertRaisesRegex(AssertionError, 'overflow/range failure'):
            verifier.verify(self.directory)

    def test_duplicate_replay_output_cannot_replace_a_missing_output(self):
        self.change('clean-replay.json', lambda data: data['results'].__setitem__(0, data['results'][1]))
        with self.assertRaisesRegex(AssertionError, 'Replay output coverage'):
            verifier.verify(self.directory)

    def test_native_ui_failure_cannot_be_claimed_as_catalog_acceptance(self):
        self.change('catalog-investigation.json', lambda data: data.update(accepted=True))
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)


if __name__ == '__main__':
    unittest.main()
