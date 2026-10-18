#!/usr/bin/env python3
"""Project calibrated Chinese field strings into typed consumer observations."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/reference-investigations/date-range-chinese-20261018/samples/output/samples.json'
DIAGNOSTICS=SOURCE.parents[2]/'diagnostics/output/private-subfields.json'
TARGET=ROOT/'tests/consumer/native-date-chinese-witnesses.json'

def generate():
    source=json.loads(SOURCE.read_text());diagnostics=json.loads(DIAGNOSTICS.read_text())
    rows={r['configuration']['id']:r for r in diagnostics['rows']};cases=[]
    assert len(source['rows'])==len(rows)==36
    for row in source['rows']:
        cfg=row['configuration'];private=rows[cfg['id']];texts=[];roles=[]
        for index,editor in enumerate(row['editors']):
            fields=[];kinds=[];natural=[]
            for field in private['endpoints'][index]['privateSubfields']:
                values={v['name']:v.get('value') for v in field['ivars']}
                pattern=values['_dateFormat'];label=values['_stringValue'];natural.append(label)
                if pattern is not None:
                    kind='month' if pattern.startswith('M') else 'day' if pattern.startswith('d') else None
                    assert kind is not None;kinds.append(kind)
                    if label and all(char.isdecimal() for char in label):label='\u2007'*max(0,2-len(label))+label
                fields.append(label)
            assert ''.join(natural)==editor['candidateText'] and kinds==['month','day']
            texts.append(''.join(fields));roles.append(kinds)
        cases.append(dict(configuration=cfg,model=row['model'],displayed=[e['date'] for e in row['editors']],editorText=texts,editableRoles=roles,calendarParts=[e['components'] for e in row['editors']],intrinsic=[e['sourceIntrinsic'] for e in row['editors']],referenceCapture=cfg['id']+'.png'))
    return dict(accepted=False,reference=source['reference'],scope='Typed data and logical padded input-string projection from calibrated isolated-cell diagnostics, cross-checked with public formatter samples; no pixel, selection, reader or physical acceptance',source=str(SOURCE.relative_to(ROOT)),sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),diagnostics=str(DIAGNOSTICS.relative_to(ROOT)),diagnosticsSha256=hashlib.sha256(DIAGNOSTICS.read_bytes()).hexdigest(),cases=cases)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    content=json.dumps(generate(),indent=2,ensure_ascii=False)+'\n'
    if args.check:
        if not TARGET.is_file() or TARGET.read_text()!=content:raise SystemExit('Chinese date observations are stale')
    else:TARGET.write_text(content)
    print('Chinese date observations: 36 source configurations, 72 endpoints; full acceptance pending')

if __name__=='__main__':main()
