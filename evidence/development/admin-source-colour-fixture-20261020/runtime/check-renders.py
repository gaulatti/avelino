from pathlib import Path
import json
import math
import re
from PIL import Image

P = Path(__file__).resolve().parent
ROOT = Path('/Users/gaulatti/.codex/tmp/avelino-reference-repair-20261020-v1')
OUT = Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016/admin-source-colour-fixture-v1')
text = (ROOT / 'tests/consumer/native-admin-shell-colours.js').read_text()
inputs = json.loads(re.search(r'var environments = (\{.*\});\s*$', text, re.S).group(1))
checks = []; errors = []; totals = {}
for scale in [1, 2]:
    receipt = json.loads((P / f'capture-dpr{scale}.json').read_text())
    assert receipt['exitCode'] == 0 and len(receipt['observations']) == len(receipt['rawCaptures']) == 80
    total = 0
    for row in receipt['observations']:
        theme = 'dark' if row['dark'] else 'light'
        path = OUT / f'dpr{scale}' / (row['name'] + '.png')
        with Image.open(path) as source:
            source.load(); assert source.size == (row['width'] * scale, row['height'] * scale)
            image = source.convert('RGBA')
            for role, actual in row['colours'].items():
                expected = inputs[theme][role]['encodedSRGB']
                assert [round(v * 65535) for v in actual] == [round(v * 65535) for v in expected]
                if role == 'root' or (role == 'sidebar' and not row['state']['displayedNavigation']):
                    continue
                frame = row['state']['frames'][role]
                x0 = math.ceil(max(0, frame['x']) * scale)
                y0 = math.ceil(max(0, frame['y']) * scale)
                x1 = math.floor(min(row['width'], frame['x'] + frame['width']) * scale)
                y1 = math.floor(min(row['height'], frame['y'] + frame['height']) * scale)
                if x1 <= x0 or y1 <= y0:
                    continue
                x = x0 + (x1 - x0) // 2; y = y0 + (y1 - y0) // 2
                expected_pixel = [round(v * 255) for v in actual]
                pixel = list(image.getpixel((x, y)))
                check = dict(scale=scale, name=row['name'], role=role, x=x, y=y,
                             expectedRGBA=expected_pixel, actualRGBA=pixel)
                checks.append(check); total += 1
                if pixel != expected_pixel:
                    errors.append(check)
    totals[str(scale)] = total
result = dict(rawCaptures=160, pixelSamplesPerScale=totals, checks=checks, mismatches=errors,
              qtColour16BitInputsMatched=True, sourceColourInputsIntegrated=True,
              nativeRasterAccepted=False, comparisonPolicyChanged=False, accepted=False)
(P / 'render-check.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks', 'mismatches']}, indent=2))
assert not errors, errors[:4]
