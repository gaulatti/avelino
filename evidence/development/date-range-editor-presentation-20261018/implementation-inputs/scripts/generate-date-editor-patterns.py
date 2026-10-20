#!/usr/bin/env python3
"""Preserve the pinned native date-style patterns used by owned editors."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/reference-investigations/date-range-font-20261018/metrics.json'
VISIBLE=SOURCE.with_name('visible-pattern-observations.json')
TARGET=ROOT/'src/Avelino/date-editor-patterns.json'
def generate():
    data=json.loads(SOURCE.read_text());patterns={}
    for row in data['rows']:
        config=row['configuration'];calendar={'islamic-umm-al-qura':'islamic-umalqura'}.get(config['calendar'],config['calendar'])
        key=config['locale']+'|'+calendar
        for editor in row['editors']:
            pattern=editor['shortDateFormat'];assert key not in patterns or patterns[key]==pattern
            patterns[key]=pattern
    assert len(patterns)==14
    observations=json.loads(VISIBLE.read_text())
    for row in observations['overrides']:
        key=row['locale']+'|'+row['calendar'];assert patterns[key]==row['shortDateFormat']
        for image in row['images']:
            assert hashlib.sha256((ROOT/image['path']).read_bytes()).hexdigest()==image['sha256']
        patterns[key]=row['visiblePattern']
    return dict(schemaVersion=1,reference=data['reference'],source=str(SOURCE.relative_to(ROOT)),sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),visibleObservations=str(VISIBLE.relative_to(ROOT)),visibleObservationsSha256=hashlib.sha256(VISIBLE.read_bytes()).hexdigest(),patterns=dict(sorted(patterns.items())))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();content=json.dumps(generate(),indent=2,ensure_ascii=False)+'\n'
    if args.check:
        if not TARGET.is_file() or TARGET.read_text()!=content:raise SystemExit('Native date editor patterns are stale')
    else:TARGET.write_text(content)
    print('Native date editor patterns: 14 recorded locale/calendar contexts; additional contexts and raster acceptance remain pending')
if __name__=='__main__':main()
