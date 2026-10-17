#!/usr/bin/env python3
"""Project native observations for the independent Linux consumer."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/command-spotlight-20261017'
OUTPUT = ROOT / 'tests/consumer/native-command-spotlight-witnesses.json'


def active_frames(state):
    present = set(state['appearedKeys'])
    return {key: value for key, value in state['frames'].items()
        if not key.startswith(('row-', 'content-')) or key.split('-', 1)[1] in present}


def projection():
    read = lambda name: json.loads((SOURCE / name).read_text())
    closed, histories, sizing = [], [], []

    def observe(row, configuration, appearance, scale, dpr, prefix):
        public, literal = row['states'][0], row['states'][2]
        fields = {key: public[key] for key in ['query', 'requests', 'pending', 'rowCounts',
            'rowInstances', 'rowAppearances', 'rowDisappearances', 'appearedKeys', 'lifecycle']}
        field = next(value for value in public['controls'] if 'editable' in value)
        return dict(configuration=configuration, appearance=appearance, textScale=scale, dpr=dpr,
            reference=str((SOURCE / prefix / row['paths'][0]).relative_to(ROOT)),
            frames=active_frames(literal), rawFrames=literal['frames'], editorText=field['value'],
            fieldEnabled=field['enabled'], **fields)

    for row in read('output/captures.json')['rows']:
        closed.append(observe(row, row['configuration'], row['appearance'], row['textScale'], row['dpr'], 'output'))
    for directory in ['history-output', 'supplementary-history-output']:
        for row in read(directory + '/histories.json')['histories']:
            steps = []
            for step in row['steps']:
                observed = observe(step, step['states'][0]['configuration'], step['states'][0]['appearance'],
                    step['states'][0]['textScale'], row['dpr'], directory)
                steps.append(dict(observed, step=step['step'], actions=step['actions'][0],
                    matchesInitialPixels=step['matchesInitialPixels']))
            histories.append(dict(configuration=row['configuration'], appearance=row['appearance'],
                textScale=row['textScale'], dpr=row['dpr'], steps=steps))
    for row in read('sizing-output/sizing.json')['rows']:
        sizing.append(dict(configuration=row['configuration'], appearance=row['appearance'],
            textScale=row['textScale'], dpr=row['dpr'], proposals=row['modes'][0]['proposals']))
    assert len(closed) == len(sizing) == 256 and len(histories) == 64
    assert sum(len(row['steps']) for row in histories) == 1536
    return dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9', accepted=False,
        geometryScope='Current appeared rows only; all raw frames and state observations retained separately. No PNG masking or tolerance.',
        closed=closed, histories=histories, sizing=sizing)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    text = json.dumps(projection(), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        assert OUTPUT.read_text() == text, 'CommandSpotlight witnesses differ from native observations'
    else:
        OUTPUT.write_text(text)


if __name__ == '__main__':
    main()
