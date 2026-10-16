import copy
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'evidence/reference-investigations/otp-20261016'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


witnesses = module('otp_witnesses', 'generate-otp-witnesses.py')
capture = module('otp_captures', 'capture-otp-cases.py')
comparison = module('otp_comparison', 'compare-otp-captures.py')


class OTPAdapters(unittest.TestCase):
    def test_all_original_inputs_reach_the_catalog(self):
        native = json.loads((SOURCE / 'captures/captures.json').read_text())
        definitions = capture.definitions(native)['fixtures']
        self.assertEqual(len(definitions), 43)
        for row in native['captures']:
            actual = next(value for value in definitions if value['fixture'] == row['fixture'])
            for key in ['code', 'codeScalars', 'length', 'proposalWidth', 'intrinsic', 'disabled', 'rtl', 'parentFont', 'parentForeground']:
                self.assertEqual(actual[key], row[key])
        initial = next(row for row in definitions if row['fixture'] == 'nonempty-length-zero')
        self.assertEqual((initial['code'], initial['length']), ('A12345', 0))

    def test_duplicate_capture_cannot_replace_another_context(self):
        native = json.loads((SOURCE / 'captures/captures.json').read_text())
        native['captures'][0] = copy.deepcopy(native['captures'][1])
        with self.assertRaisesRegex(AssertionError, 'capture coverage'):
            capture.definitions(native)

    def test_getter_scalar_spelling_cannot_change(self):
        native = json.loads((SOURCE / 'captures/captures.json').read_text())
        native['captures'][0]['code'] = '1'
        with self.assertRaisesRegex(AssertionError, 'scalar spelling'):
            capture.definitions(native)

    def test_source_free_witnesses_keep_model_editor_requests_and_selection(self):
        raw = witnesses.projected()
        self.assertEqual((ROOT / 'tests/consumer/native-otp-witnesses.json').read_text(), raw)
        data = json.loads(raw)
        self.assertEqual(len(data['traces']), 19)
        self.assertEqual(sum(len(trace['events']) for trace in data['traces']), 200)
        for trace in data['traces']:
            original = json.loads((SOURCE / trace['sourceFile']).read_text())
            native = next(row for row in original['traces'] if row['fixture'] == trace['fixture'] and
                          row.get('bindingMode', 'functional-observed') == trace['bindingMode'])
            for actual, expected in zip(trace['events'], native.get('events', native.get('steps'))):
                self.assertEqual(actual['action'], expected['action'])
                for key, value in actual['state'].items():
                    self.assertEqual(value, expected['state'][key])

    def test_geometry_failures_are_retained(self):
        expected = dict(x=1, y=2, width=240, height=40)
        self.assertEqual(comparison.bounds(expected, expected)['status'], 'passed')
        for actual in [None, {}, {**expected, 'width': 239}, {**expected, 'extra': 1}]:
            self.assertEqual(comparison.bounds(expected, actual)['status'], 'failed')

    def test_failed_capture_and_original_attempt_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / 'catalog'
            catalog.write_text('placeholder executable; subprocess is mocked')
            output = root / 'new-attempt'
            with patch.object(capture.subprocess, 'run', return_value=SimpleNamespace(returncode=9)):
                with self.assertRaisesRegex(AssertionError, 'Capture failed'):
                    capture.capture(catalog, output)
            record = json.loads((output / 'failed-capture.json').read_text())
            self.assertEqual(record['returnCode'], 9)
            self.assertFalse(record['pngWritten'])
            self.assertTrue((output / (record['path'] + '.log')).is_file())
            with self.assertRaisesRegex(AssertionError, 'output must be new'):
                capture.capture(catalog, output)
