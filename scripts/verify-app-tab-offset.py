#!/usr/bin/env python3
"""Measure badge paint direction from immutable native pixels and layout boxes."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/app-tabs-20261017'


def observe():
    data = json.loads((DIRECTORY / 'output/captures.json').read_text())
    records = []
    for appearance, scale, dpr in itertools.product(['light', 'dark'], [1, 1.5], [1, 2]):
        rows = [next(r for r in data['rows'] if r['configuration']['id'] == name
            and (r['appearance'], r['textScale'], r['dpr']) == (appearance, scale, dpr))
            for name in ['width-300', 'rtl']]
        masks, sources = [], []
        for row in rows:
            path = DIRECTORY / 'output' / row['paths'][0]
            with Image.open(path) as raw:
                rgb = raw.convert('RGB')
                channels = [rgb.getchannel(c).point([255 if i == value else 0 for i in range(256)])
                    for c, value in [('R', 255), ('G', 150), ('B', 119)]]
                mask = ImageChops.multiply(ImageChops.multiply(channels[0], channels[1]), channels[2])
                assert mask.getbbox(), 'Native sunset badge pixels absent'
                masks.append(mask)
                sources.append(dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    layout=row['states'][2]['frames']['badge-1'], sunsetPixelBounds=list(mask.getbbox())))
        delta = int((sources[1]['layout']['x'] - sources[0]['layout']['x'] - 20) * dpr)
        left, right = [mask.getbbox() for mask in masks]
        assert right == (left[0] + delta, left[1], left[2] + delta, left[3])
        records.append(dict(appearance=appearance, textScale=scale, dpr=dpr, source=sources,
            translatedSunsetBoundsPixels=delta, exactBoundsTranslation=True,
            exactSunsetMaskTranslation=ImageChops.offset(masks[0], delta, 0).tobytes() == masks[1].tobytes(),
            logicalOffsetLtr=10, logicalOffsetRtl=-10))
    return dict(reference=data['reference'], accepted=False,
        scope='Opaque sunset-color bounds from preserved native PNGs. Layout probes precede the paint transform. Full mask/raster equivalence is separate; no image modification or tolerance.', rows=records)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    value = observe()
    if args.check:
        assert json.loads(args.report.read_text()) == value, 'Native badge offset observations changed'
    else:
        assert not args.report.exists(), 'Preserve earlier diagnostic attempts'
        args.report.write_text(json.dumps(value, indent=2) + '\n')
    print('Eight native badge bounds confirm logical RTL offset; full native raster remains unaccepted')


if __name__ == '__main__':
    main()
