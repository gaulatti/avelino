#!/usr/bin/env python3
"""Collect every installed-consumer surface guide/input context without acceptance."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import time


def capture(executable,output):
    executable=Path(executable).resolve();output=Path(output).resolve();output.mkdir()
    commands=[]
    for kind,dark,scale,dpr in itertools.product(['baseline','input'],[False,True],[1,1.5],[1,2]):
        prefix=output/f'{kind}-{"dark" if dark else "light"}-text{scale}-dpr{dpr}'
        command=[str(executable),'--surface-'+kind,'--surface-supplement-observe',
                 '--surface-supplement-report',str(prefix),'--text-scale',str(scale)]
        if dark:command.append('--dark')
        start=time.monotonic()
        with Path(str(prefix)+'.log').open('w') as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,
                env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR=str(dpr)))
        commands.append(dict(command=command,exitCode=result.returncode,seconds=time.monotonic()-start,
                             report=prefix.name+'.json',log=prefix.name+'.log'))
        (output/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        if result.returncode:raise RuntimeError(f'Surface capture failed: {prefix.name}; actual exit {result.returncode}')
        report=json.loads(Path(str(prefix)+'.json').read_text())
        assert report['accepted'] is False and report['structuralChecks']=='passed'
        assert report['dpr']==dpr and report['textScale']==scale and report['appearance']==('dark' if dark else 'light')
        assert len(report['rows'])==(55 if kind=='baseline' else 36)
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()}
    assert len([name for name in files if name.endswith('.png')])==1016
    result=dict(accepted=False,complete=True,baselineContexts=440,inputProfiles=288,inputModes=576,
                inputPoints=57792,files=files,commands=commands)
    (output/'captures.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('executable');parser.add_argument('output')
    args=parser.parse_args();result=capture(args.executable,args.output)
    print('Surface supplement: complete native contexts captured; comparison and acceptance remain separate')
