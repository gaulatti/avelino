from pathlib import Path
import json, os, shutil, subprocess
p = Path('/probe')
environment = json.loads((p/'session-env.json').read_text())
runtime = Path(environment['XDG_RUNTIME_DIR'])
target = p/'speech-dispatcher-logs'
shutil.copytree(runtime/'speech-dispatcher/log', target)
packages = ['orca','python3-pyatspi','at-spi2-core','speech-dispatcher','speech-dispatcher-espeak-ng']
versions = subprocess.check_output(['dpkg-query','-W',*packages],text=True)
(p/'package-versions.txt').write_text(versions)
pid=json.loads((p/'client-pid.json').read_text())['pid']
keys={'DISPLAY','QT_QPA_PLATFORM','QT_QUICK_BACKEND','QT_SCALE_FACTOR','QT_LINUX_ACCESSIBILITY_ALWAYS_ON','QT_ACCESSIBILITY','NO_AT_BRIDGE','AT_SPI_BUS_ADDRESS','XDG_CONFIG_HOME','LANG','WAYLAND_DISPLAY','QSG_RHI_BACKEND','LIBGL_ALWAYS_SOFTWARE','QSG_INFO'}
values={}
for pair in Path('/proc/'+str(pid)+'/environ').read_bytes().split(b'\0'):
    if b'=' not in pair: continue
    key,value=pair.decode().split('=',1)
    if key in keys: values[key]=value
(p/'client-environment-allowlist.json').write_text(json.dumps(values,indent=2)+'\n')
