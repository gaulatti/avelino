from pathlib import Path
import copy,hashlib,itertools,json,resource,shutil,subprocess,sys,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');prior=Path('/Users/gaulatti/.codex/tmp/avelino-chart-geometry-source-replay-20261017-v1');P=Path('/Users/gaulatti/.codex/tmp')/(sys.argv[1] if len(sys.argv)>1 else 'avelino-media-library-native-20261017-v4');assert not P.exists();P.mkdir();(P/'tool').mkdir()
resource.setrlimit(resource.RLIMIT_CORE,(0,0));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source={str(p.relative_to(prior/'source')):sha(p) for p in (prior/'source').rglob('*') if p.is_file()};assert len(source)==89
tooling=['MediaCommon.swift','MediaMain.swift','MediaSizing.swift','MediaHistory.swift']
for n in tooling:shutil.copy2(Path('/Users/gaulatti/.codex/tmp/avelino-media-library-helper-20261017')/n,P/'tool'/n)
products=prior/'build/out/Products/Debug';shutil.copytree(products/'Sabella_Sabella.bundle',P/'tool/Sabella_Sabella.bundle')
items=[dict(id=str(i),title='Tile '+str(i+1),width=40+i*10,height=20+(i%3)*20,color=i%4) for i in range(7)]
base=dict(id='default',items=items,minimumTileWidth=160,width=460,height=None,slot='fill',rtl=False,disabled=False,parentFont=False,parentRed=False,scroll=False)
fixtures=[]
for width in [0,1,40,159,160,175,176,335,336,337,512,700]:fixtures.append(dict(copy.deepcopy(base),id='width-'+str(width),width=width))
for minimum in [0,1,10,80,240,800]:fixtures.append(dict(copy.deepcopy(base),id='minimum-'+str(minimum),minimumTileWidth=minimum))
for slot in ['fill','fixed','text','button']:
 for count in [0,1,2,3,8]:fixtures.append(dict(copy.deepcopy(base),id=slot+'-count-'+str(count),slot=slot,items=copy.deepcopy(items[:count]) if count<8 else copy.deepcopy(items)+[dict(items[0],id='7',title='Last tile')]))
fixtures.append(dict(copy.deepcopy(base),id='rtl',rtl=True));fixtures.append(dict(copy.deepcopy(base),id='constrained-height',height=40));fixtures.append(dict(copy.deepcopy(base),id='scroll',scroll=True,height=100))
for width in [335.5,335.999,336.001,511.5,511.999,512.001]:fixtures.append(dict(copy.deepcopy(base),id='fractional-'+str(width),width=width))
for width in [40,160,336]:fixtures.append(dict(copy.deepcopy(base),id='fixed-overflow-'+str(width),width=width,slot='fixed',items=[dict(items[0],width=220),dict(items[1],width=90),dict(items[2],width=400)]))
fixtures.append(dict(copy.deepcopy(base),id='zero-heights',items=[dict(p,height=0) for p in items]));fixtures.append(dict(copy.deepcopy(base),id='mixed-zero-heights',items=[dict(p,height=0 if i%2==0 else p['height']) for i,p in enumerate(items)]))
for slot in ['text','button']:
 fixtures.append(dict(copy.deepcopy(base),id=slot+'-long',slot=slot,items=[dict(p,title='A long tile title with enough words to wrap across narrow columns '+str(i)) for i,p in enumerate(items)]))
 fixtures.append(dict(copy.deepcopy(base),id=slot+'-font28',slot=slot,parentFont=True));fixtures.append(dict(copy.deepcopy(base),id=slot+'-red',slot=slot,parentRed=True));fixtures.append(dict(copy.deepcopy(base),id=slot+'-disabled',slot=slot,disabled=True))
