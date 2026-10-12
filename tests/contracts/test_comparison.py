import contextlib
import io
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("comparison", ROOT / "scripts/compare-captures.py")
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


class ComparisonBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        base = Path(self.directory.name)
        self.reference, self.candidate, self.output = [base / name for name in ['reference', 'candidate', 'report']]
        self.reference.mkdir(); self.candidate.mkdir()
        self.name = 'case.png'
        Image.new('RGBA', (2, 2), (255, 255, 255, 255)).save(self.reference / self.name)
        (self.candidate / self.name).write_bytes((self.reference / self.name).read_bytes())
        self.fixture = dict(path=self.name, width=2, height=2, dpr=1, textScale=1,
            fixture='button', appearance='light', variant='primary', size='md', state='enabled',
            source='pinned-source', sha256=comparison.digest(self.reference / self.name))
        (self.reference / 'captures.json').write_text(json.dumps({'captures': [self.fixture]}))
        self.metadata = dict(self.fixture)
        self.write_metadata()

    def write_metadata(self):
        (self.candidate / (self.name+'.json')).write_text(json.dumps(self.metadata))

    def check(self, expected_status):
        original = (self.reference / self.name).read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            result = comparison.compare(self.reference, self.candidate, self.output)
        self.assertEqual(result, 0 if expected_status == 'passed' else 1)
        self.assertEqual((self.reference / self.name).read_bytes(), original)
        report = json.loads((self.output / 'comparison.json').read_text())
        self.assertEqual(report['status'], expected_status)
        return report['results'][0]

    def test_identical_pixels_and_equivalent_metadata_pass(self):
        self.check('passed')

    def test_rgb_change_with_unchanged_alpha_fails(self):
        image = Image.open(self.candidate / self.name)
        image.putpixel((0, 0), (254, 255, 255, 255))
        image.save(self.candidate / self.name)
        result = self.check('failed')
        self.assertEqual(result['changedPixels'], 1)
        self.assertIsNone(result['alphaDifferenceBounds'])

    def test_alpha_change_with_unchanged_rgb_fails(self):
        image = Image.open(self.candidate / self.name)
        image.putpixel((0, 0), (255, 255, 255, 254))
        image.save(self.candidate / self.name)
        result = self.check('failed')
        self.assertEqual(result['changedPixels'], 0)
        self.assertIsNotNone(result['alphaDifferenceBounds'])

    def test_incompatible_scale_and_case_metadata_fail_even_with_identical_pixels(self):
        for key, value in [('dpr', 2), ('textScale', 1.25), ('state', 'disabled'), ('fixture', 'field')]:
            with self.subTest(key=key):
                self.metadata = dict(self.fixture, **{key: value})
                self.write_metadata()
                self.assertIn(key, self.check('failed')['error'])

    def test_reference_checksum_change_fails_even_with_matching_candidate(self):
        self.fixture['sha256'] = '0'*64
        (self.reference / 'captures.json').write_text(json.dumps({'captures': [self.fixture]}))
        self.assertIn('checksum', self.check('failed')['error'])

    def test_missing_candidate_and_physical_dimension_change_fail(self):
        (self.candidate / self.name).unlink()
        self.assertIn('Missing', self.check('failed')['error'])
        Image.new('RGBA', (3, 2), 'white').save(self.candidate / self.name)
        self.assertIn('dimensions', self.check('failed')['error'])

    def test_icc_profile_requires_reviewed_conversion(self):
        image = Image.open(self.candidate / self.name)
        image.save(self.candidate / self.name, icc_profile=b'unreviewed-profile')
        self.assertIn('ICC', self.check('failed')['error'])

    def test_component_geometry_difference_fails_even_when_pixels_match(self):
        self.fixture['componentSize'] = dict(width=1, height=1)
        (self.reference / 'captures.json').write_text(json.dumps({'captures': [self.fixture]}))
        self.metadata['componentSize'] = dict(width=2, height=1)
        self.write_metadata()
        result = self.check('failed')
        self.assertEqual(result['changedPixels'], 0)
        self.assertEqual(result['geometryStatus'], 'failed')
        self.assertEqual(result['componentGeometry']['delta']['width'], 1)

    def test_missing_component_geometry_rejects_the_capture(self):
        self.fixture['componentSize'] = dict(width=1, height=1)
        (self.reference / 'captures.json').write_text(json.dumps({'captures': [self.fixture]}))
        self.assertIn('geometry', self.check('failed')['error'])

    def test_proposed_fixture_parameters_must_match(self):
        self.fixture.update(api='BleeckerSwitchStyle', flag=True, value=5, text='Label', expectedEmpty=False)
        (self.reference / 'captures.json').write_text(json.dumps({'captures': [self.fixture]}))
        for key, value in [('api', 'BleeckerButton'), ('flag', False), ('value', 0), ('text', 'Wrong'), ('expectedEmpty', True)]:
            with self.subTest(key=key):
                self.metadata = dict(self.fixture, **{key: value})
                self.write_metadata()
                self.assertIn(key, self.check('failed')['error'])

    def test_identical_proposed_images_do_not_approve_the_baseline(self):
        path = self.reference / 'proposal.json'
        proposal = dict(status='proposed; no baseline approval', accepted=False)
        path.write_text(json.dumps(proposal))
        self.check('passed')
        report = json.loads((self.output / 'comparison.json').read_text())
        self.assertEqual(report['referenceStatus'], proposal['status'])
        self.assertIn('baseline approval', report['acceptance'])
        self.assertFalse(json.loads(path.read_text())['accepted'])
