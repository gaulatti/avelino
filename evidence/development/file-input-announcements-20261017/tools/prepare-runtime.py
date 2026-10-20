from pathlib import Path
import hashlib,json,shutil,subprocess
r=Path(__file__).resolve().parent
producer=r/'file-input-qt-v21'
assert json.loads((producer/'result.json').read_text())['exitCode']==0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
images={tag:json.loads(subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',tag]))[0] for tag in ['avelino-toolchain:recovered-20261017-qt6.8.3','avelino-toolchain:recovered-a11y-20261017-qt6.8.3']}
(r/'recovered-toolchain-v1/image-inspect.json').write_text(json.dumps(images,indent=2)+'\n')
for name in ['file-input-announcement-package-v2','file-input-error-reader-v3','file-input-error-reader-v4']:
 p=r/name;shutil.copytree(producer/'install',p/'install')
 files={str(f.relative_to(p/'install')):sha(f)for f in (p/'install').rglob('*')if f.is_file()}
 tag='avelino-toolchain:recovered-20261017-qt6.8.3'if'package'in name else'avelino-toolchain:recovered-a11y-20261017-qt6.8.3'
 record=dict(accepted=False,producer='file-input-qt-v21',image=tag,imageId=images[tag]['Id'],packageFiles=files,physicalDisplay=False,physicalReaderAcceptance='pending')
 if 'package'in name:
  (p/'consumer-build').mkdir()
  shutil.copy2(r/'file-input-package-pilot-v9/consumer-build/InstalledConsumer',p/'consumer-build/InstalledConsumer')
  record.update(consumerSha256=sha(p/'consumer-build/InstalledConsumer'),consumerBinarySource='file-input-package-pilot-v9',consumerSourceChanged=False)
 else:
  (p/'fixtures').mkdir();(p/'fixtures/one.txt').write_text('Avelino controlled reader fixture\n')
 (p/'inputs.json').write_text(json.dumps(record,indent=2)+'\n')
print('Final producer package copied only after all commands completed successfully')
