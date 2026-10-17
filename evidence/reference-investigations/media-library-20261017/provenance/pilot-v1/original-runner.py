from pathlib import Path
import copy,hashlib,json,resource,shutil,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');prior=Path('/Users/gaulatti/.codex/tmp/avelino-chart-geometry-source-replay-20261017-v1');P=Path('/Users/gaulatti/.codex/tmp/avelino-media-library-native-20261017-v1');assert not P.exists();P.mkdir();(P/'tool').mkdir()
resource.setrlimit(resource.RLIMIT_CORE,(0,0));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source={str(p.relative_to(prior/'source')):sha(p) for p in (prior/'source').rglob('*') if p.is_file()};assert len(source)==89
for n in ['MediaCommon.swift','MediaMain.swift']:shutil.copy2(Path('/Users/gaulatti/.codex/tmp/avelino-media-library-helper-20261017')/n,P/'tool'/n)
products=prior/'build/out/Products/Debug';shutil.copytree(products/'Sabella_Sabella.bundle',P/'tool/Sabella_Sabella.bundle')
items=[dict(id=str(i),title='Tile '+str(i+1),width=40+i*10,height=20+(i%3)*20,color=i%4) for i in range(7)]
base=dict(id='default',items=items,minimumTileWidth=160,width=460,height=None,slot='fill',rtl=False,disabled=False,parentFont=False,parentRed=False,scroll=False)
fixtures=[]
for width in [0,1,40,159,160,175,176,335,336,337,512,700]:fixtures.append(dict(copy.deepcopy(base),id='width-'+str(width),width=width))
for minimum in [0,1,10,80,240,800]:fixtures.append(dict(copy.deepcopy(base),id='minimum-'+str(minimum),minimumTileWidth=minimum))
for slot in ['fill','fixed','text','button']:
 for count in [0,1,2,3,8]:fixtures.append(dict(copy.deepcopy(base),id=slot+'-count-'+str(count),slot=slot,items=copy.deepcopy(items[:count]) if count<8 else copy.deepcopy(items)+[dict(items[0],id='7',title='Last tile')]))
fixtures.append(dict(copy.deepcopy(base),id='rtl',rtl=True));fixtures.append(dict(copy.deepcopy(base),id='constrained-height',height=40));fixtures.append(dict(copy.deepcopy(base),id='scroll',scroll=True,height=100))
(P/'fixtures.json').write_text(json.dumps(fixtures,indent=2,ensure_ascii=False)+'\n')
inputs=dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',prebuiltLibraryInputs=True,sourceLocation=str(prior/'source'),originalBuildLocation=str(prior),sourceFiles=source,moduleFiles={str(p.relative_to(products)):sha(p) for p in products.rglob('*') if p.is_file()},files={str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file()})
(P/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n');steps=[]
commands=[(['xcrun','swiftc','-parse-as-library','-swift-version','6','-target','arm64-apple-macosx26.0','-I',str(products),str(P/'tool/MediaCommon.swift'),str(P/'tool/MediaMain.swift'),str(products/'Sabella.o'),'-o',str(P/'tool/NativeMedia')],'build'),([str(P/'tool/NativeMedia'),str(P/'fixtures.json'),str(P/'output'),'--pilot','-AppleLocale','en_US'],'closed')]
for command,name in commands:
 start=time.monotonic()
 with (P/(name+'.log')).open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,log=name+'.log'));(P/'steps.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,r.returncode,flush=True)
 if r.returncode:print((P/(name+'.log')).read_text()[-6000:]);raise SystemExit(r.returncode)
assert all(sha(prior/'source'/n)==v for n,v in source.items())
(P/'result.json').write_text(json.dumps(dict(exitCode=0,sourceFilesUnchanged=89,prebuiltLibraryInputs=True,accepted=False),indent=2)+'\n')
