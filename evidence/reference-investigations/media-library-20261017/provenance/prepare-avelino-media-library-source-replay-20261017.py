from pathlib import Path
import hashlib,json,shutil
P=Path('/Users/gaulatti/.codex/tmp/avelino-media-library-source-replay-20261017-v1');assert not P.exists();P.mkdir();(P/'tool').mkdir()
prior=Path('/Users/gaulatti/.codex/tmp/avelino-media-library-native-20261017-v4');source=Path('/Users/gaulatti/.codex/tmp/avelino-chart-geometry-source-replay-20261017-v1/reference-source.tar')
shutil.copy2(source,P/'reference-source.tar')
for n in ['MediaCommon.swift','MediaMain.swift','MediaSizing.swift','MediaHistory.swift']:shutil.copy2(prior/'tool'/n,P/'tool'/n)
for n in ['fixtures.json','histories.json','edge-cases.json']:shutil.copy2(prior/n,P/n)
runner='''from pathlib import Path
import hashlib,itertools,json,resource,shutil,subprocess,tarfile,time
root=Path(__file__).resolve().parent;resource.setrlimit(resource.RLIMIT_CORE,(0,0));inputs=json.loads((root/'inputs.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(root/n)==v for n,v in inputs['files'].items())
assert not any((root/n).exists() for n in ['source','build','output']);(root/'source').mkdir();rows=[]
with tarfile.open(root/'reference-source.tar') as stream:
 members=[m for m in stream.getmembers() if m.isfile()];assert len(members)==89;stream.extractall(root/'source',filter='data')
def run(command,name):
 start=time.monotonic()
 with (root/(name+'.log')).open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 rows.append(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,log=name+'.log'));(root/'commands.json').write_text(json.dumps(rows,indent=2)+'\\n');print(name,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
run(['swift','build','--package-path',str(root/'source'),'--scratch-path',str(root/'build'),'--jobs','2','--target','Sabella','--disable-automatic-resolution','-Xswiftc','-target','-Xswiftc','arm64-apple-macosx26.0'],'library-build')
products=root/'build/out/Products/Debug';shutil.copytree(products/'Sabella_Sabella.bundle',root/'tool/Sabella_Sabella.bundle')
run(['xcrun','swiftc','-parse-as-library','-swift-version','6','-target','arm64-apple-macosx26.0','-I',str(products),*[str(root/'tool'/n) for n in ['MediaCommon.swift','MediaMain.swift','MediaSizing.swift','MediaHistory.swift']],str(products/'Sabella.o'),'-o',str(root/'tool/NativeMedia')],'helper-build')
for config,output,arguments in [('fixtures.json','output',[]),('fixtures.json','sizing-output',['--sizing']),('histories.json','history-output',['--histories'])]:run([str(root/'tool/NativeMedia'),str(root/config),str(root/output),*arguments,'-AppleLocale','en_US'],output)
edge_results=[]
for f in json.loads((root/'edge-cases.json').read_text()):
 config=root/('edge-'+f['id']+'.json');config.write_text(json.dumps([f],ensure_ascii=False)+'\\n')
 for appearance,scale,dpr in itertools.product(['light','dark'],[1,1.5],[1,2]):
  name=f['id']+'/'+appearance+'-text'+str(scale)+'-dpr'+str(dpr);output=root/'edges'/name;output.parent.mkdir(parents=True,exist_ok=True)
  command=[str(root/'tool/NativeMedia'),str(config),str(output),'--pilot','--appearance='+appearance,'--text-scale='+str(scale),'--dpr='+str(dpr),'-AppleLocale','en_US'];start=time.monotonic()
  with Path(str(output)+'.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  edge_results.append(dict(fixture=f['id'],appearance=appearance,textScale=scale,dpr=dpr,command=command,exitCode=r.returncode,seconds=time.monotonic()-start,output=str(output.relative_to(root)),log=str(Path(str(output)+'.log').relative_to(root))));(root/'edge-results.json').write_text(json.dumps(edge_results,indent=2)+'\\n')
 print('Edge',f['id'],'exits',[r['exitCode'] for r in edge_results[-8:]],flush=True)
with tarfile.open(root/'reference-source.tar') as stream:
 for m in stream.getmembers():
  if m.isfile():assert stream.extractfile(m).read()==(root/'source'/m.name).read_bytes(),m.name
(root/'result.json').write_text(json.dumps(dict(exitCode=0,sourceFilesUnchanged=89,prebuiltLibraryInputs=False,accepted=False),indent=2)+'\\n')
'''
(P/'replay.py').write_text(runner)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(P/'inputs.json').write_text(json.dumps(dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',prebuiltLibraryInputs=False,files={str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Prepared source-only replay',P)
