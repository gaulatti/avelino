from pathlib import Path
import hashlib,json,shutil
root=Path('../avelino-reference-vault/candidates/data-metrics-20261015-87d6fa9f');out=Path('evidence/reference-investigations/data-metrics-20261015');assert not out.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
replay=json.loads((root/'clean-replay.json').read_text());assert replay['filesCompared']==replay['byteIdenticalFiles']==3160 and replay['changedFiles']==[]
shutil.copytree(root/'captures',out)
for folder in root.glob('locale-*'):shutil.copytree(folder,out/folder.name)
for name in ['clean-replay.json','capture.log']:shutil.copy2(root/name,out/name)
old=json.loads(Path('evidence/reference-investigations/sidebar-brand-20261015/tooling-provenance.json').read_text());archive=root/'native-data-metrics-replay.tar.gz'
provenance={'schemaVersion':1,'referenceRevision':old['referenceRevision'],'referenceArchiveSha256':old['referenceArchiveSha256'],'toolArtifact':{'locator':str(archive),'sha256':sha(archive),'files':json.loads((root/'replay-inputs.json').read_text())},'environment':json.loads((root/'toolchain.json').read_text()),'dependencies':old['dependencies'],'cleanReplay':{k:v for k,v in replay.items() if k!='results'},'limitations':['Native ImageRenderer source evidence only; Qt implementation and complete mirror acceptance remain pending.','1048 root and 1048 reconstructed layout witnesses preserve unmodified public PNG bytes after warmup.','Seven process-local AppleLocale argument overrides change no user preferences; metric process locale and delta environment locale are recorded separately.','The preserved source-verified module/object is linked; fresh complete Sabella compilation and public helper download remain pending.','Native monospaced/symbol faces are measured but are not redistributed or approved as Linux equivalents.','Native numeric-transition frames, keyboard/focus, physical sessions, actual readers and broader composition remain pending.']}
write(out/'tooling-provenance.json',provenance)
report={'schemaVersion':1,'reference':old['referenceRevision'],'status':'measured native source; Linux implementation and complete parity remain pending','accepted':False,'existingExpectedImagesChanged':False,'sourceToolArtifact':sha(archive),'captures':1048,'metricCaptures':416,'statCardCaptures':344,'iconBadgeCaptures':184,'kbdCaptures':96,'anchorCaptures':8,'instrumentationIdentityWitnesses':2096,'processLocales':7,'localeFormatterWitnesses':1330,'byteIdenticalReplayFiles':3160,'files':{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()}}
write(out/'investigation.json',report);print('Preserved',len(report['files']),'source evidence files')
