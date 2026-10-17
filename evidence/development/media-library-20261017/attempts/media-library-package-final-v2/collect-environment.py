from pathlib import Path
import hashlib,json,subprocess
p=Path('/package')
def command(*args):return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT).strip()
digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
old=p/'environment.json';old.rename(p/'environment-seed.json')
files={str(f.relative_to(p)):digest(f) for f in (p/'install').rglob('*') if f.is_file()}
metadata=dict(scope='Current installed-chart package and actual runtime toolchain. Producer/consumer source snapshots are identified by inputs.json; environment-seed.json is preserved historical metadata only.',qt=command('qmake','-query','QT_VERSION'),compiler=command('c++','--version'),cmake=command('cmake','--version'),installedPackages=command('dpkg-query','-W'),architecture=command('uname','-m'),packageInputManifestSha256=digest(p/'inputs.json'),consumerSha256=digest(p/'consumer-build/InstalledConsumer'),installedFiles=files,physicalDisplay=False)
old.write_text(json.dumps(metadata,indent=2)+'\n')
