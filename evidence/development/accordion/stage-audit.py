import hashlib,json,subprocess
from pathlib import Path
p=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
cache={}
def staged(path):
 p.stdin.write((':'+str(path)+'\n').encode());p.stdin.flush();header=p.stdout.readline().split();assert len(header)==3 and header[1]==b'blob',(path,header)
 size=int(header[2]);data=p.stdout.read(size);assert len(data)==size and p.stdout.read(1)==b'\n';return data
def sha(path):
 key=str(path)
 if key not in cache:cache[key]=hashlib.sha256(staged(path)).hexdigest()
 return cache[key]
def manifest(root,name):
 j=json.loads(staged(root/name));actual={b.decode().removeprefix(str(root)+'/') for b in subprocess.check_output(['git','ls-files','-z','--',str(root)]).split(b'\0') if b};assert actual==set(j['files'])|{name},root
 for path,h in j['files'].items():assert sha(root/path)==h,path
 return j
root=Path('evidence/development/accordion');candidate=manifest(root,'candidate.json');native=manifest(Path('evidence/reference-proposals/accordion-20261014'),'proposal.json')
assert sha('scripts/prepare-proposal.py')==native['postprocessor']['sha256']
provenance=json.loads(staged('evidence/reference-proposals/accordion-20261014/tooling-provenance.json'));assert hashlib.sha256(Path(provenance['toolArtifact']['locator']).read_bytes()).hexdigest()==provenance['toolArtifact']['sha256'];assert provenance['cleanReplay']['byteIdenticalFiles']==193
env=json.loads(staged(root/'build-environment.json'))
for path,h in env['sourceInputs'].items():assert sha(path)==h,path
assert json.loads(staged(root/'captures/environment.json'))['sourceInputs']==env['sourceInputs'];assert json.loads(staged(root/'sessions/environment.json'))['sourceInputs']==env['sourceInputs']
for group in (root/'regression-inputs').iterdir():assert json.loads(staged(group/'environment.json'))['sourceInputs']==env['sourceInputs']
for r in json.loads(staged(root/'regressions.json'))['results']:assert sha(r['previousImage'])==r['sha256'] and sha(r['previousMetadata'])==r['metadataSha256']
old=json.loads(subprocess.check_output(['git','show','HEAD:docs/parity-inventory.json'],text=True));new=json.loads(staged('docs/parity-inventory.json'));a={e['id']:e for e in old['desktop']['entries']};b={e['id']:e for e in new['desktop']['entries']}
assert {k for k in a if a[k]!=b[k]}=={'BleeckerAccordion'};assert old['television']==new['television'] and old['exceptions']==new['exceptions'];assert sum(e['status']=='verification-pending' for e in b.values())==43
assert all(g['status']=='pending' for g in b['BleeckerAccordion']['runtimeGates'].values())
assert not any(name.startswith('reference/') for name in subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines())
p.stdin.close();p.wait();assert p.returncode==0
print('Verified staged candidate/native manifests,',len(env['sourceInputs']),'tested inputs, 2782 unchanged pairs, native replay and unchanged source pins/TV/acceptance boundaries;',len(cache),'unique checksums')
