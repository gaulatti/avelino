import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('font_baseline_source', ROOT / 'scripts/verify-font-baseline-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class FontBaselineSourceContracts(unittest.TestCase):
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

    def test_complete_source_baselines_and_strict_failures(self):
        self.assertEqual(source.verify(self.directory), dict(groups=720, publicProbePixelMatches=720,
                         publicWitnessPixelDifferences=3, sourceReplayFiles=2161, accepted=False))

    def test_source_cannot_accept_linux(self):
        self.edit('investigation.json', lambda data: data.update(accepted=True))
        self.rejected()

    def test_three_witness_differences_cannot_be_approved(self):
        self.edit('investigation.json', lambda data: data.update(publicWitnessPixelMatches=720, publicWitnessPixelDifferences=0))
        self.rejected()

    def test_hosted_window_acceptance_cannot_follow_image_renderer(self):
        self.edit('investigation.json', lambda data: data.update(hostedWindowAcceptance='passed'))
        self.rejected()

    def test_missing_context(self):
        self.edit('captures/captures.json', lambda data: data['captures'].pop())
        self.rejected()

    def test_duplicate_context(self):
        self.edit('captures/captures.json', lambda data: data['captures'].__setitem__(1, data['captures'][0]))
        self.rejected()

    def test_nontransparent_probe_rejected(self):
        self.edit('captures/captures.json', lambda data: data['captures'][0].update(publicProbedIdentical=False))
        self.rejected()

    def test_baseline_must_reach_parent_reference(self):
        def move(data):
            for state in data['captures'][0]['states'][1:]:
                for key in ['label', 'root', 'styled']:
                    state['baselines'][key] += 1
        self.edit('captures/captures.json', move)
        self.rejected()

    def test_empty_text_does_not_lose_its_baseline(self):
        def omit(data):
            row = next(row for row in data['captures'] if row['configuration']['fixture'] == 'text-empty')
            for state in row['states'][1:]:
                del state['baselines']['label']
        self.edit('captures/captures.json', omit)
        self.rejected()

    def test_background_font_is_not_explicit_text_baseline(self):
        def ambient(data):
            row = next(row for row in data['captures'] if row['configuration']['fixture'] == 'content-system-font')
            for state in row['states'][1:]:
                for key in ['label', 'root', 'styled']:
                    state['baselines'][key] = 14
        self.edit('captures/captures.json', ambient)
        self.rejected()

    def test_multiple_geometry_writers_cannot_be_hidden(self):
        def duplicate(data):
            for state in data['captures'][0]['states'][1:]:
                state['partInstances']['root'].append(state['partInstances']['root'][0])
        self.edit('captures/captures.json', duplicate)
        self.rejected()

    def test_precompiled_input_rejected(self):
        self.edit('tooling-provenance.json', lambda data: data.update(compiledInputs=['Sabella.o']))
        self.rejected()

    def test_incomplete_replay_rejected(self):
        self.edit('clean-replay.json', lambda data: data['outputs'].pop())
        self.rejected()

    def test_unsealed_file_rejected(self):
        (self.directory / 'unexpected.json').write_text('{}\n')
        self.rejected()


if __name__ == '__main__':
    unittest.main()
