from pathlib import Path
import json,runpy,shutil,sys
name=sys.argv[1];sdk=Path('/opt/qt');metadata=sdk/'share/avelino/qt-software-rectangle/provenance.json'
if name in ['broken-chain','wrong-header-record']:
 record=json.loads(metadata.read_text());record['originalLibrarySha256'if name=='broken-chain'else'installedHeaderSha256']='0'*64;metadata.write_text(json.dumps(record))
elif name=='stale-header':
 shutil.copyfile('/probe/original-rectangle.h',sdk/'include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h')
elif name=='stale-library':
 shutil.copyfile('/seed/product-quick.so',sdk/'lib/libQt6Quick.so.6.8.3')
else:assert name in ['valid','missing-stage']
runpy.run_path('/probe/driver-preflight.py',run_name='__main__')
