"""Whole-image comparisons include RGB and alpha without resizing or tolerance."""
import importlib.util
from pathlib import Path
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('file_input_pixels', ROOT / 'scripts/compare-file-input-candidate.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class FileInputPixels(unittest.TestCase):
    def test_changes_in_rgb_and_alpha_are_both_counted(self):
        expected = Image.new('RGBA', (3, 1), (10, 20, 30, 255))
        actual = expected.copy()
        actual.putpixel((0, 0), (11, 20, 30, 255))
        actual.putpixel((1, 0), (10, 20, 30, 254))
        self.assertEqual(source.different_pixels(expected, actual), 2)

    def test_exact_pixels_require_every_channel(self):
        image = Image.new('RGBA', (2, 2), (10, 20, 30, 0))
        self.assertEqual(source.different_pixels(image, image.copy()), 0)
        changed = image.copy()
        changed.putpixel((1, 1), (9, 20, 30, 0))
        self.assertEqual(source.different_pixels(image, changed), 1)

    def test_dimension_difference_is_rejected(self):
        with self.assertRaises(AssertionError):
            source.different_pixels(Image.new('RGBA', (2, 1)), Image.new('RGBA', (1, 2)))


if __name__ == '__main__':
    unittest.main()
