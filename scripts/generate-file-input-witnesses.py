#!/usr/bin/env python3
"""Retain every native FileInput observation and an explicit Linux type adapter."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/file-input-20261017'
OUTPUT = ROOT / 'tests/consumer/native-file-input-witnesses.json'


def content_types(values):
    mappings = {'public.plain-text': 'text/plain', 'public.image': 'image/*',
        'public.png': 'image/png', 'com.adobe.pdf': 'application/pdf',
        'public.folder': 'inode/directory', 'public.item': '*/*',
        'org.avelino.fixture': {'identifier': 'org.avelino.fixture', 'filenameExtensions': []}}
    assert all(value in mappings for value in values), 'A new native type requires an explicit Linux adapter'
    return [mappings[value] for value in values]


def projection():
    closed = []
    for row in json.loads((SOURCE / 'output/captures.json').read_text())['rows']:
        public = row['modes'][0]
        closed.append(dict(configuration=row['configuration'], appearance=row['appearance'],
            textScale=row['textScale'], dpr=row['dpr'],
            reference=str((SOURCE / 'output' / public['path']).relative_to(ROOT)),
            frames=row['modes'][1]['state']['frames'], nativeState=public['state'],
            linuxContentTypes=content_types(row['configuration']['types'])))
    sizing = [dict(configuration=row['configuration'], appearance=row['appearance'],
        textScale=row['textScale'], dpr=row['dpr'], proposals=row['modes'][0]['proposals'],
        linuxContentTypes=content_types(row['configuration']['types']))
        for row in json.loads((SOURCE / 'sizing-output/sizing.json').read_text())['rows']]
    assert len(closed) == len(sizing) == 256
    definitions = [dict(fixture='file-input-' + row['configuration']['id'],
        api='BleeckerFileInput', source='fe8a1d462fbd793d883fb92086a16aa2947e32c9',
        width=600, height=300, configuration=row['configuration'], linuxContentTypes=row['linuxContentTypes'])
        for row in closed if (row['appearance'], row['textScale'], row['dpr']) == ('light', 1, 1)]
    assert len(definitions) == 32
    return dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9', accepted=False,
        scope='All native closed frames, state and sizing responses. Explicit MIME/descriptor adapter; exact UTType conformance, native chooser presentation, input and reader acceptance remain pending.',
        fixtures=definitions, closed=closed, sizing=sizing)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    text = json.dumps(projection(), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        assert OUTPUT.read_text() == text, 'FileInput witnesses differ from native observations'
    else:
        OUTPUT.write_text(text)


if __name__ == '__main__':
    main()
