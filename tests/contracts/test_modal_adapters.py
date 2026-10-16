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


capture = module('modal_capture_contract', 'capture-modal-cases.py')
comparison = module('modal_comparison_contract', 'compare-modal-captures.py')
witnesses = module('modal_witness_contract', 'generate-modal-witnesses.py')


class ModalAdapterIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((capture.SOURCE / 'captures/captures.json').read_text())

    def test_consumer_retains_native_states_and_excludes_editor_proxy_body(self):
        expected = witnesses.projected()
        self.assertEqual((ROOT / 'tests/consumer/native-modal-witnesses.json').read_text(), expected)
        data = json.loads(expected)
        self.assertEqual(sum(len(t['events']) for t in data['traces']), 60)
        self.assertEqual(sum(len(t['events']) for t in data['reopening']), 20)
        self.assertEqual(sum(len(p['samples']) for p in data['hitProfiles']), 568)
        for trace in data['reopening']:
            for event in trace['events']:
                self.assertNotIn('parts', event['state'])

    def test_capture_projection_preserves_zero_body_outer_offers_and_flat_children(self):
        rows = {r['fixture']: r for r in capture.definitions(self.source)['fixtures']}
        self.assertEqual(len(rows), 36)
        self.assertTrue(rows['width-0']['expectedEmpty'])
        self.assertFalse(rows['offer-0']['expectedEmpty'])
        for name in ['offer-0', 'offer-160', 'offer-800', 'content-empty', 'content-zero', 'content-multi', 'unicode', 'bidi']:
            native = next(r['configuration'] for r in self.source['captures'] if r['configuration']['fixture'] == name)
            for key in native:
                self.assertEqual(rows[name][key], native[key])

    def test_missing_context_cannot_enter_capture_projection(self):
        data = copy.deepcopy(self.source)
        data['captures'].pop()
        with self.assertRaises(AssertionError):
            capture.definitions(data)

    def test_duplicate_context_cannot_replace_required_context(self):
        data = copy.deepcopy(self.source)
        data['captures'][0] = data['captures'][1]
        with self.assertRaises(AssertionError):
            capture.definitions(data)

    def test_nontransparent_witness_cannot_supply_capture_inputs(self):
        data = copy.deepcopy(self.source)
        data['captures'][0]['publicWitnessIdentical'] = False
        with self.assertRaises(AssertionError):
            capture.definitions(data)

    def compare_metadata(self, mutate):
        row = next(r for r in self.source['captures'] if r['configuration']['fixture'] == 'offer-0')
        configuration, parts = row['configuration'], row['witness']['parts']
        with tempfile.TemporaryDirectory(prefix='avelino-modal-comparison-') as temporary:
            root = Path(temporary)
            candidate = root / 'candidate'
            candidate.mkdir()
            metadata = dict(componentOrigin={k: parts['root'][k] for k in ['x', 'y']},
                            componentSize={k: parts['root'][k] for k in ['width', 'height']},
                            offeredFrameSize={'width': 0, 'height': parts['root']['height']},
                            renderedTitle=configuration['title'], renderedModalWidth=configuration['modalWidth'],
                            renderedContent=configuration['content'], renderedDisabled=configuration['disabled'],
                            renderedRtl=configuration['rtl'], layoutWitnessRects=copy.deepcopy(parts))
            mutate(metadata)
            (candidate / (row['paths'][0] + '.json')).write_text(json.dumps(metadata))
            output = root / 'comparison'
            def pixel_pass(_source, _candidate, destination, **_kwargs):
                destination.mkdir()
                (destination / 'comparison.json').write_text(json.dumps({'results': [{'fixture': row['paths'][0], 'status': 'passed'}]}))
            with patch.object(comparison.pixels, 'compare', side_effect=pixel_pass):
                status = comparison.compare(candidate, output)
            return status, json.loads((output / 'comparison.json').read_text())

    def test_passing_pixels_cannot_hide_wrong_rendered_title(self):
        status, result = self.compare_metadata(lambda d: d.update(renderedTitle='Wrong title'))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['stateStatus'], 'failed')

    def test_passing_pixels_cannot_hide_wrong_child_bounds(self):
        status, result = self.compare_metadata(lambda d: d['layoutWitnessRects']['close'].update(width=99))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['childBoundsStatus'], 'failed')

    def test_passing_body_pixels_cannot_hide_wrong_outer_allocation(self):
        status, result = self.compare_metadata(lambda d: d['offeredFrameSize'].update(width=480))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['offeredFrame']['status'], 'failed')

    def test_zero_outer_allocation_is_valid_with_full_width_body(self):
        status, result = self.compare_metadata(lambda d: None)
        self.assertEqual(status, 0)
        self.assertFalse(result['accepted'])

    def test_nonnumeric_child_bounds_fail_comparison(self):
        status, result = self.compare_metadata(lambda d: d['layoutWitnessRects']['close'].update(width='44'))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['childBoundsStatus'], 'failed')


if __name__ == '__main__':
    unittest.main()
