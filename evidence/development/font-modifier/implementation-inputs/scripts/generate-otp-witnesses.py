#!/usr/bin/env python3
"""Copy native editor observations for the source-free installed OTP consumer."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/otp-20261016'


def projected():
    report = json.loads((SOURCE / 'investigation.json').read_text())
    traces, hashes = [], {}
    for name in ['behavior-final/behavior.json', 'state-bindings/state-bindings.json', 'edges/edges.json']:
        raw = (SOURCE / name).read_bytes()
        hashes[name] = hashlib.sha256(raw).hexdigest()
        assert hashes[name] == report['files'][name], name
        data = json.loads(raw)
        assert data['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
        for trace in data['traces']:
            events = trace.get('events', trace.get('steps'))
            keys = ['code', 'fieldValue', 'requests', 'hasMarkedText', 'editorSelection', 'selection']
            traces.append({
                'sourceFile': name, 'fixture': trace['fixture'],
                'bindingMode': trace.get('bindingMode', 'functional-observed'),
                'initialCode': trace.get('initialCode', events[0]['state']['code']),
                'initialLength': trace.get('initialLength', 6),
                'disabled': trace.get('disabled', trace['fixture'] == 'disabled'),
                'observeOnly': trace.get('observeOnly', False), 'deferredOwner': trace.get('deferredOwner', False),
                'events': [{'action': event['action'], 'state': {k: event['state'][k] for k in keys if k in event['state']}}
                           for event in events],
            })
    assert len(traces) == 19 and sum(len(trace['events']) for trace in traces) == 200
    return json.dumps({'reference': data['reference'], 'sourceFiles': hashes, 'traces': traces}, indent=2, ensure_ascii=False) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / 'tests/consumer/native-otp-witnesses.json'
    expected = projected()
    if args.check:
        assert target.read_text() == expected, 'Native OTP consumer witnesses differ'
    else:
        target.write_text(expected)
    print('OTP consumer witnesses: 19 traces, 200 original model/editor observations')
