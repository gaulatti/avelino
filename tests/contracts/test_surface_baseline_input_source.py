import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('surface_baseline_input_source', ROOT / 'scripts/verify-surface-baseline-input-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class SurfaceBaselineInputSourceContracts(unittest.TestCase):
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
        if name in ['baseline/baselines.json', 'input/input.json']:
            replay_path = self.directory / 'clean-replay.json'
            replay = json.loads(replay_path.read_text())
            row = next(row for row in replay['outputs'] if row['file'] == name)
            row['originalSha256'] = row['replaySha256'] = report['files'][name]
            replay_path.write_text(json.dumps(replay, indent=2) + '\n')
            report['files']['clean-replay.json'] = hashlib.sha256(replay_path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(report, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            source.verify(self.directory)

    def test_complete_native_evidence_remains_unaccepted(self):
        result = source.verify(self.directory)
        self.assertEqual((result['baselineGroups'], result['inputProfiles'], result['sourceReplayFiles'], result['accepted']),
                         (440, 288, 3778, False))
        self.assertGreater(result['borderBlockedSamples'], 0)
        self.assertGreater(result['publicHitsOutsideCallerFrame'], 0)

    def test_source_cannot_accept_linux(self):
        self.edit('investigation.json', lambda data: data.update(accepted=True))
        self.rejected()

    def test_synthetic_input_cannot_accept_physical_input(self):
        self.edit('investigation.json', lambda data: data['acceptanceGates'].update(physicalInput='passed'))
        self.rejected()

    def test_missing_baseline_context(self):
        self.edit('baseline/baselines.json', lambda data: data['captures'].pop())
        self.rejected()

    def test_negative_explicit_guide_cannot_be_clamped(self):
        def clamp(data):
            row = next(r for r in data['captures'] if r['configuration']['fixture'] == 'guide--5')
            for state in row['states'][1:3]:
                for key in ['caller', 'styled', 'root']:
                    state['guideQueries'][key][0]['value'] = 0
        self.edit('baseline/baselines.json', clamp)
        self.rejected()

    def test_multiple_emitted_guides_cannot_be_collapsed(self):
        def collapse(data):
            row = next(r for r in data['captures'] if r['configuration']['content'] == 'multi')
            for state in row['states'][1:]:
                state['partInstances']['root'].pop()
        self.edit('baseline/baselines.json', collapse)
        self.rejected()

    def test_unreached_sample_cannot_be_reported_as_a_hit(self):
        def forge(data):
            sample = data['profiles'][0]['samples'][0][0]
            sample['activated'] = 0
        self.edit('input/input.json', forge)
        self.rejected()

    def test_missing_input_point_rejected(self):
        self.edit('input/input.json', lambda data: data['profiles'][0]['samples'][0].pop())
        self.rejected()

    def test_disabled_caller_cannot_activate(self):
        def activate(data):
            row = next(r for r in data['profiles'] if r['configuration']['disabled'])
            sample = row['samples'][0][0]
            sample.update(activated=1, afterUp=1, afterSettle=1)
        self.edit('input/input.json', activate)
        self.rejected()

    def test_precompiled_input_rejected(self):
        self.edit('tooling-provenance.json', lambda data: data.update(compiledInputs=['Sabella.o']))
        self.rejected()

    def test_incomplete_replay_rejected(self):
        self.edit('clean-replay.json', lambda data: data['outputs'].pop())
        self.rejected()

    def test_original_probe_failures_cannot_be_hidden(self):
        self.edit('diagnostics/probe-correction.json', lambda data: data['contexts'].pop())
        self.rejected()

    def test_resource_termination_cannot_be_called_success(self):
        self.edit('diagnostics/original-build/commands.json', lambda data: data[-1].update(exitCode=0))
        self.rejected()

    def test_partial_input_cannot_be_called_complete(self):
        self.edit('diagnostics/resource-attempts.json', lambda data: data['attempts'][0].update(inputComplete=True))
        self.rejected()

    def test_unsealed_file_rejected(self):
        (self.directory / 'unexpected.json').write_text('{}\n')
        self.rejected()


if __name__ == '__main__':
    unittest.main()
