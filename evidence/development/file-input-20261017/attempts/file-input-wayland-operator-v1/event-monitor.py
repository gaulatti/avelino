from pathlib import Path
import json, time
import pyatspi
from gi.repository import GLib

p = Path('/probe')
desktop = pyatspi.Registry.getDesktop(0)
log = (p / 'events.jsonl').open('w', buffering=1)
def record(event):
    row = dict(time=time.time(), event=event.type, detail1=event.detail1, detail2=event.detail2)
    try:
        source = event.source
        row.update(name=source.name, role=source.getRoleName(), pid=source.get_process_id())
    except Exception as error:
        row['error'] = repr(error)
    log.write(json.dumps(row) + '\n')
pyatspi.Registry.registerEventListener(record, 'focus:', 'object:state-changed:focused',
    'object:state-changed:selected', 'object:selection-changed',
    'object:property-change:accessible-name', 'window:')
(p / 'event-monitor-ready').touch()
pyatspi.Registry.start()
