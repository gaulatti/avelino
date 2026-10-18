from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

output = Path('/ci-proof/permissions')
output.mkdir()
root = Path(tempfile.mkdtemp(prefix='avelino-ci-permissions-'))
root.chmod(0o755)
trees = ['artifacts/linux', 'artifacts/package', 'build/linux/Testing/Temporary']
reports = []
for tree in trees:
    private = root / tree / 'private'
    private.mkdir(parents=True)
    private.chmod(0o700)
    report = private / 'report.json'
    report.write_bytes(b'synthetic evidence\n')
    report.chmod(0o600)
    reports.append(report)

def read(report):
    return subprocess.run(['runuser', '-u', 'nobody', '--', 'python3', '-c',
        'from pathlib import Path; import sys; assert Path(sys.argv[1]).read_bytes()==b"synthetic evidence\\n"',
        str(report)], capture_output=True)

before = [read(report) for report in reports]
assert all(row.returncode != 0 and b'PermissionError' in row.stderr for row in before)
before_hashes = [hashlib.sha256(report.read_bytes()).hexdigest() for report in reports]
workflow = (Path('/ci-proof/after/.github/workflows/linux.yml')).read_text()
loop = '\n'.join(line[10:] for line in workflow.splitlines()
    if line.startswith('          for artifact_path ') or line.startswith('            if [[ -d "$artifact_path" ]]')
    or line == '          done')
assert loop.count('sudo chmod -R a+rX -- "$artifact_path"') == 1
# This container is already root and has no sudo binary; run its exact chmod loop
# on the container's Linux filesystem rather than the macOS shared mount.
subprocess.run(['bash', '-eu', '-c', loop.replace('sudo chmod ', 'chmod ')], cwd=root, check=True)
after = [read(report) for report in reports]
assert all(row.returncode == 0 for row in after)
assert before_hashes == [hashlib.sha256(report.read_bytes()).hexdigest() for report in reports]
result = dict(beforeExit=before[0].returncode, afterExit=after[0].returncode,
    bytesUnchanged=True, filesystem='container Linux filesystem',
    execution='root container; sudo prefix omitted; exact workflow chmod loop',
    paths=[dict(tree=tree, beforeExit=old.returncode, beforeError=old.stderr.decode(),
        afterExit=new.returncode, sha256=checksum)
        for tree, old, new, checksum in zip(trees, before, after, before_hashes)])
(output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
