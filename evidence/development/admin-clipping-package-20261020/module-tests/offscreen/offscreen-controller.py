from pathlib import Path
import json,hashlib,io,tarfile,subprocess,time,sys
P=Path(__file__).resolve().parent
ROOT=Path('/Users/gaulatti/source/gaulatti/avelino')
PACKAGE=ROOT/'artifacts/resumed-avelino-20261016/admin-clipping-compiled-v1/output/package'
OUT=ROOT/'artifacts/resumed-avelino-20261016/admin-clipping-installed-tests-v1'
BUILD=Path('/Users/gaulatti/.codex/tmp/avelino-admin-clipping-compiled-20261020-v1')
result=json.loads((BUILD/'result.json').read_text());inputs=json.loads((BUILD/'inputs.json').read_text());assert result['exitCode']==0
scale=sys.argv[1];name='dpr'+scale;assert scale in ['1','2'];assert not (P/(name+'.json')).exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=['tests/components/tst_admin_shell.qml','tests/components/native-admin-divider.js','tests/consumer/AdminShellCase.qml','tests/consumer/AdminShell.qml','tests/consumer/native-admin-shell-colours.js','tests/consumer/native-admin-shell-witnesses.json']
original={n:(ROOT/n).read_bytes() for n in files};assert all(hashlib.sha256(b).hexdigest()==inputs['sourceFiles'][n] for n,b in original.items())
payload=dict(original);payload['tests/components/witnesses.js']=b'var data = '+original['tests/consumer/native-admin-shell-witnesses.json']+b';\n'
f='tests/components/tst_admin_shell.qml';text=payload[f].decode().replace('import QtTest','import QtTest\nimport "witnesses.js" as Native',1).replace('    id: root','    id: root\n    property var nativeAdminShellWitnesses: Native.data',1)
text=text.replace('            const after = grabImage(host)','            const after = grabImage(host)\n            before.save("/evidence/'+name+'-before.png"); after.save("/evidence/'+name+'-after.png")',1);payload[f]=text.encode()
assert all(n.startswith('tests/') for n in payload)
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w') as archive:
 for n,b in payload.items():
  info=tarfile.TarInfo(n);info.size=len(b);archive.addfile(info,io.BytesIO(b))
(P/(name+'-payload.tar')).write_bytes(buf.getvalue())
script='test ! -e /work/src; test ! -e /work/CMakeLists.txt; mkdir /tmp/installed-admin; tar -xf - -C /tmp/installed-admin; test ! -e /tmp/installed-admin/src; sha256sum /avelino/lib/qml/Avelino/libAvelino.so; exec /opt/qt/bin/qmltestrunner -import /avelino/lib/qml -input /tmp/installed-admin/tests/components -o -,txt'
command=['docker','--context','colima-avelino-verify','run','--init','--rm','-i','--ulimit','core=0','-v',str(PACKAGE/'install')+':/avelino:ro','-v',str(OUT)+':/evidence','-e','QT_QPA_PLATFORM=offscreen','-e','QT_QUICK_BACKEND=software','-e','QT_SCALE_FACTOR='+scale,'-e','LD_LIBRARY_PATH=/avelino/lib/qml/Avelino:/opt/qt/lib',inputs['imageId'],'bash','-euc',script]
module=PACKAGE/'install/lib/qml/Avelino/libAvelino.so';before=sha(module);start=time.monotonic()
r=subprocess.run(command,input=buf.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(P/(name+'.log')).write_bytes(r.stdout);assert before==sha(module)
receipt={'command':command,'exitCode':r.returncode,'seconds':time.monotonic()-start,'sourceRevision':result['sourceRevision'],'sourceInputHashes':{n:hashlib.sha256(b).hexdigest() for n,b in original.items()},'executedPayloadHashes':{n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},'librarySha256':before,'libraryQmldirSha256':sha(PACKAGE/'install/lib/qml/Avelino/qmldir'),'sourceProjectsMounted':False,'productBuildMounted':False,'librarySourceOverlayProvided':False,'libraryQmldirModified':False,'testFixtureSourcesSuppliedViaStdin':True,'nativeRasterAccepted':False,'accepted':False}
(P/(name+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(name,r.returncode,flush=True)
print('\n'.join(line for line in r.stdout.decode(errors='replace').splitlines() if not line.startswith('PASS   :')))
raise SystemExit(r.returncode)
