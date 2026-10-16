import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('activity_alignment_source', ROOT / 'scripts/verify-activity-alignment-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class ActivityAlignmentSourceContracts(unittest.TestCase):
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
        if name != 'investigation.json':
            manifest = self.directory / 'investigation.json'
            data = json.loads(manifest.read_text())
            data['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
            if name.startswith(('directions/', 'lines/')):
                replay_path = self.directory / 'clean-replay.json'
                replay = json.loads(replay_path.read_text())
                row = next(r for r in replay['outputs'] if r['file'] == name)
                row['originalSha256'] = row['replaySha256'] = data['files'][name]
                replay_path.write_text(json.dumps(replay, indent=2) + '\n')
                data['files']['clean-replay.json'] = hashlib.sha256(replay_path.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(data, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            source.verify(self.directory)

    def test_complete_public_corpus_and_historical_failures(self):
        self.assertEqual(source.verify(self.directory)['historicalQtMismatches'], 614)

    def test_cannot_claim_acceptance(self):
        self.edit('investigation.json', lambda d: d.update(accepted=True))
        self.rejected()

    def test_missing_direction_context_is_rejected(self):
        self.edit('directions/text-directions.json', lambda d: d['queries'].pop())
        self.rejected()

    def test_duplicate_context_is_rejected(self):
        self.edit('directions/text-directions.json', lambda d: d['queries'].__setitem__(1, d['queries'][0]))
        self.rejected()

    def test_custom_renderer_cannot_be_declared_transparent(self):
        self.edit('investigation.json', lambda d: d.update(publicAlignmentRendererPNGIdentities=768))
        self.rejected()

    def test_proxy_frame_cannot_replace_bare_public_frame(self):
        def swap(data):
            row = next(r for r in data['rows'] if r['key'] == 'title' and r['dpr'] == 1 and r['rtl'] and r['alignment'] == 'leading' and r['proposalWidth'] == 40)
            self.assertNotEqual(row['bareRect'], row['probedRect'])
            row['bareRect'] = row['probedRect']
        self.edit('lines/lines.json', swap)
        self.rejected()

    def test_historical_qt_failure_cannot_be_hidden(self):
        def hide(data):
            row = next(r for r in data['results'] if r['differences'])
            row['differences'] = {}
        self.edit('qt/comparison.json', hide)
        self.rejected()

    def test_historical_implementation_binding_is_required(self):
        self.edit('qt/provenance.json', lambda d: d['sourceFileHashes'].update({'src/Avelino/buttonlabel.cpp': '0' * 64}))
        self.rejected()

    def test_complete_replay_is_required(self):
        self.edit('clean-replay.json', lambda d: d['outputs'].pop())
        self.rejected()

    def test_unsealed_files_are_rejected(self):
        (self.directory / 'unexpected.json').write_text('{}\n')
        self.rejected()


if __name__ == '__main__':
    unittest.main()
