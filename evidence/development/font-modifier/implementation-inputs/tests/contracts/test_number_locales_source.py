import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('number_locales_source', ROOT / 'scripts/verify-number-locales-source.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class NumberLocaleSourceIntegrity(unittest.TestCase):
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

    def test_native_symbol_cannot_be_changed_by_rehashing_the_manifest(self):
        self.change('native-locale-data.json', lambda data: data['locales']['ar_EG'].update(nan='ليس رقم'))
        with self.assertRaisesRegex(AssertionError, 'Native Arabic NaN'):
            verifier.verify(self.directory)

    def test_duplicate_cannot_replace_a_required_boundary_witness(self):
        self.change('native-compact-boundaries.json', lambda data: data['results'].__setitem__(0, data['results'][1]))
        with self.assertRaisesRegex(AssertionError, 'boundary coverage'):
            verifier.verify(self.directory)

    def test_cached_native_binary_cannot_claim_a_source_only_replay(self):
        self.change('clean-replay.json', lambda data: data.update(compiledInputs=['NativeExpanded']))
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)


if __name__ == '__main__':
    unittest.main()
