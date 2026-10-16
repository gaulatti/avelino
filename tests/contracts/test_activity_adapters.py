import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


capture = module('activity_capture', 'scripts/capture-activity-cases.py')
comparison = module('activity_comparison', 'scripts/compare-activity-captures.py')
witnesses = module('activity_witnesses', 'scripts/generate-activity-witnesses.py')


class ActivityAdapterIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((capture.SOURCE / 'captures/captures.json').read_text())

    def test_consumer_preserves_all_native_action_and_lifecycle_observations(self):
        self.assertEqual((ROOT / 'tests/consumer/native-activity-witnesses.json').read_text(), witnesses.projected())
        data = json.loads(witnesses.projected())
        self.assertEqual(len(data['traces']), 13)
        self.assertEqual(sum(len(t['events']) for t in data['traces']), 94)

    def test_fixture_projection_preserves_direct_empty_and_multiple_actions(self):
        rows = {r['fixture']: r for r in capture.definitions(self.source)['fixtures']}
        self.assertEqual(len(rows), 69)
        for name in ['actions-empty-direct', 'actions-multi-direct', 'symbol-empty', 'width-0', 'parent-font32-plain', 'unicode']:
            original = next(r for r in self.source['captures'] if r['fixture'] == name)
            for key in ['title', 'detail', 'timestamp', 'actions', 'symbol', 'proposalWidth', 'parentFont']:
                self.assertEqual(rows[name][key], original[key])
        self.assertEqual(rows['badge-anchor']['variant'], 'subtle')

    def test_missing_context_cannot_enter_capture_projection(self):
        data = copy.deepcopy(self.source)
        data['captures'].pop()
        with self.assertRaises(AssertionError):
            capture.definitions(data)

    def test_duplicate_context_cannot_replace_a_required_context(self):
        data = copy.deepcopy(self.source)
        data['captures'][0] = data['captures'][1]
        with self.assertRaises(AssertionError):
            capture.definitions(data)

    def test_another_native_renderer_cannot_enter_hosted_comparison(self):
        data = copy.deepcopy(self.source)
        data['captures'][0]['captureMethod'] = 'ImageRenderer'
        with self.assertRaises(AssertionError):
            capture.definitions(data)

    def compare_metadata(self, mutate):
        row = next(r for r in self.source['captures'] if r['api'] == 'BleeckerActivityItem')
        with tempfile.TemporaryDirectory(prefix='avelino-activity-comparison-') as temporary:
            root = Path(temporary)
            candidate = root / 'candidate'
            candidate.mkdir()
            metadata = dict(componentOrigin={k: row['componentRect'][k] for k in ['x', 'y']},
                            componentSize={k: row['componentRect'][k] for k in ['width', 'height']},
                            renderedTitle=row['title'], renderedDetail=row['detail'], renderedTimestamp=row['timestamp'],
                            renderedActionMode=row['actions'], renderedDisabled=row['disabled'], renderedRtl=row['rtl'],
                            layoutWitnessRects=copy.deepcopy(row['witness']['parts']))
            mutate(metadata)
            (candidate / (row['path'] + '.json')).write_text(json.dumps(metadata))
            output = root / 'comparison'
            def pixel_pass(_source, _candidate, destination, **_kwargs):
                destination.mkdir()
                (destination / 'comparison.json').write_text(json.dumps({'results': [{'fixture': row['path'], 'status': 'passed'}]}))
            with patch.object(comparison.pixels, 'compare', side_effect=pixel_pass):
                status = comparison.compare(candidate, output)
            return status, json.loads((output / 'comparison.json').read_text())

    def test_passing_pixels_cannot_hide_a_wrong_rendered_field(self):
        status, result = self.compare_metadata(lambda d: d.update(renderedTitle='Wrong field'))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['stateStatus'], 'failed')
        self.assertFalse(result['accepted'])

    def test_passing_pixels_and_root_cannot_hide_a_wrong_child_frame(self):
        status, result = self.compare_metadata(lambda d: d['layoutWitnessRects']['title'].update(height=999))
        self.assertEqual(status, 1)
        self.assertEqual(result['results'][0]['rootBounds']['status'], 'passed')
        self.assertEqual(result['results'][0]['childBoundsStatus'], 'failed')


if __name__ == '__main__':
    unittest.main()
