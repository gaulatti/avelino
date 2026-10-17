#!/usr/bin/env python3
"""Project measured native surface guides and pointer sequences into the consumer."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT/'evidence/reference-investigations/surface-baseline-input-20261016'
TARGET = ROOT/'tests/consumer/native-surface-supplement-witnesses.json'


def projected():
    baseline = json.loads((DIRECTORY/'baseline/baselines.json').read_text())
    projection = json.loads((DIRECTORY/'guide-projection.json').read_text())
    pointer = json.loads((DIRECTORY/'input/input.json').read_text())
    guides = {tuple(row['context']): row['parts'] for row in projection}
    baselines = []
    for row in baseline['captures']:
        identity = (row['configuration']['fixture'], row['appearance'], row['textScale'], row['dpr'])
        parts = guides[identity]
        measured = {key: [p['values'][0] for p in entry['frames']] for key, entry in parts.items()
                    if all(p['status'] == 'unique' for p in entry['frames'])}
        baselines.append(dict(configuration=row['configuration'], appearance=row['appearance'],
            textScale=row['textScale'], dpr=row['dpr'], parts=row['states'][1]['partInstances'], guides=measured,
            state={key:row['states'][1][key] for key in ['appearances','disappearances','callerInstances','actions','counter']}))
    profiles = []
    for row in pointer['profiles']:
        points = [s['point'] for s in row['samples'][0]]
        modes = []
        for mode in [0,3]:
            assert [s['point'] for s in row['samples'][mode]] == points
            modes.append(dict(mode=mode, sequences=[[s[k] for k in ['beforeDown','afterDown','afterUp','afterSettle']]
                                                   for s in row['samples'][mode]],
                activations=[s['activated'] for s in row['samples'][mode]]))
        profiles.append(dict(configuration=row['configuration'], appearance=row['appearance'], textScale=row['textScale'],
            dpr=row['dpr'], parts=row['initialStates'][1]['partInstances'], points=points, modes=modes))
    assert len(baselines) == 440 and len(profiles) == 288
    return json.dumps(dict(reference=baseline['reference'], accepted=False, nativeBaselineContexts=baselines,
                           nativeInputProfiles=profiles), indent=2, ensure_ascii=False)+'\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true');args=parser.parse_args()
    expected = projected()
    if args.check:
        assert TARGET.read_text() == expected, 'Surface supplement projection differs from native observations'
    else:
        TARGET.write_text(expected)
    print('Surface supplement: 440 baseline contexts and 288 input profiles; no accepted parity')
