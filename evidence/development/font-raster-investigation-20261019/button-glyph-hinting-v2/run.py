from pathlib import Path
import hashlib,json,subprocess,time
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent;ROOT=P.parents[2];BASE=P.parent
PACKAGE=BASE/'button-group-runtime-v2/runtime/install'
NATIVE=ROOT/'evidence/reference-investigations/button-group-slots-20261019'
CONTROL=BASE/'button-group-compiled-v6/output/artifacts'
IMAGE='sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def difference(a,b):
 with Image.open(a) as x,Image.open(b) as y:
  x=x.convert('RGBA');y=y.convert('RGBA');assert x.size==y.size
  d=ImageChops.difference(x,y);mask=d.getchannel('R')
  for c in ['G','B','A']:mask=ImageChops.lighter(mask,d.getchannel(c))
  return dict(changedPixels=x.width*x.height-mask.histogram()[0],bounds=mask.getbbox(),maxChannelError=max(v[1] for v in d.getextrema()))
rows=[];commands=[]
try:
 output=P/'output';output.mkdir();frozen={str(f.relative_to(PACKAGE)):sha(f) for f in sorted(PACKAGE.rglob('*')) if f.is_file()}
 write('inputs.json',dict(sourceRevision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),imageId=IMAGE,packageFiles=frozen,probeSha256=sha(P/'probe.qml'),fontWeight=500,productSourceChanged=False,accepted=False))
 expected=json.loads((NATIVE/'captures.json').read_text())['captures']
 for dark in [False,True]:
  for scale in [1,1.5]:
   for dpr in [1,2]:
    context=('dark' if dark else 'light')+'-text'+str(scale)+'-dpr'+str(dpr)
    native_name='button-group-'+('dark' if dark else 'light')+'-text'+format(scale,'.1f')+'-offscreen-dpr'+format(dpr,'.1f')+'.png'
    source=NATIVE/'canonical'/native_name
    native=next(r for r in expected if r['variant']=='mixed-buttons' and r['appearance']==('dark' if dark else 'light') and r['textScale']==scale and r['dpr']==dpr)
    for hint,label in [(0,'default'),(1,'none'),(2,'vertical'),(3,'full')]:
     name=context+'-'+label;capture=output/(name+'.png')
     command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(P)+':/probe:ro','-v',str(output)+':/output','-v',str(PACKAGE)+':/package/install:ro','-e','QML_IMPORT_PATH=/package/install/lib/qml','-e','QT_QPA_PLATFORM=offscreen','-e','QT_QUICK_BACKEND=software','-e','QT_SCALE_FACTOR='+str(dpr),IMAGE,'qml','/probe/probe.qml','--','--hint',str(hint),'--scale',str(scale),'--output','/output/'+capture.name]
     if dark:command.append('--dark')
     start=time.monotonic();r=subprocess.run(command,capture_output=True,text=True);(P/(name+'.log')).write_text(r.stdout+r.stderr);commands.append(dict(name=name,command=command,exitCode=r.returncode,seconds=time.monotonic()-start));write('commands.json',commands)
     assert r.returncode==0,(name,r.stdout,r.stderr)
     records=[json.loads(line.split('GLYPH_HINT ',1)[1]) for line in (r.stdout+r.stderr).splitlines() if 'GLYPH_HINT ' in line];assert len(records)==1
     record=records[0];geometry={key:record[key]==native['frames'][key] for key in ['component','first','second']}
     baseline_identical=capture.read_bytes()==(CONTROL/(context+'.png')).read_bytes()
     rows.append(dict(context=context,hint=hint,hintName=label,capture=capture.name,sha256=sha(capture),source=native_name,sourceSha256=sha(source),record=record,geometry=geometry,geometryPassed=all(geometry.values()),compiledBaselineByteIdentical=baseline_identical,**difference(source,capture),accepted=False))
     write('comparison.json',dict(rows=rows,rawPixels=True,pixelTolerance=0,accepted=False))
     if hint==0:assert baseline_identical,(name,'Interpreted probe differs from compiled product baseline')
    print(context,'complete',flush=True)
 assert all(sha(PACKAGE/n)==h for n,h in frozen.items())
 summary={label:dict(profiles=sum(r['hintName']==label for r in rows),changedPixels=sum(r['changedPixels'] for r in rows if r['hintName']==label),exact=sum(r['changedPixels']==0 for r in rows if r['hintName']==label),geometry=sum(r['geometryPassed'] for r in rows if r['hintName']==label)) for label in ['default','none','vertical','full']}
 write('result.json',dict(exitCode=0,profiles=len(rows),summary=summary,compiledBaselineControls=8,installedPackageUnchanged=True,productSourceChanged=False,accepted=False,fullMirrorAccepted=False))
 print(json.dumps(summary),flush=True)
except BaseException as e:
 write('result.json',dict(exitCode=1,error=repr(e),productSourceChanged=False,accepted=False));raise
