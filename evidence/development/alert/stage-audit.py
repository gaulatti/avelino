import hashlib,json,subprocess
from pathlib import Path
reader=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE);cache={}
def staged(path):
    reader.stdin.write((':'+str(path)+'\n').encode());reader.stdin.flush();header=reader.stdout.readline().split();assert len(header)==3 and header[1]==b'blob',(path,header)
    count=int(header[2]);data=reader.stdout.read(count);assert len(data)==count and reader.stdout.read(1)==b'\n';return data
def sha(path):
    if str(path) not in cache:cache[str(path)]=hashlib.sha256(staged(path)).hexdigest()
    return cache[str(path)]
def manifest(root,name):
    value=json.loads(staged(root/name));actual={p.decode().removeprefix(str(root)+'/') for p in subprocess.check_output(['git','ls-files','-z','--',str(root)]).split(b'\0') if p}
    assert actual==set(value['files'])|{name},root
    for path,h in value['files'].items():assert sha(root/path)==h,path
    return value
root=Path('evidence/development/alert');candidate=manifest(root,'candidate.json')
native=manifest(Path('evidence/reference-investigations/alert-20261015'),'investigation.json')
proposal=manifest(Path('evidence/reference-proposals/alert-20261015'),'proposal.json')
boundary=manifest(Path('evidence/reference-investigations/prose-boundaries-20261015'),'investigation.json')
assert boundary['accepted'] is False and boundary['trustedQtCases']==84 and boundary['untrustedContextWitnesses']==['text2-hosttrue-probefalse.png']
boundaryProvenance=json.loads(staged('evidence/reference-investigations/prose-boundaries-20261015/tooling-provenance.json'))
assert hashlib.sha256(Path(boundaryProvenance['toolArtifact']['locator']).read_bytes()).hexdigest()==boundaryProvenance['toolArtifact']['sha256']==boundary['sourceToolArtifact']
assert boundaryProvenance['cleanReplay']['filesCompared']==boundaryProvenance['cleanReplay']['byteIdenticalFiles']==179
assert not native['accepted'] and not proposal['accepted'] and sha('scripts/prepare-proposal.py')==proposal['postprocessor']['sha256']
assert sha('evidence/geometry/native-alert.json')==sha('evidence/reference-investigations/alert-20261015/captures.json')
text=json.loads(staged('evidence/geometry/native-alert-text-layout.json'));assert text['cases']==json.loads(staged('evidence/reference-investigations/alert-20261015/text-layout/measurements.json'))
provenance=json.loads(staged('evidence/reference-investigations/alert-20261015/tooling-provenance.json'));artifact=provenance['toolArtifact']
assert hashlib.sha256(Path(artifact['locator']).read_bytes()).hexdigest()==artifact['sha256']==native['sourceToolArtifact']
assert provenance['cleanReplay']['filesCompared']==provenance['cleanReplay']['byteIdenticalFiles']==722
env=json.loads(staged(root/'build-environment.json'))
assert len(env['sourceInputs'])==239
for path,h in env['sourceInputs'].items():assert sha(path)==h,path
assert json.loads(staged(root/'sessions/environment.json'))['sourceInputs']==env['sourceInputs']
assert json.loads(staged(root/'captures/environment.json'))['sourceInputs']==env['sourceInputs']
for directory in (root/'regression-inputs').iterdir():assert json.loads(staged(directory/'environment.json'))['sourceInputs']==env['sourceInputs']
regressions=json.loads(staged(root/'regressions.json'));assert regressions['auditedPairs']==3258
for r in regressions['results']:
    assert sha(r['previousImage'])==r['sha256'] and sha(r['previousMetadata'])==r['metadataSha256']
    if r['status'].startswith('byte-identical'):assert r['currentSha256']==r['sha256'] and r['currentMetadataSha256']==r['metadataSha256']
    else:assert sha(r['currentImage'])==r['currentSha256'] and sha(r['currentMetadata'])==r['currentMetadataSha256']
for s in json.loads(staged(root/'regression-comparison.json'))['selections']:assert sha(s['originalManifest'])==s['originalManifestSha256']
old=json.loads(subprocess.check_output(['git','show','HEAD:docs/parity-inventory.json'],text=True));new=json.loads(staged('docs/parity-inventory.json'))
a={e['id']:e for e in old['desktop']['entries']};b={e['id']:e for e in new['desktop']['entries']}
assert {k for k in a if a[k]!=b[k]}==set(json.loads(staged(root/'inventory-changes.json'))['entries'])
assert old['television']==new['television'] and old['exceptions']==new['exceptions']
assert sum(e['status']=='verification-pending' for e in b.values())==47
assert b['BleeckerAlert']['status']=='verification-pending' and all(g['status']=='pending' for g in b['BleeckerAlert']['runtimeGates'].values())
changed=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
assert not any(p.startswith('reference/') or p.startswith('.agents/') or p=='AGENTS.md' for p in changed)
reader.stdin.close();assert reader.wait()==0
print('Verified candidate/native/proposal manifests, 239 tested inputs, 3258 preceding pairs, unchanged pins/TV/exceptions and',len(cache),'file checksums')
