import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


capture = module('stepper_capture', 'scripts/capture-stepper-cases.py')
witnesses = module('stepper_witnesses', 'scripts/generate-stepper-witnesses.py')
SOURCE = json.loads((capture.SOURCE / 'captures/captures.json').read_text())


class StepperAdapterIntegrity(unittest.TestCase):
    def test_consumer_witnesses_match_preserved_source_inputs(self):
        self.assertEqual(witnesses.TARGET.read_text(), witnesses.projected())

    def test_unsafe_integer_survives_fixture_projection_as_a_string(self):
        definitions = capture.definitions(SOURCE)['fixtures']
        row = next(row for row in definitions if row['fixture'] == 'beyond-js-safe')
        self.assertEqual(row['stepperValue'], '9007199254740993')
        self.assertEqual(row['upperBound'], '9223372036854775807')
        self.assertEqual(len(definitions), 43)

    def test_appearance_cannot_change_integer_input_silently(self):
        source = copy.deepcopy(SOURCE)
        source['captures'][0]['value'] = '3'
        with self.assertRaisesRegex(AssertionError, 'Non-appearance inputs'):
            capture.definitions(source)

    def test_missing_fixture_variant_is_refused(self):
        source = copy.deepcopy(SOURCE)
        source['captures'][0] = source['captures'][1]
        with self.assertRaisesRegex(AssertionError, 'capture coverage'):
            capture.definitions(source)

    def test_placeholder_renderer_cannot_enter_hosted_capture_path(self):
        source = copy.deepcopy(SOURCE)
        source['captures'][0]['captureMethod'] = 'ImageRenderer'
        with self.assertRaisesRegex(AssertionError, 'Unsupported native capture method'):
            capture.definitions(source)


if __name__ == '__main__':
    unittest.main()
