from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

root = Path(tempfile.mkdtemp(prefix='avelino-search-provider-', dir='/home'))
inside, outside = root / 'inside', root / 'inside-peer'
inside.mkdir(); outside.mkdir()
token = 'avelinoulnacerulean'
(inside / (token + '-name.txt')).write_text('Controlled filename-only match.\n')
(inside / 'pine-only.txt').write_text('Controlled content token: ' + token + '\n')
(outside / (token + '-outside.txt')).write_text('Controlled other-root filename match.\n')
env = dict(os.environ, GSETTINGS_BACKEND='keyfile')
for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'),
                  ('XDG_DATA_HOME', 'data'), ('XDG_RUNTIME_DIR', 'runtime')]:
    folder = root / name; folder.mkdir(mode=0o700); env[key] = str(folder)
schema = 'org.freedesktop.Tracker3.Miner.Files'
settings = [('index-recursive-directories', json.dumps([str(inside), str(outside)])),
            ('index-single-directories', '[]'), ('initial-sleep', '0')]
for key, value in settings:
    subprocess.run(['gsettings', 'set', schema, key, value], env=env, check=True)
for command in [['gsettings', 'list-recursively', schema], ['/usr/libexec/tracker-miner-fs-3', '--eligible', str(inside / (token + '-name.txt'))], ['/usr/libexec/tracker-miner-fs-3', '--eligible', str(inside / 'pine-only.txt')]]:
    status = subprocess.run(command, env=env, capture_output=True, text=True)
    print(json.dumps({'phase': 'configuration', 'command': command, 'exitCode': status.returncode, 'stdout': status.stdout, 'stderr': status.stderr}), flush=True)
spec = {'inside': inside.as_uri() + '/', 'outside': outside.as_uri() + '/', 'token': token}
(root / 'spec.json').write_text(json.dumps(spec))
inner = root / 'query.py'
inner.write_text(r'''
from pathlib import Path
import json
import sys
import time
import gi
gi.require_version('Tracker', '3.0')
from gi.repository import Tracker

root = Path(sys.argv[1]); spec = json.loads((root / 'spec.json').read_text())
connection = Tracker.SparqlConnection.bus_new('org.freedesktop.Tracker3.Miner.Files', None, None)

def execute(text, bindings=None):
    statement = connection.query_statement(text, None)
    for key, value in (bindings or {}).items():
        statement.bind_string(key, value)
    cursor = statement.execute(None); rows = []
    try:
        while cursor.next(None):
            rows.append(cursor.get_string(0)[0])
    finally:
        cursor.close()
    return rows

all_files = 'SELECT DISTINCT ?url WHERE { ?file a nfo:FileDataObject ; nie:url ?url } ORDER BY ?url'
deadline = time.monotonic() + 50
while True:
    current = execute(all_files)
    print(json.dumps({'phase': 'indexing', 'urls': current}), flush=True)
    if len([url for url in current if url.startswith(spec['inside']) or url.startswith(spec['outside'])]) >= 3:
        break
    if time.monotonic() >= deadline:
        raise RuntimeError('Filesystem index did not expose all three controlled files within the observation interval')
    time.sleep(0.5)

def query(kind, scoped):
    if kind == 'filename':
        expression = '?file a nfo:FileDataObject ; nie:url ?url ; nfo:fileName ?name . FILTER(CONTAINS(LCASE(?name), LCASE(~needle)))'
    else:
        expression = '?file a nfo:FileDataObject ; nie:url ?url . { ?file fts:match ~needle } UNION { ?file nie:interpretedAs ?document . ?document fts:match ~needle }'
    if scoped:
        expression += ' FILTER(STRSTARTS(?url, ~folder))'
    bindings = {'needle': spec['token']}
    if scoped: bindings['folder'] = spec['inside']
    return execute('SELECT DISTINCT ?url WHERE { ' + expression + ' } ORDER BY ?url', bindings)

deadline = time.monotonic() + 50
while True:
    values = {kind + ('-folder' if scoped else '-global'): query(kind, scoped)
              for kind in ['filename', 'content'] for scoped in [False, True]}
    print(json.dumps({'phase': 'queries', 'values': values}), flush=True)
    if any(url.endswith('/pine-only.txt') for url in values['content-folder']):
        break
    if time.monotonic() >= deadline:
        raise RuntimeError('Content extractor did not expose the controlled content-only file')
    time.sleep(0.5)
assert len(values['filename-global']) == 2 and len(values['filename-folder']) == 1
assert len(values['content-global']) == 3 and len(values['content-folder']) == 2
assert all(url.startswith(spec['inside']) for url in values['content-folder'])
connection.close()
print(json.dumps({'phase': 'complete', 'values': values, 'accepted': False}), flush=True)
''')
result = subprocess.run(['dbus-run-session', '--', '/usr/bin/python3', str(inner), str(root)], env=env)
raise SystemExit(result.returncode)
