from pathlib import Path
import ctypes
import hashlib
import json
import os
import subprocess
import time

P=Path(__file__).resolve().parent
SOURCE=Path('/Users/gaulatti/.codex/worktrees/avelino-footer-source-20261019-v1')
MIRROR=P/'source'
clone=ctypes.CDLL(None,use_errno=True).clonefile
clone.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name,value):
    (P/name).write_text(json.dumps(value,indent=2)+'\n')


try:
    frozen=json.loads((SOURCE/'artifacts/footer-compiled-v1/inputs.json').read_text())
    assert all(sha(SOURCE/name)==digest for name,digest in frozen['sourceFiles'].items())
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=SOURCE).decode().split('\0')
    names=sorted(set(name for name in names if name))
    MIRROR.mkdir()
    size=0
    for index,name in enumerate(names,1):
        relative=Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        source,target=SOURCE/relative,MIRROR/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        if source.is_symlink():target.symlink_to(os.readlink(source))
        else:
            if clone(os.fsencode(source),os.fsencode(target),0):
                code=ctypes.get_errno()
                raise OSError(code,os.strerror(code),str(source))
            size+=source.stat().st_size
        if index%20000==0:
            write('prepare-progress.json',dict(files=index,total=len(names),logicalBytes=size))
            print('Shared source clone',index,'/',len(names),flush=True)
    (MIRROR/'build').mkdir()
    assert all(sha(MIRROR/name)==digest for name,digest in frozen['sourceFiles'].items())
    assert all(sha(SOURCE/name)==digest for name,digest in frozen['sourceFiles'].items())
    write('prepare-result.json',dict(exitCode=0,method='APFS clonefile',source=str(SOURCE),mirror=str(MIRROR),
        gitWorktreeUnchanged=True,files=len(names),logicalBytes=size,compiledInputsVerified=len(frozen['sourceFiles']),
        sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip(),
        vmRestarted=False,accepted=False))
except BaseException as error:
    write('prepare-result.json',dict(exitCode=1,error=repr(error),accepted=False))
    raise
