import hashlib,json,shutil
from pathlib import Path
root=Path('evidence/development/alert');summary=json.load(open(root/'verification-summary.json'));audit=json.load(open(root/'regression-comparison.json'));regressions=json.load(open(root/'regressions.json'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
affected={'BleeckerAlert'}
for selection in audit['selections']:
    cases=json.load(open(selection['originalManifest']))['captures'];names=set(selection['paths'])
    for c in cases:
        if c['path'] in names:affected.add(c['api'] if 'api' in c else 'BleeckerButton')
p=Path('docs/parity-inventory.json');j=json.load(open(p));known={e['id']:e for e in j['desktop']['entries']};assert affected<=set(known)
for name in affected-{'BleeckerAlert'}:
    e=known[name]
    e['cases'].append({'id':'shared-two-line-prose','status':'pending','evidence':['evidence/development/alert/regression-comparison.json','docs/wrapping.md'],'notes':'Shared label wrapping changed only where the measured two-line prose rule applies. Exact visual, broader scripts/context and complete component acceptance remain pending.'})
    e['comparisonResults'].append('evidence/development/alert/regression-comparison.json')
p.write_text(json.dumps(j,indent=2)+'\n')
(root/'inventory-changes.json').write_text(json.dumps({'entries':sorted(affected),'coverage':'47/80 started; no complete mirror acceptance; TV/approved exceptions unchanged'},indent=2)+'\n')
for name in ['preserve.py','finish-evidence.py','stage-audit.py','seal-boundaries.py']:shutil.copy2(Path('artifacts/alert')/name,root/name)
value={'schemaVersion':1,'status':'alert, caller-content and measured prose-layout candidates verified; complete mirror acceptance pending','previousCandidate':regressions['previousCandidate'],'referenceRevision':'fe8a1d462fbd793d883fb92086a16aa2947e32c9','referenceProposal':'evidence/reference-proposals/alert-20261015/proposal.json',**summary,'sourcePixelChangeCounts':{'fewerChangedPixels':sum(r['afterChangedPixels']<r['beforeChangedPixels'] for r in audit['results']),'sameChangedPixels':sum(r['afterChangedPixels']==r['beforeChangedPixels'] for r in audit['results']),'moreChangedPixels':sum(r['afterChangedPixels']>r['beforeChangedPixels'] for r in audit['results'])},'geometryPassesLost':0,'exactPassesLost':0,'approvedExceptions':[],'limitations':['47/80 desktop APIs started; none completely accepted; TV unchanged.','Original glyph artwork and exact raster, arbitrary font/script/layout contexts and physical/reader acceptance remain pending.','Software arbitrary-child clipping remains rectangular; source circular overflow is an explicit unaccepted case.','The caller Component interface exposes finite proposals and font/color hints; broader generic compositions remain pending.','Source native pointer records use DPR 2 inactive windows; synthetic Qt/native actions do not establish physical input, keyboard equivalence or reader output.','Both source tools link preserved source-verified objects; full fresh compilation and public helper download remain pending.','One hosted primary18 TextRenderer witness changes pixels and is excluded from trusted line evidence; raw diagnostics are preserved.','The corrected run is independent of the preserved first pass, which exposed four loading-text pixel regressions.','Capture/build provenance records preceding main plus exact dirty source hashes.','No source pin, expected image, tolerance, accepted exception, sibling or TV change.']}
value['files']={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='candidate.json'}
(root/'candidate.json').write_text(json.dumps(value,indent=2)+'\n')
print('Sealed',len(value['files']),'files;',json.dumps({k:v for k,v in value.items() if k not in ['files','limitations']}))
