import hashlib,json,subprocess
from pathlib import Path

reader=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
cache={}
def staged(path):
    reader.stdin.write((':'+str(path)+'\n').encode());reader.stdin.flush();header=reader.stdout.readline().split()
    assert len(header)==3 and header[1]==b'blob',(path,header)
    count=int(header[2]);data=reader.stdout.read(count);assert len(data)==count and reader.stdout.read(1)==b'\n';return data
def sha(path):
    if str(path) not in cache:cache[str(path)]=hashlib.sha256(staged(path)).hexdigest()
    return cache[str(path)]
def manifest(root,name):
    value=json.loads(staged(root/name));actual={p.decode().removeprefix(str(root)+'/') for p in subprocess.check_output(['git','ls-files','-z','--',str(root)]).split(b'\0') if p}
    assert actual==set(value['files'])|{name},(root,actual^set(value['files'])^{name})
    for path,h in value['files'].items():assert sha(root/path)==h,path
    return value
root=Path('evidence/development/spinner');candidate=manifest(root,'candidate.json')
native=manifest(Path('evidence/reference-investigations/spinner-20261015'),'investigation.json')
assert not native['accepted']
assert sha('evidence/geometry/native-spinner.json')==sha('evidence/reference-investigations/spinner-20261015/captures.json')
provenance=json.loads(staged('evidence/reference-investigations/spinner-20261015/tooling-provenance.json'))
artifact=provenance['toolArtifact'];assert hashlib.sha256(Path(artifact['locator']).read_bytes()).hexdigest()==artifact['sha256']==native['sourceToolArtifact']
assert provenance['cleanReplay']['filesCompared']==provenance['cleanReplay']['byteIdenticalFiles']==335
env=json.loads(staged(root/'build-environment.json'))
for path,h in env['sourceInputs'].items():assert sha(path)==h,path
assert json.loads(staged(root/'sessions/environment.json'))['sourceInputs']==env['sourceInputs']
for group in [p.name for p in (root/'regression-inputs').iterdir()]:assert json.loads(staged(root/'regression-inputs'/group/'environment.json'))['sourceInputs']==env['sourceInputs']
regressions=json.loads(staged(root/'regressions.json'));assert regressions['auditedPairs']==3254
for r in regressions['results']:
    assert sha(r['previousImage'])==r['sha256'] and sha(r['previousMetadata'])==r['metadataSha256']
    if r['status'].startswith('byte-identical'):assert r['currentSha256']==r['sha256'] and r['currentMetadataSha256']==r['metadataSha256']
    else:assert sha(r['currentImage'])==r['currentSha256'] and sha(r['currentMetadata'])==r['currentMetadataSha256']
old=json.loads(subprocess.check_output(['git','show','HEAD:docs/parity-inventory.json'],text=True));new=json.loads(staged('docs/parity-inventory.json'))
a={e['id']:e for e in old['desktop']['entries']};b={e['id']:e for e in new['desktop']['entries']}
assert {k for k in a if a[k]!=b[k]}=={'BleeckerLoadingSpinner','BleeckerButton','BleeckerLoadingOverlay'}
assert old['television']==new['television'] and old['exceptions']==new['exceptions']
assert sum(e['status']=='verification-pending' for e in b.values())==46
assert all(g['status']=='pending' for name in ['BleeckerLoadingSpinner','BleeckerLoadingOverlay'] for g in b[name]['runtimeGates'].values())
changed=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
assert not any(p.startswith('reference/') for p in changed)
assert not any(p.startswith('.agents/') or p=='AGENTS.md' for p in changed)
reader.stdin.close();assert reader.wait()==0
print('Verified staged source/candidate manifests,',len(env['sourceInputs']),'tested inputs, 3254 preceding pairs, unchanged pins/TV/exceptions and',len(cache),'unique file checksums')
