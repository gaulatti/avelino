import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('font_modifier_source', ROOT / 'scripts/verify-font-modifier-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class FontModifierSourceContracts(unittest.TestCase):
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
            row = next(row for row in replay['outputs'] if row['file'] == 'captures.json')
            row['originalSha256'] = row['replaySha256'] = report['files'][name]
            replay_path.write_text(json.dumps(replay, indent=2) + '\n')
            report['files']['clean-replay.json'] = hashlib.sha256(replay_path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(report, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            source.verify(self.directory)

    def test_complete_source_corpus(self):
        self.assertEqual(source.verify(self.directory), dict(closedGroups=864, updateHistories=24,
                                                           sourceReplayFiles=2761, accepted=False))

    def test_source_cannot_accept_linux(self):
        self.edit('investigation.json', lambda data: data.update(accepted=True))
        self.rejected()

    def test_missing_context(self):
        self.edit('captures/captures.json', lambda data: data['captures'].pop())
        self.rejected()

    def test_duplicate_context(self):
        self.edit('captures/captures.json', lambda data: data['captures'].__setitem__(1, data['captures'][0]))
        self.rejected()

    def test_weight_cannot_be_relabelled(self):
        self.edit('captures/captures.json', lambda data: data['captures'][0]['configuration'].update(weight='regular'))
        self.rejected()

    def test_flat_children_cannot_collapse(self):
        def collapse(data):
            row = next(row for row in data['captures'] if row['configuration']['fixture'] == 'multi-parent-hstack')
            for state in row['states'][1:]:
                state['partInstances']['styled'] = state['partInstances']['styled'][:1]
                state['partInstances']['root'] = state['partInstances']['root'][:1]
        self.edit('captures/captures.json', collapse)
        self.rejected()

    def test_font_override_cannot_grow_with_ambient_scale(self):
        def scale(data):
            row = next(row for row in data['captures'] if row['configuration']['fixture'] == 'content-own-font' and row['textScale'] == 1.5)
            for state in row['states'][1:]:
                state['partInstances']['label'][0]['height'] *= 1.5
        self.edit('captures/captures.json', scale)
        self.rejected()

    def test_live_updates_cannot_recreate_caller(self):
        def recreate(data):
            for history in data['histories']:
                history['steps'][3]['state']['callerInstances'] += 1
                history['steps'][3]['state']['appearances'] += 1
        self.edit('captures/captures.json', recreate)
        self.rejected()

    def test_live_history_cannot_omit_middle_step(self):
        self.edit('captures/captures.json', lambda data: data['histories'][0]['steps'].pop(3))
        self.rejected()

    def test_precompiled_input_rejected(self):
        self.edit('tooling-provenance.json', lambda data: data.update(compiledInputs=['Sabella.o']))
        self.rejected()

    def test_replay_requires_fresh_source_build(self):
        self.edit('replay-build/source-build-result.json', lambda data: data.update(libraryBuiltFromSources=False))
        self.rejected()

    def test_incomplete_replay_rejected(self):
        self.edit('clean-replay.json', lambda data: data['outputs'].pop())
        self.rejected()

    def test_unsealed_file_rejected(self):
        (self.directory / 'unexpected.json').write_text('{}\n')
        self.rejected()

    def test_unrequested_baselines_cannot_be_accepted_as_complete(self):
        self.edit('investigation.json', lambda data: data.update(baselineScope='All repeated parts measured'))
        self.rejected()


if __name__ == '__main__':
    unittest.main()
