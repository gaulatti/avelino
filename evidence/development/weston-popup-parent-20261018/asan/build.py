from pathlib import Path
import subprocess,json,time,hashlib
p=Path(__file__).resolve().parent;image='avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3';steps=[]
base=['docker','--context','colima-avelino-verify'];name='avelino-weston-popup-guard-asan-v1'
container=subprocess.check_output(base+['create','--name',name,'-v',str(p)+':/probe',image,'bash','-lc','touch /weston-13.0.4/libweston/desktop/surface.c && meson compile -C /probe/build -j2 && meson install -C /probe/build'],text=True).strip()
subprocess.run(base+['cp',str(p/'source')+'/.',container+':/weston-13.0.4'],check=True)
start=time.monotonic()
with(p/'build.log').open('w')as log:r=subprocess.run(base+['start','-a',container],stdout=log,stderr=subprocess.STDOUT)
state=json.loads(subprocess.check_output(base+['inspect',container],text=True))[0]['State']
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=r.returncode,containerExitCode=state['ExitCode'],container=container,seconds=time.monotonic()-start),indent=2)+'\n')
print('Candidate sanitizer build',r.returncode,state['ExitCode'])
if r.returncode or state['ExitCode']:raise SystemExit(1)
(p/'installed-files.json').write_text(json.dumps({str(f.relative_to(p/'install')):hashlib.sha256(f.read_bytes()).hexdigest()for f in (p/'install').rglob('*')if f.is_file()},indent=2)+'\n')
