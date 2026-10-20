import hashlib, json, subprocess
from pathlib import Path
def command(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()
files = sorted([Path('CMakeLists.txt'), Path('CMakePresets.json')] +
    [p for folder in ['src', 'samples', 'assets', 'tokens', 'tests', 'scripts', 'cmake', 'tools', 'evidence/geometry']
     for p in Path(folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts])
# The CI bind mount belongs to the runner UID, while the toolchain runs as root.
# Trust only this explicit checkout for these read-only provenance commands.
git = ['git', '-c', f'safe.directory={Path.cwd()}']
qt_opacity_stage = json.loads(Path('/opt/qt/share/avelino/qt-software-opacity/provenance.json').read_text())
qt_software_renderer = json.loads(Path('/opt/qt/share/avelino/qt-software-rectangle/provenance.json').read_text())
qt_quick_sha256 = hashlib.sha256(Path('/opt/qt/lib/libQt6Quick.so.6.8.3').read_bytes()).hexdigest()
qt_rectangle_header_sha256 = hashlib.sha256(Path('/opt/qt/include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h').read_bytes()).hexdigest()
assert qt_opacity_stage['qt'] == '6.8.3' and not qt_opacity_stage['nativeAcceptance']
assert qt_software_renderer['qt'] == '6.8.3' and not qt_software_renderer['nativeAcceptance']
assert qt_software_renderer['previousStage'] == 'qt-software-opacity'
assert qt_software_renderer['originalLibrarySha256'] == qt_opacity_stage['installedLibrarySha256']
assert qt_software_renderer['archiveSha256'] == qt_opacity_stage['archiveSha256']
assert qt_opacity_stage['patchSha256'] == hashlib.sha256(Path('tools/qt-software-opacity.patch').read_bytes()).hexdigest()
assert qt_software_renderer['patchSha256'] == hashlib.sha256(Path('tools/qt-software-rectangle.patch').read_bytes()).hexdigest()
assert qt_software_renderer['installedLibrarySha256'] == qt_quick_sha256
assert qt_software_renderer['installedHeaderSha256'] == qt_rectangle_header_sha256
metadata = {
    'sourceRevision': command(*git, 'rev-parse', 'HEAD'),
    'uncommittedChanges': bool(command(*git, 'status', '--porcelain')),
    'compiler': command('c++', '--version'),
    'qt': command('qmake', '-query', 'QT_VERSION'),
    'qtQuickSha256': qt_quick_sha256,
    'qtSoftwareRenderer': qt_software_renderer,
    'qtSoftwareRendererStages': [qt_opacity_stage, qt_software_renderer],
    'cmake': command('cmake', '--version'),
    'installedPackages': command('dpkg-query', '-W'),
    'sourceInputs': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
}
Path('artifacts/linux/environment.json').write_text(json.dumps(metadata, indent=2)+'\n')
