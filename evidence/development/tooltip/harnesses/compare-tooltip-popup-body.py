"""One measured native help body versus the installed Qt DPR2 default body."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[2]
reference=root/'evidence/reference-investigations/tooltip-20261016/native-v2/auto-aux-window49094-content.png'
candidate=root/'artifacts/tooltip-package-20261016-v7/tooltip-native-body-v1/tooltip-xcb-software-standard-native-default-tooltip.png'
metadata=candidate.with_name('tooltip-xcb-software-standard.json')
output=root/'artifacts/tooltip-popup-comparison-20261016-v1';output.mkdir()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads(metadata.read_text());assert record['dpr']==2 and record['textScale']==1 and record['appearance']=='light' and record['separateTooltipWindow'] and record['shownHintPixelsIdentical']
investigation=json.loads((root/'evidence/reference-investigations/tooltip-20261016/investigation.json').read_text());assert digest(reference)==investigation['files']['native-v2/auto-aux-window49094-content.png']
a,b=Image.open(reference),Image.open(candidate)
report=dict(accepted=False,status='failed',reference=str(reference.relative_to(root)),candidate=str(candidate.relative_to(root)),referenceSha256=digest(reference),candidateSha256=digest(candidate),metadataSha256=digest(metadata),referencePhysicalSize=list(a.size),candidatePhysicalSize=list(b.size),dpr=2,textScale=1,appearance='light',pixelTolerance=0,resized=False,referenceColorMetadata={k:str(v) for k,v in a.info.items() if k in ['srgb','gamma','chromaticity']},candidateColorMetadata={k:str(v) for k,v in b.info.items() if k in ['srgb','gamma','chromaticity']},scope='Single original help body observation; compositor shadow/vibrancy, timing, full popup coverage, native system font and readers remain pending')
if a.size!=b.size:report['error']='Physical pixel dimensions differ; comparison refuses resizing'
elif 'icc_profile' in a.info or 'icc_profile' in b.info:report['error']='ICC-managed captures require explicitly reviewed conversion'
else:
 diff=ImageChops.difference(a.convert('RGB'),b.convert('RGB'));alpha=ImageChops.difference(a.getchannel('A'),b.getchannel('A'))
 report.update(rgbDifferenceBounds=diff.getbbox(),alphaDifferenceBounds=alpha.getbbox(),status='passed' if not diff.getbbox() and not alpha.getbbox() else 'failed');diff.save(output/'body-diff.png')
pair=Image.new('RGBA',(a.width+b.width+20,max(a.height,b.height)),(255,255,255,255));pair.paste(a,(0,0),a);pair.paste(b,(a.width+20,0),b);pair.save(output/'body-pair-original-size.png')
(output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','accepted','referencePhysicalSize','candidatePhysicalSize','error']},indent=2))
