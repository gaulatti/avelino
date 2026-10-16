import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('surface_modifier_source', ROOT / 'scripts/verify-surface-modifier-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class SurfaceModifierSourceContracts(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / 'source'
        shutil.copytree(source.DIRECTORY, self.directory)

    def edit(self, name, mutate):
        path = self.directory / name
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value, indent=2) + '\n')
        if name == 'investigation.json':
            return
        report_path = self.directory / 'investigation.json'
        report = json.loads(report_path.read_text())
        report['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        if name == 'captures/captures.json':
            replay_path = self.directory / 'clean-replay.json'
            replay = json.loads(replay_path.read_text())
            row = next(row for row in replay['outputs'] if row['file'] == 'captures.json')
            row['originalSha256'] = row['replaySha256'] = report['files'][name]
            replay_path.write_text(json.dumps(replay, indent=2) + '\n')
            report['files']['clean-replay.json'] = hashlib.sha256(replay_path.read_bytes()).hexdigest()
        report_path.write_text(json.dumps(report, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            source.verify(self.directory)

    def test_complete_native_source_corpus(self):
        self.assertEqual(source.verify(self.directory), dict(closedGroups=416, updateHistories=30,
                                                           sourceReplayFiles=1845, accepted=False))

    def test_native_source_cannot_accept_linux(self):
        self.edit('investigation.json', lambda data: data.update(accepted=True))
        self.rejected()

    def test_no_physical_gate_can_close_from_hosted_images(self):
        self.edit('investigation.json', lambda data: data['acceptanceGates'].update(physicalInput='passed'))
        self.rejected()

    def test_missing_context_rejected(self):
        self.edit('captures/captures.json', lambda data: data['captures'].pop())
        self.rejected()

    def test_duplicate_context_rejected(self):
        self.edit('captures/captures.json', lambda data: data['captures'].__setitem__(1, data['captures'][0]))
        self.rejected()

    def test_flat_children_cannot_collapse_to_one_surface(self):
        def collapse(data):
            row = next(row for row in data['captures'] if row['configuration']['fixture'] == 'multi-parent-hstack')
            for state in row['states'][1:]:
                for key in ['styled', 'root']:
                    state['partInstances'][key] = state['partInstances'][key][:1]
        self.edit('captures/captures.json', collapse)
        self.rejected()

    def test_native_surface_cannot_change_bare_caller_frame(self):
        def move(data):
            row = next(row for row in data['captures'] if row['configuration']['fixture'] == 'content-rectangle')
            row['states'][3]['partInstances']['caller'][0]['x'] += 1
        self.edit('captures/captures.json', move)
        self.rejected()

    def test_radius_update_cannot_recreate_caller(self):
        def recreate(data):
            data['histories'][0]['steps'][1]['state']['callerInstances'] += 1
            data['histories'][0]['steps'][1]['state']['appearances'] += 1
        self.edit('captures/captures.json', recreate)
        self.rejected()

    def test_live_trace_cannot_skip_middle_step(self):
        self.edit('captures/captures.json', lambda data: data['histories'][0]['steps'].pop(2))
        self.rejected()

    def test_empty_baseline_maps_are_not_baseline_acceptance(self):
        self.edit('investigation.json', lambda data: data.update(baselineScope='All text baselines measured'))
        self.rejected()

    def test_prebuilt_library_cannot_replace_source_rebuild(self):
        self.edit('replay-build/source-build-result.json', lambda data: data.update(prebuiltLibraryInputs=True))
        self.rejected()

    def test_direct_initializer_must_remain_inaccessible(self):
        self.edit('api-check/result.json', lambda data: data['cases']['direct-initializer'].update(exitCode=0))
        self.rejected()

    def test_incomplete_replay_rejected(self):
        self.edit('clean-replay.json', lambda data: data['outputs'].pop())
        self.rejected()

    def test_unsealed_file_rejected(self):
        (self.directory / 'unexpected.json').write_text('{}\n')
        self.rejected()


if __name__ == '__main__':
    unittest.main()
