import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


capture = module('tooltip_capture_contract', 'capture-tooltip-cases.py')
comparison = module('tooltip_comparison_contract', 'compare-tooltip-captures.py')


class TooltipAdapterIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((capture.SOURCE / 'closed/captures.json').read_text())

    def test_projection_preserves_all_caller_inputs(self):
        rows = {r['fixture']: r for r in capture.definitions(self.source)['fixtures']}
        self.assertEqual(len(rows), 21)
        for native in self.source['captures']:
            configuration = native['configuration']
            row = rows[configuration['fixture']]
            for key, value in configuration.items():
                self.assertEqual(row[key], value)
            self.assertEqual(row['expectedEmpty'], row['content'] in ['empty', 'zero', 'hidden'])
            self.assertTrue(row['helpAttached'])

    def test_missing_context_rejected(self):
        data = copy.deepcopy(self.source)
        data['captures'].pop()
        with self.assertRaises(AssertionError):
            capture.definitions(data)

    def test_duplicate_context_rejected(self):
        data = copy.deepcopy(self.source)
        data['captures'][0] = data['captures'][1]
        with self.assertRaises(AssertionError):
            capture.definitions(data)

    def test_nontransparent_probe_cannot_supply_inputs(self):
        for field in ['publicProbedIdentical', 'publicWitnessIdentical', 'publicUnwrappedIdentical']:
            data = copy.deepcopy(self.source)
            data['captures'][0][field] = False
            with self.subTest(field=field), self.assertRaises(AssertionError):
                capture.definitions(data)

    def test_conflicting_inputs_across_profiles_rejected(self):
        data = copy.deepcopy(self.source)
        data['captures'][0]['configuration']['hint'] = 'Changed producer'
        with self.assertRaises(AssertionError):
            capture.definitions(data)

    def compare_metadata(self, mutate):
        row = next(r for r in self.source['captures'] if r['configuration']['content'] == 'rectangle')
        configuration = row['configuration']
        metadata = dict(tooltipCallerRects=copy.deepcopy(row['states'][1]['parts']),
                        renderedHint=configuration['hint'], renderedContent=configuration['content'],
                        renderedDisabled=configuration['disabled'], renderedRtl=configuration['rtl'],
                        tooltipVisible=False, counterValue=0, mountValues=[])
        mutate(metadata)
        with tempfile.TemporaryDirectory(prefix='avelino-tooltip-comparison-') as temporary:
            root = Path(temporary)
            candidate = root / 'candidate'
            candidate.mkdir()
            (candidate / (row['paths'][0] + '.json')).write_text(json.dumps(metadata))
            output = root / 'comparison'
            def pixel_pass(_source, _candidate, destination, **_kwargs):
                destination.mkdir()
                (destination / 'comparison.json').write_text(json.dumps({'results': [{'fixture': row['paths'][0], 'status': 'passed'}]}))
            with patch.object(comparison.pixels, 'compare', side_effect=pixel_pass):
                status = comparison.compare(candidate, output)
            return status, json.loads((output / 'comparison.json').read_text())

    def test_closed_body_match_cannot_accept_popup(self):
        status, result = self.compare_metadata(lambda d: None)
        self.assertEqual(status, 0)
        self.assertFalse(result['accepted'])

    def test_passing_pixels_cannot_hide_wrong_hint(self):
        status, result = self.compare_metadata(lambda d: d.update(renderedHint='Wrong hint'))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['stateStatus'], 'failed')

    def test_passing_pixels_cannot_hide_visible_popup(self):
        status, result = self.compare_metadata(lambda d: d.update(tooltipVisible=True))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['stateStatus'], 'failed')

    def test_passing_pixels_cannot_hide_reparented_caller(self):
        status, result = self.compare_metadata(lambda d: d['tooltipCallerRects']['root'].update(x=19))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['callerFramesStatus'], 'failed')

    def test_unexpected_caller_part_rejected(self):
        status, result = self.compare_metadata(lambda d: d['tooltipCallerRects'].update(extra=dict(x=0, y=0, width=1, height=1)))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['callerFramesStatus'], 'failed')


if __name__ == '__main__':
    unittest.main()
