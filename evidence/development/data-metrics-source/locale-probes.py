import json,subprocess
from pathlib import Path
root=Path('../avelino-reference-vault/candidates/data-metrics-20261015-87d6fa9f').resolve()
for locale in ['en_US','de_DE','es_CL','fr_FR','ja_JP','ar_EG','hi_IN']:
 out=root/('locale-'+locale);out.mkdir()
 with (out/'run.log').open('w') as log:subprocess.run([str(root/'tool/NativeCapture'),str(out),'--format-only','-AppleLocale',locale],stdout=log,stderr=subprocess.STDOUT,check=True)
 data=json.loads((out/'captures.json').read_text());print(locale,'->',data['processLocale'],len(data['formatting']))
 assert data['processLocale']==locale and data['captures']==[],locale
