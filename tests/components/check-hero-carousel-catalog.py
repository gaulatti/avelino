#!/usr/bin/env python3
"""Exercise every captured HeroCarousel configuration through the catalog."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog, imports, root = map(Path, sys.argv[1:])
native = json.loads((root / 'tests/consumer/native-hero-carousel-witnesses.json').read_text())
rows = [row for row in native['closed']
    if (row['appearance'], row['textScale'], row['dpr']) == ('light', 1, 1)]
assert len(rows) == 20
definitions = [dict(row['configuration'], api='BleeckerHeroCarousel', source=native['reference'],
    fixture='hero-' + row['configuration']['id'], carouselWidth=row['configuration']['width'],
    carouselHeight=row['configuration'].get('height'), width=640, height=400) for row in rows]
with tempfile.TemporaryDirectory(prefix='avelino-hero-catalog-') as temporary:
    directory = Path(temporary)
    inputs = directory / 'fixtures.json'
    inputs.write_text(json.dumps(dict(fixtures=definitions), ensure_ascii=False))
    environment = dict(os.environ, QML_IMPORT_PATH=str(imports), QT_QPA_PLATFORM='offscreen',
        QT_QUICK_BACKEND='software', QT_SCALE_FACTOR='1')

    def run(definition):
        image = directory / (definition['fixture'] + '.png')
        result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', definition['fixture'],
            '--case-definitions', str(inputs), '--capture', str(image)], env=environment, capture_output=True)
        log = (result.stdout + result.stderr).decode(errors='replace')
        assert result.returncode == 0, (definition['id'], result.returncode, log)
        assert not any(message in log for message in ['Unable to assign', 'ReferenceError', 'TypeError',
            'Error:', 'Binding loop', 'QFont::']), (definition['id'], log)
        meta = json.loads(Path(str(image) + '.json').read_text())
        assert meta['heroState']['appearances'] == meta['heroState']['wrapperInstances'] == 1
        assert meta['heroState']['disappearances'] == 0
        assert len(meta['heroMetrics']['entries']) == len(definition['items'])
        assert set(meta['heroFrame']) == {'caller', 'carousel', 'slides'}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, definitions))
    base = definitions[0]
    item = dict(id='a', title='A', width=91, height=80, color=0)
    invalid = [dict(base, source='unapproved'), dict(base, carouselWidth='337'),
        dict(base, carouselHeight={}), dict(base, carouselWidth=-1), dict(base, slot='unknown'),
        dict(base, disabled=1), dict(base, items={}), dict(base, width=320), dict(base, extra=True),
        dict(base, scroll=True), dict(base, items=[dict(item, height=-1)]),
        dict(base, items=[dict(item, color=0.5)]), dict(base, items=[item, item]),
        dict(base, items=[dict(item, id='\u00e9'), dict(item, id='e\u0301')])]
    for key in base:
        if key == 'api':
            continue
        value = dict(base)
        del value[key]
        invalid.append(value)
    for index, value in enumerate(invalid):
        inputs.write_text(json.dumps(dict(fixtures=[value])))
        result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', base['fixture'],
            '--case-definitions', str(inputs), '--capture', str(directory / f'invalid-{index}.png')],
            env=environment, capture_output=True)
        assert result.returncode == 6, (value, result.returncode, result.stderr.decode(errors='replace'))
print(f'HeroCarousel catalog: 20 native configurations and {len(invalid)} malformed definitions; parity pending')
