import importlib.util
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('otp_unicode', ROOT / 'scripts/generate-otp-unicode.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class OTPUnicodeProjection(unittest.TestCase):
    def test_transformation_checkpoint_preserves_bytes_and_pending_component(self):
        folder = ROOT / 'evidence/development/otp-transformation'
        record = json.loads((folder / 'candidate.json').read_text())
        self.assertFalse(record['accepted'])
        self.assertIn('component and complete parity pending', record['status'])
        self.assertEqual(record['counts']['nativeTransitions'], 13137306)
        self.assertEqual(record['counts']['nativeResultFNV1a64'], '3d551fb50bf22f59')
        for name, expected in record['sourceInputs'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)
        for name, expected in record['files'].items():
            self.assertEqual(hashlib.sha256((folder / name).read_bytes()).hexdigest(), expected, name)
        rows = json.loads((folder / 'gallery-byte-comparison.json').read_text())
        self.assertFalse(rows['accepted'])
        self.assertEqual(len(rows['files']), 199)
        self.assertEqual(sum(row['file'].endswith('.png') for row in rows['files']), 99)
        self.assertTrue(all(row['identicalToRadioGallery'] for row in rows['files']))

    def test_production_ranges_match_immutable_native_properties(self):
        self.assertEqual((ROOT / 'src/Avelino/otpunicode.h').read_text(), generator.projected())

    def test_input_changes_are_refused(self):
        with patch.object(Path, 'read_bytes', return_value=b'{}'):
            with self.assertRaisesRegex(AssertionError, 'OTP input bytes changed'):
                generator.projected()

    def test_ranges_preserve_scalars_without_gaps(self):
        self.assertEqual(generator.ranges([1, 2, 3, 7, 9, 10]), [[1, 3], [7, 7], [9, 10]])
        for values in [[2, 1], [1, 1], [0xd800], [-1], [0x110000]]:
            with self.assertRaises(AssertionError):
                generator.ranges(values)

    def test_specialization_invariants_cannot_be_relaxed(self):
        original = generator.read
        for key in ['numericGCBClasses', 'numericExtendedPictographicOverlap',
                    'numericIndicConsonantOverlap', 'joiningExtendedPictographicOverlap',
                    'joiningIndicConsonantOverlap']:
            def changed(name):
                data = original(name)
                if name == 'numeric-cluster-properties.json':
                    data[key] = {'Other': 2022} if key == 'numericGCBClasses' else [49]
                return data
            with patch.object(generator, 'read', side_effect=changed):
                with self.assertRaises(AssertionError):
                    generator.projected()
