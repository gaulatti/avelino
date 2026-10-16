import argparse,hashlib,json,platform,random,time
from PIL import __version__ as pillow_version
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser(description="Compare exact legacy/histogram RGB metrics on synthetic and preserved native captures")
parser.add_argument("--output",type=Path,default=ROOT/"artifacts/pixel-counting/benchmark.json")
args=parser.parse_args()

def previous(delta):
    pixels=list(delta.get_flattened_data())
    return (sum(any(c!=0 for c in p) for p in pixels),max(max(p) for p in pixels))

def histogram(delta):
    red,green,blue=delta.split()
    maximum=ImageChops.lighter(ImageChops.lighter(red,green),blue)
    return (delta.width*delta.height-maximum.histogram()[0],maximum.getextrema()[1])

randomizer=random.Random(0xA7E110)
checks=0
for size in [(1,1),(2,3),(17,31),(128,64)]:
    for mode in ['zero','one-channel','random','sparse']:
        pixels=[]
        for i in range(size[0]*size[1]):
            if mode=='zero':p=(0,0,0)
            elif mode=='one-channel':p=tuple(randomizer.randrange(256) if c==i%3 else 0 for c in range(3))
            elif mode=='sparse':p=tuple(randomizer.randrange(256) if randomizer.random()<0.03 else 0 for _ in range(3))
            else:p=tuple(randomizer.randrange(256) for _ in range(3))
            pixels.append(p)
        image=Image.new('RGB',size);image.putdata(pixels)
        assert previous(image)==histogram(image),(size,mode)
        checks+=1
rows=[];seen=set()
reference=ROOT/'evidence/reference-proposals/data-metrics-20261015'
candidate=ROOT/'evidence/development/data-metrics/captures'
for case in json.loads((reference/'captures.json').read_text())['captures']:
    key=(case['api'],case['dpr'])
    if key in seen:continue
    seen.add(key)
    expected=reference/case['path'];actual=candidate/case['path']
    with Image.open(expected) as a,Image.open(actual) as b:
        delta=ImageChops.difference(a.convert('RGB'),b.convert('RGB'))
    start=time.perf_counter();before=previous(delta);oldSeconds=time.perf_counter()-start
    start=time.perf_counter();after=histogram(delta);newSeconds=time.perf_counter()-start
    assert before==after,case['path']
    rows.append({'fixture':case['path'],'referenceSha256':hashlib.sha256(expected.read_bytes()).hexdigest(),
        'candidateSha256':hashlib.sha256(actual.read_bytes()).hexdigest(),
        'changedPixels':after[0],'maximumChannelError':after[1],
        'previousSeconds':oldSeconds,'histogramSeconds':newSeconds,'equal':True})
report={'pillow':pillow_version,'platform':platform.platform(),'status':'exact diagnostic metric equivalence; no product or acceptance-policy change',
        'syntheticChecks':checks,'realCaptureChecks':len(rows),
        'previousSeconds':sum(r['previousSeconds'] for r in rows),
        'histogramSeconds':sum(r['histogramSeconds'] for r in rows),'results':rows}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items() if k!='results'})
