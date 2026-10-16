"""Audit original full-output snapshots without resizing or masking."""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageChops

root = Path(sys.argv[1])
stem = 'radio-group-wayland-opengl-scaled'
names = [stem + suffix for suffix in ['-initial-session.png', '-after-500ms-session.png', '-after-1000ms-session.png', '-session.png']]
rows, images = [], []
for name in names:
    path = root / name
    image = Image.open(path).convert('RGB')
    images.append(image)
    rows.append({'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'physicalPixels': list(image.size)})
differences = []
for index in range(1, len(images)):
    difference = ImageChops.difference(images[index - 1], images[index])
    differences.append({'before': names[index - 1], 'after': names[index], 'fullOutputChangedPixels': sum(value != (0, 0, 0) for value in difference.get_flattened_data()), 'fullOutputDifferenceBounds': difference.getbbox()})
result = {'scope': 'Original full output; no resize or mask. Delays are nominal sleeps plus capture time. This is a virtual compositor timing diagnostic, not strict mirror acceptance.', 'captures': rows, 'differences': differences, '500msAnd2000msFilesByteIdentical': (root / names[1]).read_bytes() == (root / names[3]).read_bytes(), 'visualInspection': 'All four keyboard rows and their bottom borders are visible in the settled 500ms/2000ms output. Initial cropping is consistent with the entrance transition; a persistent layout defect is not established. Native keyboard, physical sessions and actual readers remain pending.'}
(root / 'settlement-analysis.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
