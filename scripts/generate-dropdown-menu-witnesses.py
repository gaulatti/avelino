#!/usr/bin/env python3
"""Project the complete native dropdown observations for the Linux consumer."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/dropdown-menu-20261017'
OUTPUT = ROOT / 'tests/consumer/native-dropdown-menu-witnesses.json'


def projection():
    closed = []
    for row in json.loads((SOURCE / 'output/captures.json').read_text())['results']:
        public = row['modes'][0]
        button = next(view for view in public['views'] if view['type'] == 'SwiftUIPopupButton')
        closed.append(dict(configuration=row['configuration'], appearance=row['appearance'],
            textScale=row['textScale'], dpr=row['dpr'],
            reference=str((SOURCE / 'output' / public['path']).relative_to(ROOT)),
            frames=row['modes'][1]['frames'], nativeViews=public['views'], title=button['title'],
            enabled=button['enabled'], font=button['font'], calls=public['calls']))
    sizing = [dict(configuration=row['configuration'], appearance=row['appearance'],
        textScale=row['textScale'], dpr=row['dpr'], proposals=row['modes'][0]['proposals'])
        for row in json.loads((SOURCE / 'sizing-output/sizing.json').read_text())['rows']]
    dispatch = [json.loads((SOURCE / f'behavior-output/mode{branch}.json').read_text())
        for branch in range(3)]
    assert len(closed) == len(sizing) == 256
    return dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9', accepted=False,
        scope='All native frames and views remain present, including zero-size metadata labels. No raster masking, tolerance or parity acceptance.',
        closed=closed, sizing=sizing, dispatch=dispatch)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    text = json.dumps(projection(), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        assert OUTPUT.read_text() == text, 'Dropdown witnesses differ from native observations'
    else:
        OUTPUT.write_text(text)


if __name__ == '__main__':
    main()
