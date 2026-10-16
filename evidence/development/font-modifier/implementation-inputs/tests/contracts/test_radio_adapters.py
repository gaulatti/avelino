import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'evidence/reference-investigations/radio-20261016'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


witnesses = module('radio_witnesses', 'generate-radio-witnesses.py')
capture = module('radio_captures', 'capture-radio-cases.py')


class RadioAdapters(unittest.TestCase):
    def test_production_identity_and_consumer_witnesses_match_native_inputs(self):
        for path, expected in witnesses.projected().items():
            self.assertEqual(path.read_text(), expected)
        consumer = json.loads((ROOT / 'tests/consumer/native-radio-witnesses.json').read_text())
        self.assertEqual((len(consumer['traces']), len(consumer['pointerPhases']), len(consumer['stringPairs'])), (24, 11, 13762))
        for name, digest in consumer['sourceFiles'].items():
            self.assertEqual(hashlib.sha256((SOURCE / name).read_bytes()).hexdigest(), digest)

    def test_all_native_cases_reach_the_catalog_without_coercing_original_values(self):
        native = json.loads((SOURCE / 'captures/captures.json').read_text())
        projected = capture.definitions(native)
        self.assertEqual(len(projected['fixtures']), 55)
        for row in native['captures']:
            definition = next(d for d in projected['fixtures'] if d['fixture'] == row['fixture'])
            for key in ['selection', 'orientation', 'proposalWidth', 'parentFont', 'parentFontKind', 'parentFontWeight', 'parentForeground', 'disabled', 'rtl', 'intrinsic']:
                self.assertEqual(definition[key], row[key])
            self.assertEqual(definition['expectedEmpty'], row['api']=='BleeckerRadioGroup' and not row['options'])
            self.assertEqual(definition['options'], [{k: option[k] for k in ['value', 'label', 'disabled']} for option in row['options']])
        canonical = next(d for d in projected['fixtures'] if d['fixture'] == 'canonical-value')
        self.assertEqual(list(map(ord, canonical['selection'])), [101, 769])
        self.assertEqual(list(map(ord, canonical['options'][0]['value'])), [233])

    def test_duplicate_capture_cannot_replace_a_missing_case(self):
        native = json.loads((SOURCE / 'captures/captures.json').read_text())
        native['captures'][0] = copy.deepcopy(native['captures'][1])
        with self.assertRaisesRegex(AssertionError, 'capture coverage'):
            capture.definitions(native)

    def test_unicode_profile_retains_new_combining_classes_and_algorithmic_hangul(self):
        source = json.loads((SOURCE / 'native-normalization-data.json').read_text())
        profile = json.loads((ROOT / 'src/Avelino/unicode-normalization-17.json').read_text())
        self.assertEqual(profile['combiningClasses'], source['combiningClasses'])
        self.assertEqual(profile['canonical'], {k: v for k, v in source['decompositions'].items() if not 0xac00 <= int(k, 16) < 0xac00 + 11172})
        self.assertEqual(len(profile['canonical']), 2081)
        self.assertEqual(profile['unicodeVersion'], '17.0.0')

    def test_unicode_resource_and_license_match_their_provenance(self):
        provenance = json.loads((ROOT / 'assets/unicode/provenance.json').read_text())
        for key in ['license', 'resource']:
            record = provenance[key]
            self.assertEqual(hashlib.sha256((ROOT / record['path']).read_bytes()).hexdigest(), record['sha256'])
        self.assertEqual(provenance['officialData']['sha256'], '2e1efc1dcb59c575eedf5ccae60f95229f706ee6d031835247d843c11d96470c')


if __name__ == '__main__':
    unittest.main()
