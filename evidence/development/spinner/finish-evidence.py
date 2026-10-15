import hashlib,json,shutil
from pathlib import Path

root=Path('evidence/development/spinner')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
summary=json.load(open(root/'verification-summary.json'))
regressions=json.load(open(root/'regressions.json'));comparisons=json.load(open(root/'comparison/change-audit.json'))
assert summary['sourceComparisons']==44
assert comparisons['geometryPassesLost']==comparisons['exactPassesLost']==0
for name in ['preserve.py','finish-evidence.py','stage-audit.py']:shutil.copy2(Path('artifacts/spinner')/name,root/name)
value={'schemaVersion':1,'status':'shared spinner runtime and native-model candidate verified; complete mirror acceptance pending','previousCandidate':regressions['previousCandidate'],'referenceRevision':'fe8a1d462fbd793d883fb92086a16aa2947e32c9','nativeInvestigation':'evidence/reference-investigations/spinner-20261015/investigation.json',**summary,'sourcePixelChangeCounts':{'fewerChangedPixels':sum(r['afterChangedPixels']<r['beforeChangedPixels'] for r in comparisons['results']),'sameChangedPixels':sum(r['afterChangedPixels']==r['beforeChangedPixels'] for r in comparisons['results']),'moreChangedPixels':sum(r['afterChangedPixels']>r['beforeChangedPixels'] for r in comparisons['results'])},'geometryPassesLost':0,'exactPassesLost':0,'approvedExceptions':[],'limitations':['No complete API mirror acceptance; 46/80 desktop entries started, TV unchanged.','Native model-frame and opacity witnesses do not establish exact raster, physical cadence or synchronized phase.','Actual native DPR 1, color-pipeline reconciliation, physical display/input and actual screen readers remain pending.','Native reduced-motion, keyboard and broader generic composition correspondence remain pending.','Helpers link preserved source-verified objects; fresh full Sabella compilation and public helper distribution remain pending.','Virtual software/Mesa and synthetic input are implementation evidence, separate from hardware and physical input.','Capture/build input provenance records preceding main plus exact dirty source hashes.','No source pin, expected image, tolerance, approved exception, sibling checkout or TV implementation changed.']}
value['files']={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='candidate.json'}
(root/'candidate.json').write_text(json.dumps(value,indent=2)+'\n')
print('Sealed',len(value['files']),'files;',json.dumps({k:v for k,v in value.items() if k not in ['files','limitations']}))
