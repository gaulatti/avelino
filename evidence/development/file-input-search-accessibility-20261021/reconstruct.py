#!/usr/bin/env python3
"""Recover captured records or the exact Linux producer source into a fresh path."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

DIRECTORY=Path(__file__).resolve().parent


def record_bytes(name):
    row=json.loads((DIRECTORY/'records.json').read_text())[name]
    stored=Path(row['stored']);assert not stored.is_absolute() and '..' not in stored.parts
    payload=(DIRECTORY/stored).read_bytes()
    raw=gzip.decompress(payload) if stored.suffix=='.gz' else payload
    assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
    return raw


def restore_source(repository,destination):
    source=json.loads(record_bytes('producer/inputs.json'))
    overrides=json.loads((DIRECTORY/'source-overrides.json').read_text())
    names=list(source['sourceFiles'])
    for name in names:assert not Path(name).is_absolute() and '..' not in Path(name).parts
    batch=subprocess.check_output(['git','cat-file','--batch'],cwd=repository,input=('\n'.join(source['parent']+':'+n for n in names)+'\n').encode())
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=False)
    stream=io.BytesIO(batch)
    for name in names:
        header=stream.readline().split()
        if len(header)==3:
            assert header[1]==b'blob';original=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        else:
            assert header[-1]==b'missing';original=None
        raw=record_bytes('source-overrides/'+name) if name in overrides['overrides'] else original
        assert raw is not None and hashlib.sha256(raw).hexdigest()==source['sourceFiles'][name],name
        target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    assert not stream.read()
    return {'sourceFiles':len(names),'baseSourceRevision':source['parent'],'sourceUncommittedAtExecution':True,'accepted':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    choices=parser.add_mutually_exclusive_group(required=True)
    choices.add_argument('--record',help='write original record bytes to stdout')
    choices.add_argument('--source',type=Path,help='restore the selected source into this new directory')
    parser.add_argument('--repository',type=Path,default=DIRECTORY.parents[2],help='Git checkout containing the recorded parent')
    args=parser.parse_args()
    if args.record:sys.stdout.buffer.write(record_bytes(args.record))
    else:print(json.dumps(restore_source(args.repository,args.source),indent=2))
