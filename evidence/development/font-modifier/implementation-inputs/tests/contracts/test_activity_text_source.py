import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('activity_text_source', ROOT / 'scripts/verify-activity-text-source.py')
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


class ActivityTextSourceIntegrity(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='avelino-activity-text-')
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name) / 'evidence'
        shutil.copytree(verifier.DIRECTORY, self.directory)

    def change(self, name, mutate):
        path = self.directory / name
        data = json.loads(path.read_text());mutate(data)
        path.write_text(json.dumps(data, indent=2) + '\n')
        manifest = self.directory / 'investigation.json'
        report = json.loads(manifest.read_text());report['files'][name] = verifier.digest(path)
        manifest.write_text(json.dumps(report))

    def rejected(self):
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)

    def test_original_text_and_qt_diagnostic_are_intact(self):
        self.assertEqual(verifier.verify(self.directory)['originalQtMismatches'], 185)

    def test_duplicate_query_cannot_replace_missing_half_point(self):
        self.change('queries.json', lambda d: d['queries'].__setitem__(0, d['queries'][1]))
        self.rejected()

    def test_cached_product_cannot_claim_fresh_source_replay(self):
        self.change('tooling-provenance.json', lambda d: d.update(compiledInputs=['Sabella.o']))
        self.rejected()

    def test_replay_cannot_ignore_changed_output(self):
        self.change('clean-replay.json', lambda d: d['outputs'][0].update(identical=False))
        self.rejected()

    def test_original_qt_mismatch_cannot_be_reported_as_success(self):
        self.change('qt-probe/comparison.json', lambda d: d.update(mismatchCount=0))
        self.rejected()

    def test_original_qt_source_cannot_follow_current_working_tree(self):
        self.change('qt-probe/comparison.json', lambda d: d.update(buttonLabelSha256='0' * 64))
        self.rejected()

    def test_qt_failure_cannot_use_a_different_native_text_frame(self):
        self.change('qt-probe/comparison.json', lambda d: d['mismatches'][0]['source'].update(width=999))
        self.rejected()

    def test_diagnostic_cannot_approve_parity(self):
        path = self.directory / 'investigation.json'
        data = json.loads(path.read_text());data['accepted'] = True;path.write_text(json.dumps(data))
        self.rejected()


if __name__ == '__main__':
    unittest.main()
