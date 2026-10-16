import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('native_source_rebuild', ROOT / 'scripts/verify-native-source-rebuild.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class NativeSourceRebuildIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'rebuild'
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

    def test_preserved_source_replay_is_intact(self):
        self.assertEqual(verifier.verify(self.directory)['sourceOnlyArchiveReplayIdenticalFiles'], 3160)

    def test_changed_blob_cannot_claim_the_pinned_full_tree(self):
        self.change('source-identity.json', lambda data: data['files'][0].update(gitBlob='0' * 40))
        with self.assertRaisesRegex(AssertionError, 'pinned Git tree'):
            verifier.verify(self.directory)

    def test_cached_object_cannot_claim_a_source_build(self):
        self.change('build-provenance.json', lambda data: data.update(compiledInputs=['cached-reference/Sabella.o']))
        with self.assertRaisesRegex(AssertionError, 'Compiled Sabella inputs'):
            verifier.verify(self.directory)

    def test_dependency_drift_cannot_claim_the_recorded_build(self):
        self.change('build-provenance.json', lambda data: data['dependencies'][0].update(revision='0' * 40))
        with self.assertRaisesRegex(AssertionError, 'dependency lock'):
            verifier.verify(self.directory)

    def test_duplicate_output_cannot_replace_a_missing_output(self):
        self.change('comparison.json', lambda data: data['results'].__setitem__(0, data['results'][1]))
        with self.assertRaisesRegex(AssertionError, 'output coverage'):
            verifier.verify(self.directory)

    def test_rebuilt_output_cannot_be_rebaselined_in_the_report(self):
        self.change('comparison.json', lambda data: data['results'][0].update(expectedSha256='0' * 64, freshSha256='0' * 64, archiveReplaySha256='0' * 64))
        with self.assertRaisesRegex(AssertionError, 'Rebuilt output differs'):
            verifier.verify(self.directory)


if __name__ == '__main__':
    unittest.main()
