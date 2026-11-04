import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('date_assistive_lifetime', ROOT / 'scripts/verify-date-range-assistive-lifetime.py')
EVIDENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


class DateAssistiveLifetimeEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validation = json.loads((EVIDENCE.DIRECTORY / 'validation.json').read_text())
        cls.records = json.loads((EVIDENCE.DIRECTORY / 'records.json').read_text())

    @classmethod
    def raw(cls, name):
        row = cls.records[name]; path = EVIDENCE.DIRECTORY / row['stored']; value = path.read_bytes()
        return gzip.decompress(value) if path.suffix == '.gz' else value

    @classmethod
    def record(cls, name):
        return json.loads(cls.raw(name))

    def test_retained_crashes_and_current_runtime_recompute(self):
        EVIDENCE.verify()

    def test_historical_runtime_cannot_be_assigned_to_its_parent(self):
        with mock.patch.object(EVIDENCE, 'PUBLISHED', EVIDENCE.PARENT), self.assertRaises(AssertionError):
            EVIDENCE.verify()

    def test_reused_suite_cannot_be_relabelled_as_current_execution(self):
        value = self.record('source8/validation/source7-suite-comparability.json')
        value['qtSuiteRerunOnCurrent'] = True
        with self.assertRaises(AssertionError):
            EVIDENCE.comparability(value)

    def test_library_or_test_changes_cannot_reuse_the_prior_suite(self):
        value = self.record('source8/validation/source7-suite-comparability.json')
        value['sourceDifferences'].append('src/Avelino/daterangeinput.cpp')
        with self.assertRaises(AssertionError):
            EVIDENCE.comparability(value)

    def test_end_edit_cannot_change_the_start_binding(self):
        value = self.record('package/date-runtime.json')
        row = next(row for row in value['assistiveInput'] if row['endpoint'] == 'end' and row['owner'] == 'echo')
        row['actual']['model']['start'] = 1680264000.625
        with self.assertRaises(AssertionError):
            EVIDENCE.assistive(value)

    def test_ignored_requests_cannot_be_presented_as_saved_values(self):
        value = self.record('package/date-runtime.json')
        row = next(row for row in value['assistiveInput'] if row['endpoint'] == 'start' and row['owner'] == 'ignore')
        row['actual']['model']['start'] = 1680264000.625
        with self.assertRaises(AssertionError):
            EVIDENCE.assistive(value)

    def test_delayed_owner_must_retain_its_pending_request(self):
        value = self.record('package/date-runtime.json')
        next(row for row in value['assistiveInput'] if row['owner'] == 'delay')['actual']['model']['pending'] = {}
        with self.assertRaises(AssertionError):
            EVIDENCE.assistive(value)

    def test_reader_requires_actual_named_speech_receipts(self):
        value = self.record('reader6/output/operator-report.json')
        with self.assertRaises(AssertionError):
            EVIDENCE.reader(value, b'')

    def test_reader_keeps_figure_space_field_padding(self):
        value = self.record('reader6/output/operator-report.json')
        next(row for row in value['phases'] if row['phase'] == 'delayed-edit')['observations']['fromText'] = '3/11/2024'
        with self.assertRaises(AssertionError):
            EVIDENCE.reader(value, self.raw('reader6/output/orca-debug.log'))

    def test_runtime_checks_cannot_promote_native_acceptance(self):
        for key in ['accepted', 'nativeRasterAccepted', 'nativeGeometryAccepted', 'nativeReaderAccepted',
                    'physicalInputAccepted', 'independentMachineAccepted', 'expectedImagesChanged', 'nativeImePreeditAccepted']:
            value = copy.deepcopy(self.validation); value[key] = True
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.limits(value)


if __name__ == '__main__':
    unittest.main()
