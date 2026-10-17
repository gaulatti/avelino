"""Dense evidence must preserve the samples that reject the prototype."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('surface_stroke_dense', ROOT / 'scripts/verify-surface-stroke-dense.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class DenseSurfaceStrokeIntegrity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name) / 'candidate'
        shutil.copytree(source.DIRECTORY, self.directory)
        self.report = json.loads((self.directory / 'investigation.json').read_text())

    def tearDown(self):
        self.temporary.cleanup()

    def save(self):
        (self.directory / 'investigation.json').write_text(json.dumps(self.report))

    def update(self, name, value):
        path = self.directory / name
        path.write_text(json.dumps(value))
        self.report['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.save()

    def refused(self):
        with self.assertRaises((AssertionError, ValueError)):
            source.verify(self.directory)

    def test_complete_dense_probe_remains_rejected_and_unapplied(self):
        self.assertEqual(source.verify(self.directory), self.report['summary'])

    def test_sparse_success_cannot_be_promoted_to_acceptance(self):
        self.report['accepted'] = True
        self.save()
        self.refused()

    def test_rejected_prototype_cannot_be_claimed_as_applied(self):
        self.report['implementationApplied'] = True
        self.save()
        self.refused()

    def test_dense_failures_cannot_be_hidden_in_totals(self):
        self.report['summary']['denseDifferences'] = [0] * 5
        self.save()
        self.refused()

    def test_missing_dense_bits_fail_with_refreshed_manifest(self):
        name = 'linux-results.json'
        data = json.loads((self.directory / name).read_text())
        row = data['rows'][0]['methods'][0]
        row['mask'] = base64.b64encode(base64.b64decode(row['mask'])[:-1]).decode()
        self.update(name, data)
        self.refused()

    def test_modified_dense_result_fails_with_refreshed_manifest(self):
        name = 'linux-results.json'
        data = json.loads((self.directory / name).read_text())
        row = data['rows'][0]['methods'][0]
        mask = bytearray(base64.b64decode(row['mask']))
        mask[3] ^= 1
        row['mask'] = base64.b64encode(mask).decode()
        self.update(name, data)
        self.refused()

    def test_missing_geometry_cannot_pass_complete_count(self):
        name = 'native-paths.json'
        data = json.loads((self.directory / name).read_text())
        data['rows'].pop()
        self.update(name, data)
        self.refused()

    def test_critical_adjacent_float_query_cannot_be_skipped(self):
        name = 'native-paths.json'
        data = json.loads((self.directory / name).read_text())
        data['rows'][0]['queries'].pop()
        self.update(name, data)
        self.refused()

    def test_clean_sdk_replay_must_match_actual_bytes(self):
        name = 'sdk-replay-comparison.json'
        data = json.loads((self.directory / name).read_text())
        data['replay'] = '0' * 64
        self.update(name, data)
        self.refused()


if __name__ == '__main__':
    unittest.main()
