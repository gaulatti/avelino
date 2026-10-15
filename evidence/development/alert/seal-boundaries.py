import hashlib,json,shutil,subprocess,tarfile
from pathlib import Path
root=Path('../avelino-reference-vault/candidates/prose-boundaries-20261015-ea0825f');old=json.load(open('evidence/reference-investigations/alert-20261015/tooling-provenance.json'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
env={**old['environment'],'capturePreparationRevision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()};write(root/'toolchain.json',env)
inputs=sorted([p for p in (root/'cached-reference').rglob('*') if p.is_file()]+list((root/'src').glob('*.swift'))+[root/'tool/build-probe.py',root/'toolchain.json']);files={str(p.relative_to(root)):sha(p) for p in inputs};assert len(files)==37
for p,h in old['toolArtifact']['files'].items():
    if p.startswith('cached-reference/'):assert files[p]==h,p
archive=root/'native-prose-boundaries-replay.tar.gz'
with tarfile.open(archive,'w:gz') as t:
    for p in inputs:t.add(p,arcname=str(p.relative_to(root)),recursive=False)
clean=root/'clean-replay';clean.mkdir()
with tarfile.open(archive) as t:t.extractall(clean,filter='data')
for p,h in files.items():assert sha(clean/p)==h
for name in ['context','initial','boundary']:
    subprocess.run(['python3',str(clean/'tool/build-probe.py'),name],check=True)
    out=clean/'raw'/name;out.mkdir(parents=True);subprocess.run([str(clean/'tool'/name),str(out)],check=True)
names={str(p.relative_to(root/'raw')) for p in (root/'raw').rglob('*') if p.is_file()};assert len(names)==179
changed=sorted(p for p in names if (root/'raw'/p).read_bytes()!=(clean/'raw'/p).read_bytes())
replay={'filesCompared':179,'byteIdenticalFiles':179-len(changed),'changedFiles':changed,'method':'37 archived input hashes verified; three probes compiled in a clean extraction; all PNGs and complete metadata compared byte-for-byte'};write(Path('artifacts/alert/boundary-replay.json'),replay);assert not changed,changed
limits=['Measured Latin/ASCII character boundaries only; broader scripts and grapheme-count behavior remain unaccepted.','The context probe includes one native-hosted primary 18-point TextRenderer image mismatch; that instrumented view is diagnostic and excluded from trusted line witnesses.','Native context-probe windows do not record backing DPR or establish physical/reader acceptance; pure ImageRenderer cases explicitly render at DPR2.','All tools link preserved source-verified objects; fresh full Sabella compilation and public helper download remain pending.']
provenance={**old,'toolArtifact':{'locator':str(archive),'sha256':sha(archive),'files':files},'environment':env,'cleanReplay':replay,'limitations':limits};write(root/'tooling-provenance.json',provenance)
dst=Path('evidence/reference-investigations/prose-boundaries-20261015');shutil.copytree(root/'raw',dst);shutil.copy2(root/'tooling-provenance.json',dst/'tooling-provenance.json');write(dst/'native-replay.json',replay)
cases=[]
for name in ['initial','boundary']:
    rows=json.load(open(dst/name/'measurements.json'));assert len(rows)==(32 if name=='initial' else 48)
    for c in rows:
        assert c['probeByteIdentical'] and (dst/name/c['path']).read_bytes()==(dst/name/(Path(c['path']).stem+'-probed.png')).read_bytes()
        cases.append({**c,'sourcePath':name+'/'+c['path'],'dpr':2,'weight':'medium' if c['primary'] else 'semibold'})
context=json.load(open(dst/'context/measurements.json'));mismatches=[]
for c in context:
    if c['probed']:continue
    partner=next(p for p in context if p['text']==c['text'] and p['primary']==c['primary'] and p['hosted']==c['hosted'] and p['probed'])
    identical=(dst/'context'/c['path']).read_bytes()==(dst/'context'/partner['path']).read_bytes()
    if not identical:mismatches.append(c['path'])
    if not c['hosted']:
        assert identical
        cases.append({**c,'lines':partner['lines'],'sourcePath':'context/'+c['path'],'dpr':2,'weight':'medium' if c['size']==14 else 'semibold','probeByteIdentical':True})
assert mismatches==['text2-hosttrue-probefalse.png'] and len(cases)==84
write(Path('evidence/geometry/native-prose-boundaries.json'),{'reference':old['referenceRevision'],'cases':cases,'untrustedContextWitnesses':mismatches})
report={'schemaVersion':1,'reference':old['referenceRevision'],'accepted':False,'existingExpectedImagesChanged':False,'status':'measured short-token boundaries; complete wrapping and physical acceptance pending','sourceToolArtifact':sha(archive),'records':96,'trustedQtCases':84,'untrustedContextWitnesses':mismatches,'limitations':limits,'files':{str(p.relative_to(dst)):sha(p) for p in sorted(dst.rglob('*')) if p.is_file()}};write(dst/'investigation.json',report)
print('Sealed short-token boundaries:',replay,'trusted Qt cases',len(cases),'untrusted hosted context',mismatches)
