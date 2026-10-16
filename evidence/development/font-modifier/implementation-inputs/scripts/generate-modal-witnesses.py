#!/usr/bin/env python3
"""Project trusted native Modal state/input witnesses into the independent consumer."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'evidence/reference-investigations/modal-20261016'
INPUT = ROOT / 'evidence/reference-investigations/modal-input-20261016'


def read(directory, name, hashes):
    raw = (directory / name).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert json.loads((directory / 'investigation.json').read_text())['files'][name] == digest
    hashes[str(directory.relative_to(ROOT) / name)] = digest
    return json.loads(raw)


def projected():
    hashes = {}
    original = read(ORIGINAL, 'behavior/behavior.json', hashes)
    inputs = read(INPUT, 'outputs/input.json', hashes)
    hits = read(INPUT, 'outputs/hit-profiles.json', hashes)
    assert original['reference'] == inputs['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    keys = ['configuration', 'calls', 'appears', 'disappears', 'mounted', 'mountValues', 'text',
            'windowVisible', 'parentVisible', 'presented', 'sheetCount', 'sheetDismissCount']
    traces = [{'id': trace['id'], 'initialConfiguration': trace['initialConfiguration'],
               'presentation': trace['presentation'], 'events': [
        {'action': event['action'], 'state': {key: event['state'][key] for key in keys if key in event['state']}}
        for event in trace['events']]} for trace in original['traces']]
    reopening = []
    for trace in inputs['traces']:
        events = []
        for event in trace['events']:
            state = event.get('state', event)
            projected = {key: state[key] for key in keys if key in state}
            if 'visible' in event:
                projected['windowVisible'] = event['visible']
            if 'text' in event:
                projected['text'] = event['text']
            events.append({'action': event['action'], 'state': projected})
        reopening.append({'id': trace['id'], 'events': events})
    # Clipping groups have verified transparent witnesses. Sheet TextField body
    # proxy frames are deliberately excluded; only original input/lifecycle data
    # and the independently verified Close header are used by the consumer.
    groups = [{'configuration': group['configuration'], 'parts': group['parts']} for group in inputs['groups']]
    queries = [{key: row[key] for key in ['fixture', 'point', 'calls', 'windowVisible', 'targetKey']}
               for row in inputs['queries']]
    profiles = [{key: profile[key] for key in ['dpr', 'textScale', 'closeFrame', 'samples']}
                for profile in hits['profiles']]
    assert len(traces) == 14 and sum(len(t['events']) for t in traces) == 60
    assert len(reopening) == 3 and sum(len(t['events']) for t in reopening) == 20
    assert len(groups) == 12 and len(queries) == 170
    assert len(profiles) == 4 and sum(len(p['samples']) for p in profiles) == 568
    return json.dumps({'reference': original['reference'], 'sourceFiles': hashes,
        'scope': 'Native inactive source data; Qt destruction is recorded separately from native onDisappear; no sheet editor body proxy frames',
        'traces': traces, 'reopening': reopening, 'groups': groups, 'queries': queries,
        'hitProfiles': profiles}, indent=2, ensure_ascii=False) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / 'tests/consumer/native-modal-witnesses.json'
    expected = projected()
    if args.check:
        assert target.read_text() == expected, 'Native Modal consumer witnesses differ'
    else:
        target.write_text(expected)
    print('Modal consumer witnesses: 60 original states, 20 reopening states, 170 clipping and 568 glyph queries')
