import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('activity_layout_source', ROOT / 'scripts/verify-activity-layout-source.py')
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


class ActivityLayoutSourceIntegrity(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='avelino-activity-layout-')
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name) / 'evidence'
        shutil.copytree(verifier.DIRECTORY, self.directory)

    def change(self, name, mutate):
        path = self.directory / name
        data = json.loads(path.read_text());mutate(data)
        path.write_text(json.dumps(data, indent=2) + '\n')
        replay_path = self.directory / 'clean-replay.json'
        if name != replay_path.name:
            replay = json.loads(replay_path.read_text())
            for row in replay['outputs']:
                if row['file'] == name:
                    row['originalSha256'] = row['replaySha256'] = verifier.digest(path)
            replay_path.write_text(json.dumps(replay, indent=2) + '\n')
        manifest = self.directory / 'investigation.json'
        report = json.loads(manifest.read_text())
        report['files'][name] = verifier.digest(path)
        report['files'][replay_path.name] = verifier.digest(replay_path)
        manifest.write_text(json.dumps(report))

    def rejected(self):
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)

    def test_raw_source_and_clean_replay_are_intact(self):
        self.assertEqual(verifier.verify(self.directory)['cleanReplayIdenticalFiles'], 156)

    def test_action_proposal_cannot_be_rounded_before_fitting(self):
        def mutate(data):
            row = next(r for r in data['rows'] if r['dpr'] == 1 and r['textScale'] == 1.5 and r['proposalWidth'] == 240)
            next(r for r in row['queries'] if r['width'] == 148 / 3)['width'] = 50
        self.change('actions/proposals.json', mutate)
        self.rejected()

    def test_fresh_text_cannot_be_conflated_with_growing_text(self):
        self.change('buckets/buckets.json', lambda d: next(t for t in d['traces'] if t['key'] == 'review' and t['dpr'] == 1 and t['sequence'] == 0)['events'][0]['rect'].update(height=96))
        self.rejected()

    def test_previously_measured_exact_width_cannot_be_lost(self):
        self.change('buckets/buckets.json', lambda d: next(t for t in d['traces'] if t['key'] == 'review' and t['dpr'] == 1 and t['sequence'] == 2)['events'][-1]['rect'].update(height=96))
        self.rejected()

    def test_appkit_diagnostic_cannot_claim_complete_swiftui_equivalence(self):
        def mutate(data):
            for row in data['rows']:
                delta = row['native']['height'] - sum(line['height'] for line in row['nsPushOut'])
                row['nsPushOut'][0]['height'] += delta
                row['nsStandard'][0]['height'] += delta
        self.change('text/fixed-queries.json', mutate)
        self.rejected()

    def test_duplicate_replay_output_cannot_replace_a_missing_file(self):
        self.change('clean-replay.json', lambda d: d['outputs'].__setitem__(0, d['outputs'][1]))
        self.rejected()

    def test_compiled_input_cannot_replace_unchanged_sources(self):
        self.change('tooling-provenance.json', lambda d: d.update(compiledInputs=['Sabella.o']))
        self.rejected()

    def test_diagnostic_cannot_approve_mirror_parity(self):
        path = self.directory / 'investigation.json'
        data = json.loads(path.read_text());data['accepted'] = True;path.write_text(json.dumps(data))
        self.rejected()


if __name__ == '__main__':
    unittest.main()
