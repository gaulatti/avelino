from pathlib import Path
import json, os, subprocess, time
p = Path('/probe')
os.environ.update(json.loads((p / 'session-env.json').read_text()))
for phase, keys in [('folder', ['Down']), ('one-text', ['Down']), ('accepted', ['Return'])]:
    subprocess.run(['xdotool', 'key', '--clearmodifiers', *keys], check=True)
    time.sleep(.7)
    subprocess.run(['python3', '/probe/dump.py', 'keyboard-' + phase + '-v1.json'], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['import', '-window', 'root', '/probe/keyboard-' + phase + '-v1.png'], check=True)
    print(phase, flush=True)
