#!/usr/bin/env python3
"""Restore frozen Linux sources and/or the installed package into a new directory."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,subprocess
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--source',action='store_true');parser.add_argument('--package',action='store_true')
parser.add_argument('--snapshot',default='file-input-qt-v29');a=parser.parse_args()
if not a.source and not a.package:a.source=True
d=Path(__file__).resolve().parents[1];root=d.parents[2];assert not a.output.exists();a.output.mkdir(parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def target(prefix,name):
 path=Path(name);assert not path.is_absolute()and'..'not in path.parts
 result=prefix/path;result.parent.mkdir(parents=True,exist_ok=True);return result
if a.source:
 source=json.loads((d/'replay/source.json').read_text());files=source['snapshots'][a.snapshot]
 with subprocess.Popen(['git','cat-file','--batch'],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE)as git:
  for name,digest in sorted(files.items()):
   baseline=source['baseline'][name]
   if baseline and baseline['sha256']==digest:
    git.stdin.write((baseline['blob']+'\n').encode());git.stdin.flush();header=git.stdout.readline().split();assert header[1]==b'blob'
    raw=git.stdout.read(int(header[2]));assert git.stdout.read(1)==b'\n'
   else:raw=(d/'replay/blobs'/digest).read_bytes()
   assert sha(raw)==digest,name;target(a.output/'source',name).write_bytes(raw)
  git.stdin.close();assert git.wait()==0
 print('Restored',len(files),'checksummed Linux source files for',a.snapshot)
if a.package:
 package=json.loads((d/'replay/package.json').read_text());limit=package['chunkBytes'];assert limit<=16*1024*1024
 for name,row in package['files'].items():
  path=target(a.output/'package',name);digest=hashlib.sha256();total=0
  with path.open('xb')as stream:
   for part in row['parts']:
    archive=Path(part['archive']);assert not archive.is_absolute()and'..'not in archive.parts
    with gzip.open(d/archive,'rb')as compressed:raw=compressed.read(limit+1)
    assert len(raw)==part['bytes']<=limit and sha(raw)==part['sha256']
    stream.write(raw);digest.update(raw);total+=len(raw)
  assert digest.hexdigest()==row['sha256']and total==row['bytes'],name
  assert row['mode']&~0o777==0;os.chmod(path,row['mode'])
 (a.output/'package/output').mkdir()
 print('Restored',len(package['files']),'installed runtime files without library or consumer project sources')
