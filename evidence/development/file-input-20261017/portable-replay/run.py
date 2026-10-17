#!/usr/bin/env python3
"""Run the restored Linux package with no source tree mounted in the container."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--restored',required=True,type=Path)
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args()
restored=args.restored.resolve();output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
root=Path(__file__).resolve().parents[4]
evidence=Path(__file__).resolve().parents[1]
assert json.loads((restored/'reconstructed.json').read_text())['sourceAndPackageBytesVerified']
package=restored/'package';captures=package/'replay-output';captures.mkdir()
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(package)+':/consumer-check','-w','/consumer-check',
      '--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-file-input-portable',
      'avelino-toolchain:clipping-qt6.8.3']
commands=[]
for name,command in [
    ('source-absence',['python3','-c',"from pathlib import Path; assert not Path('/work/src/Avelino').exists(); assert not Path('/consumer-check/consumer').exists(); assert not Path('/consumer-check/src').exists(); assert not Path('/replay/source').exists(); print('Only restored installed prefix and compiled independent consumer mounted')"]),
    ('file-input',['./consumer-build/InstalledConsumer','--file-input','--file-input-observe','--file-input-report','/consumer-check/replay-output/light-text1-dpr1'])]:
    start=time.monotonic()
    with(output/(name+'.log')).open('wb')as log:process=subprocess.run(base+command,stdout=log,stderr=subprocess.STDOUT)
    commands.append(dict(name=name,command=base+command,exitCode=process.returncode,seconds=time.monotonic()-start))
    (output/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    if process.returncode:raise SystemExit(process.returncode)
record=json.loads((captures/'light-text1-dpr1.json').read_text());assert record['structuralChecks']=='passed' and len(record['closed'])==32
rows=[]
for row in record['closed']:
    name='light-text1-dpr1-'+row['configuration']['id']+'.png'
    actual=(captures/name).read_bytes();expected=(evidence/'captures'/name).read_bytes();assert actual==expected,name
    rows.append(dict(path=name,sha256=hashlib.sha256(actual).hexdigest()))
(output/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,restoredPackageRuntime=True,libraryAndConsumerSourceAbsent=True,
    unchangedClosedImages=32,pairs=rows,nativePanelAcceptance='pending',physicalReaderAcceptance='pending'),indent=2)+'\n')
print('Restored installed package: FileInput passed; 32 closed images byte-identical; native acceptance pending')
