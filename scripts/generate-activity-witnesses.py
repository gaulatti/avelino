#!/usr/bin/env python3
"""Copy native action/lifecycle observations into the independent Linux consumer."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/activity-item-20261016'


def projected():
    name = 'behavior/behavior.json'
    raw = (SOURCE / name).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    report = json.loads((SOURCE / 'investigation.json').read_text())
    assert report['files'][name] == digest
    data = json.loads(raw)
    assert data['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    keys = ['configuration', 'calls', 'count', 'appears', 'disappears', 'actionValues']
    traces = [{'fixture': trace['fixture'], 'events': [
        {'action': event['action'], 'state': {key: event['state'][key] for key in keys}}
        for event in trace['events']]} for trace in data['traces']]
    assert len(traces) == 13 and sum(len(trace['events']) for trace in traces) == 94
    return json.dumps({'reference': data['reference'], 'sourceFiles': {name: digest}, 'traces': traces}, indent=2, ensure_ascii=False) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / 'tests/consumer/native-activity-witnesses.json'
    expected = projected()
    if args.check:
        assert target.read_text() == expected, 'Native ActivityItem consumer witnesses differ'
    else:
        target.write_text(expected)
    print('ActivityItem consumer witnesses: 13 traces, 94 original action/lifecycle snapshots')
