#!/usr/bin/env python3
"""Restore a frozen Linux source snapshot without copying Apple reference sources."""
from pathlib import Path
import argparse,hashlib,json,subprocess
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--snapshot',choices=['file-input-qt-v19','file-input-qt-v20','file-input-qt-v21'],default='file-input-qt-v21')
a=parser.parse_args();d=Path(__file__).resolve().parents[1];root=d.parents[2]
binding=json.loads((d/'source-binding.json').read_text());expected=binding['snapshots'][a.snapshot]
assert not a.output.exists();a.output.mkdir(parents=True)
with subprocess.Popen(['git','cat-file','--batch'],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE)as git:
 for name,row in sorted(binding['files'].items()):
  assert not Path(name).is_absolute()and'..'not in Path(name).parts
  if name in binding['changedBySnapshot'][a.snapshot]:
   folder='overlay'if a.snapshot==binding['finalProducer']else'source-overlays/'+a.snapshot
   data=(d/folder/name).read_bytes()
  else:
   git.stdin.write((row['baseBlob']+'\n').encode());git.stdin.flush();header=git.stdout.readline().split();assert header[1]==b'blob'
   data=git.stdout.read(int(header[2]));assert git.stdout.read(1)==b'\n'
  assert hashlib.sha256(data).hexdigest()==expected[name],name
  target=a.output/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 git.stdin.close();assert git.wait()==0
print(f'Restored {len(expected)} checksummed Linux source files for {a.snapshot}')
