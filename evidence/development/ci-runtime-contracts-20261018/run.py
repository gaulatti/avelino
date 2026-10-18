from pathlib import Path
import json
import shutil
import subprocess
import time

p = Path(__file__).resolve().parent
r = p.parents[2]
previous = p.with_name('ci-validator-repair-v1')
initial = json.loads((previous / 'commands.json').read_text())
assert len(initial) == 19
assert all(step['exitCode'] == step['expectedExitCode'] for step in initial[:-1])
assert initial[-1]['name'] == 'artifact-permissions' and initial[-1]['exitCode'] == 1
steps = [dict(step, attempt='v1') for step in initial[:-1]]
for name in ['scripts/check-installed-catalog.sh', 'scripts/check-display-sessions.sh', '.github/workflows/linux.yml']:
    for state in ['before', 'after']:
        target = p / state / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(previous / state / name, target)
    assert (p / 'after' / name).read_bytes() == (r / name).read_bytes()
    assert (p / 'before' / name).read_bytes() == subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=r)

def run(name, command):
    start = time.monotonic()
    with (p / (name + '.log')).open('wb') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    steps.append(dict(name=name, command=command, exitCode=result.returncode,
        expectedExitCode=0, seconds=time.monotonic() - start, attempt='v2'))
    (p / 'commands.json').write_text(json.dumps(steps, indent=2) + '\n')
    print(name, result.returncode, flush=True)
    assert result.returncode == 0

for name in ['check-installed-catalog.sh', 'check-display-sessions.sh']:
    run('syntax-' + name, ['bash', '-n', str(r / 'scripts' / name)])
run('artifact-permissions-linux', ['docker', '--context', 'colima-avelino-verify', 'run', '--rm',
    '-v', str(p) + ':/ci-proof', 'avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3',
    'python3', '/ci-proof/permission-probe.py'])
catalog = json.loads((previous / 'catalog-evidence/catalog-results.json').read_text())
assert len(catalog['captures']) == 159 and catalog['status'] == 'passed'
(p / 'result.json').write_text(json.dumps(dict(accepted=False, exitCode=0,
    baselineDisplayFailures=8, fixedDisplayProfiles=8, catalogCaptures=159,
    unprivilegedArtifactRead='passed', applicationSourcesChanged=False,
    fullRemoteCi='pending', earlierProbe='v1 macOS-shared-mount precondition failed; retained separately'), indent=2) + '\n')