fixtures.append(dict(copy.deepcopy(base),id='scroll-dense',scroll=True,height=100,items=[dict(items[i%7],id=str(i),title='Tile '+str(i+1)) for i in range(50)]))
fixtures.append(dict(copy.deepcopy(base),id='unicode',items=[dict(p,id=identity,title=identity) for p,identity in zip(items,['é','Å','Ω','👩🏽‍💻','ß','ss','1'])]))
(P/'fixtures.json').write_text(json.dumps(fixtures,indent=2,ensure_ascii=False)+'\n')
histories=[copy.deepcopy(next(f for f in fixtures if f['id']==n)) for n in ['width-337','fixed-count-8','text-long','button-count-8','scroll-dense','unicode']]
(P/'histories.json').write_text(json.dumps(histories,indent=2,ensure_ascii=False)+'\n');(P/'sizing-pilot.json').write_text(json.dumps([base],indent=2)+'\n')
edges=[]
for field,values in [('minimumTileWidth',[-100,-16,-1,'__native_nan__','__native_positive_infinity__','__native_negative_infinity__']),('width',[-1,'__native_nan__','__native_positive_infinity__','__native_negative_infinity__']),('height',[-1,'__native_nan__','__native_positive_infinity__','__native_negative_infinity__'])]:
 for i,value in enumerate(values):edges.append(dict(copy.deepcopy(base),**{field:value},id=field+'-edge-'+str(i)))
(P/'edge-cases.json').write_text(json.dumps(edges,indent=2,ensure_ascii=False)+'\n')
inputs=dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',prebuiltLibraryInputs=True,sourceLocation=str(prior/'source'),originalBuildLocation=str(prior),sourceFiles=source,moduleFiles={str(p.relative_to(products)):sha(p) for p in products.rglob('*') if p.is_file()},files={str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file()})
(P/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n');steps=[]
commands=[(['xcrun','swiftc','-parse-as-library','-swift-version','6','-target','arm64-apple-macosx26.0','-I',str(products),*[str(P/'tool'/n) for n in tooling],str(products/'Sabella.o'),'-o',str(P/'tool/NativeMedia')],'build'),([str(P/'tool/NativeMedia'),str(P/'fixtures.json'),str(P/'output'),'-AppleLocale','en_US'],'closed'),([str(P/'tool/NativeMedia'),str(P/'fixtures.json'),str(P/'sizing-output'),'--sizing','-AppleLocale','en_US'],'sizing'),([str(P/'tool/NativeMedia'),str(P/'histories.json'),str(P/'history-output'),'--histories','-AppleLocale','en_US'],'histories')]
for command,name in commands:
 start=time.monotonic()
 with (P/(name+'.log')).open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,log=name+'.log'));(P/'steps.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,r.returncode,flush=True)
 if r.returncode:
  (P/'result.json').write_text(json.dumps(dict(exitCode=r.returncode,stage=name,prebuiltLibraryInputs=True,accepted=False),indent=2)+'\n');print((P/(name+'.log')).read_text()[-6000:]);raise SystemExit(r.returncode)
assert all(sha(prior/'source'/n)==v for n,v in source.items())
(P/'original-runner.py').write_bytes(Path(__file__).read_bytes())
edge_results=[]
for f in edges:
 config=P/('edge-'+f['id']+'.json');config.write_text(json.dumps([f],ensure_ascii=False)+'\n')
 for appearance,scale,dpr in itertools.product(['light','dark'],[1,1.5],[1,2]):
  name=f['id']+'/'+appearance+'-text'+str(scale)+'-dpr'+str(dpr);output=P/'edges'/name;output.parent.mkdir(parents=True,exist_ok=True)
  command=[str(P/'tool/NativeMedia'),str(config),str(output),'--pilot','--appearance='+appearance,'--text-scale='+str(scale),'--dpr='+str(dpr),'-AppleLocale','en_US'];start=time.monotonic()
  with Path(str(output)+'.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  edge_results.append(dict(fixture=f['id'],appearance=appearance,textScale=scale,dpr=dpr,command=command,exitCode=r.returncode,seconds=time.monotonic()-start,output=str(output.relative_to(P)),log=str(Path(str(output)+'.log').relative_to(P))));(P/'edge-results.json').write_text(json.dumps(edge_results,indent=2)+'\n')
 print('Edge',f['id'],'exits',[row['exitCode'] for row in edge_results[-8:]],flush=True)
(P/'result.json').write_text(json.dumps(dict(exitCode=0,sourceFilesUnchanged=89,prebuiltLibraryInputs=True,accepted=False),indent=2)+'\n')
