from pathlib import Path
import json
import re
import shlex
import shutil
import subprocess
import time

p = Path(__file__).resolve().parent
source = p.with_name('ci-validator-repair-v1') / 'catalog-evidence'
output = p / 'negative-catalog'
shutil.copytree(source, output)
text = (p / 'after/scripts/check-installed-catalog.sh').read_text()
block = re.search(r"<<'PY'\n(.*?)\nPY", text, re.S)[1]
validator = p / 'catalog-validator.py'
validator.write_text(block + '\n')
fixtures = shlex.split(re.search(r'^fixtures=\((.*)\)$', text, re.M)[1])
steps = json.loads((p / 'commands.json').read_text())
image = sorted(output.glob('*.png'))[0]
held = image.with_suffix('.held')
image.rename(held)

def run(name, reason):
    command = ['python3', str(validator), str(output), *fixtures]
    start = time.monotonic()
    result = subprocess.run(command, capture_output=True)
    (p / (name + '.log')).write_bytes(result.stdout + result.stderr)
    assert result.returncode == 1 and reason in result.stderr
    steps.append(dict(name=name, command=command, exitCode=result.returncode,
        expectedExitCode=1, seconds=time.monotonic() - start, attempt='v2'))
    (p / 'commands.json').write_text(json.dumps(steps, indent=2) + '\n')
    print(name, result.returncode)

run('catalog-missing-capture', b"'missing': ['")
held.rename(image)
shutil.copy2(image, output / 'unexpected.png')
shutil.copy2(image.with_name(image.name + '.json'), output / 'unexpected.png.json')
run('catalog-unexpected-capture', b"'unexpected': ['unexpected.png']")
