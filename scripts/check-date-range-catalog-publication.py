#!/usr/bin/env python3
"""Exercise repeated publication using the actual Linux-check shell block."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def files(directory):
    return {str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in directory.rglob('*') if path.is_file()}


def main():
    script = (ROOT / 'scripts/check-linux.sh').read_text()
    copy = 'cp -R "$stage/date-range-catalog-evidence" artifacts/linux/date-range-catalog-installed'
    assert script.count(copy) == 1
    start = script.index('# Keep each earlier date catalog intact')
    block = script[start:script.index(copy) + len(copy)]
    source = ROOT / 'evidence/development/date-range-owned-editors-20261018/catalog/output'
    assert len(list(source.glob('*.png'))) == 4
    with tempfile.TemporaryDirectory(prefix='avelino-date-catalog-') as temporary:
        work = Path(temporary)
        stage = work / 'temporary-stage'
        incoming = stage / 'date-range-catalog-evidence'
        shutil.copytree(source, incoming)
        current = work / 'artifacts/linux/date-range-catalog-installed'
        current.parent.mkdir(parents=True)
        shutil.copytree(source, current)
        (current / 'prior-only.txt').write_text('previous publication\n')
        generations = [files(current)]
        for iteration in range(1, 3):
            (incoming / 'generation.txt').write_text(str(iteration) + '\n')
            expected = files(incoming)
            subprocess.run(['bash', '-eu', '-c', block], cwd=work,
                           env=dict(os.environ, stage=str(stage)), check=True)
            assert files(current) == expected
            archives = sorted(current.parent.glob('date-range-catalog-previous.*'))
            assert len(archives) == iteration
            for generation in generations:
                matches = [folder for folder in archives if files(folder / 'catalog-installed') == generation]
                assert len(matches) == 1 and not matches[0].is_relative_to(stage)
            generations.append(expected)
        shutil.rmtree(stage)
        assert files(current) == generations[-1]
        for generation in generations[:-1]:
            assert sum(files(folder / 'catalog-installed') == generation for folder in archives) == 1
    print('Date catalog publication: two fresh trees and both earlier generations survive temporary-stage cleanup byte for byte')


if __name__ == '__main__':
    main()
