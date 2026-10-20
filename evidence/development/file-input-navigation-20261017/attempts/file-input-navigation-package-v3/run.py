from pathlib import Path
import hashlib,json,shutil,subprocess
p=Path(__file__).resolve().parent;r=p.parent
producer=r/'file-input-qt-v25';consumer=r/'file-input-navigation-package-v2'
assert json.loads((producer/'result.json').read_text())['exitCode']==0
assert json.loads((consumer/'result.json').read_text())['exitCode']==0
source=json.loads((producer/'inputs.json').read_text())['files'];prior=json.loads((consumer/'inputs.json').read_text())
assert prior['consumerFiles']=={name.removeprefix('tests/consumer/'):sha for name,sha in source.items()if name.startswith('tests/consumer/')}
shutil.copytree(producer/'install',p/'install');(p/'consumer-build').mkdir();shutil.copy2(consumer/'runtime/consumer-build/InstalledConsumer',p/'consumer-build/InstalledConsumer')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
record=dict(accepted=False,producer=producer.name,consumerBinarySource=consumer.name,consumerSourceProducer=prior['producer'],consumerSourceIdenticalToFinal=True,consumerSha256=sha(p/'consumer-build/InstalledConsumer'),packageFiles={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()},image=prior['image'],imageId=prior['imageId'])
(p/'inputs.json').write_text(json.dumps(record,indent=2)+'\n')
subprocess.run(['python3',str(p/'run-contexts.py')],check=True)
