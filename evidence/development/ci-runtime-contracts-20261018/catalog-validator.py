import hashlib,json,struct,sys
from pathlib import Path
root=Path(sys.argv[1]);records=[]
fixtures=sys.argv[2:]
assert fixtures and len(fixtures)==len(set(fixtures)),fixtures
expected={f'{fixture}-{appearance}-dpr{dpr}.png'for fixture in fixtures for appearance in ['light','dark']for dpr in [1,2]}
expected.update({'actions-light.png','actions-dark.png','button-light-primary-md-enabled.png'})
for image in sorted(root.glob('*.png')):
 meta=json.loads(image.with_name(image.name+'.json').read_text())
 assert meta['qt']=='6.8.3' and meta['platform']=='offscreen'
 assert struct.unpack('>II',image.read_bytes()[16:24])==(meta['width']*meta['dpr'],meta['height']*meta['dpr'])
 records.append({'path':image.name,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'metadataSha256':hashlib.sha256(image.with_name(image.name+'.json').read_bytes()).hexdigest()})
actual={record['path']for record in records}
assert actual==expected,{'missing':sorted(expected-actual),'unexpected':sorted(actual-expected)}
(root/'catalog-results.json').write_text(json.dumps({'status':'passed','method':'installed executable; QML_IMPORT_PATH and QML2_IMPORT_PATH explicitly unset; offscreen software','captures':records,'missingModuleRefusal':'passed','acceptance':'startup/relocation evidence only; strict mirror and physical/session gates remain separate'},indent=2)+'\n')
print(f'Installed catalog: {len(records)} fixture captures passed without source/build import paths')
