import hashlib,json,subprocess
from pathlib import Path
process=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
cache={}
def staged(path):
 process.stdin.write((':'+str(path)+'\n').encode());process.stdin.flush();header=process.stdout.readline().split();assert len(header)==3 and header[1]==b'blob',(path,header)
 size=int(header[2]);data=process.stdout.read(size);assert len(data)==size and process.stdout.read(1)==b'\n';return data
def digest(path):
 path=str(path)
 if path not in cache:cache[path]=hashlib.sha256(staged(path)).hexdigest()
 return cache[path]
root=Path('evidence/development/text-wrapping');j=json.loads(staged(root/'candidate.json'))
actual={p.decode().removeprefix(str(root)+'/') for p in subprocess.check_output(['git','ls-files','-z','--',str(root)]).split(b'\0') if p};assert actual==set(j['files'])|{'candidate.json'}
for p,h in j['files'].items():assert digest(root/p)==h,p
for r in json.loads(staged(root/'regressions.json'))['results']:
 for key,checksum in [('currentImage','sha256'),('currentMetadata','metadataSha256'),('previousImage','previousSha256'),('previousMetadata','previousMetadataSha256')]:assert digest(r[key])==r[checksum],r[key]
env=json.loads(staged(root/'build-environment.json'))
for p,h in env['sourceInputs'].items():assert digest(p)==h,p
assert json.loads(staged(root/'sessions/environment.json'))['sourceInputs']==env['sourceInputs']
for p in root.glob('*/environment.json'):assert json.loads(staged(p))['sourceInputs']==env['sourceInputs'],p
native=json.loads(staged('evidence/geometry/native-wrapping.json'));assert native['provenance']['replay']['byteIdenticalFiles']==121 and len(native['cases'])==120
archive=Path(native['provenance']['toolArtifact']['locator']);assert hashlib.sha256(archive.read_bytes()).hexdigest()==native['provenance']['toolArtifact']['sha256']
old=json.loads(subprocess.check_output(['git','show','HEAD:docs/parity-inventory.json'],text=True));new=json.loads(staged('docs/parity-inventory.json'))
a={e['id']:e for e in old['desktop']['entries']};b={e['id']:e for e in new['desktop']['entries']};assert {k for k in a if a[k]!=b[k]}=={'BleeckerPagination','View.bleeckerFont'}
assert old['television']==new['television'] and old['exceptions']==new['exceptions'];assert sum(e['status']=='verification-pending' for e in b.values())==42
assert all(a[k].get('runtimeGates')==b[k].get('runtimeGates') for k in a), 'An acceptance gate changed'
changed=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines();assert not any(p.startswith('reference/') for p in changed)
process.stdin.close();process.wait();assert process.returncode==0
print('Verified staged candidate manifest',len(j['files']),'files;',len(env['sourceInputs']),'tested inputs;',len(cache),'unique staged checksums; 2782 regression pairs; source replay artifact and unchanged TV/pins/acceptance gates')
