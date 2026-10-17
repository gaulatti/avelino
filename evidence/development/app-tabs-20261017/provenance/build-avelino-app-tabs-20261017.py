from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016'
attempt=base/sys.argv[1];cache=base/sys.argv[2];assert not attempt.exists();attempt.mkdir()
source=attempt/'source'
shutil.copytree(base/'surface-matrix-build-v4/source',source,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
# Preserve the known complete Qt fixture dependencies; refresh every producer,
# consumer, component fixture and script from the current worktree.
for directory in ['src','assets','samples','tests','cmake','scripts','tools']:
 if (root/directory).exists():shutil.copytree(root/directory,source/directory,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy2(root/'CMakeLists.txt',source/'CMakeLists.txt')
(source/'artifacts').mkdir(exist_ok=True)
hashes={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
(attempt/'inputs.json').write_text(json.dumps(dict(scope='Complete Qt compilation/fixture dependencies; native observations are projected in the consumer resources',sourceFiles=hashes),indent=2)+'\n')
shutil.copytree(cache/'build',attempt/'build',ignore=shutil.ignore_patterns('Testing'))
(attempt/'qt-artifacts').mkdir()
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-'+attempt.name,
 '-v',str(source)+':/work:ro','-v',str(attempt)+':/result:rw','-v',str(attempt/'qt-artifacts')+':/work/artifacts:rw',
 '-w','/work','avelino-toolchain:data-metrics-qt6.8.3','bash','-lc',
 'cmake -S /work -B /result/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DCMAKE_PREFIX_PATH=/opt/qt && cmake --build /result/build --parallel 2 && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software /result/build/tests/components/AvelinoComponentTests -input /work/tests/components/tst_app_tabs.qml -import /result/build/qml && cmake --install /result/build --prefix /result/install']
start=time.monotonic()
with (attempt/'run.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(attempt/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n')
print(attempt.name,r.returncode);print((attempt/'run.log').read_text()[-2500:]);raise SystemExit(r.returncode)
