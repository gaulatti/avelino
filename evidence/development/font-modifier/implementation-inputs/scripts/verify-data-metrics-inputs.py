#!/usr/bin/env python3
"""Verify the separately replayed proposal inputs for the sealed native images."""
import hashlib,itertools,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/data-metrics-inputs-20261015'
def verify():
    p=DIRECTORY/'fixture-inputs.json';j=json.loads(p.read_text());v=json.loads((DIRECTORY/'provenance.json').read_text());ref=json.loads((ROOT/'reference/source-manifest.json').read_text())['references']['desktop']
    assert j['reference']==v['reference']==ref['revision'] and v['sourceArchiveSha256']==ref['sha256']
    assert v['accepted'] is False and v['existingExpectedImagesChanged'] is False and v['inputHashesVerified']==35 and len(v['toolArtifact']['files'])==35
    assert v['cleanReplayByteIdentical'] is True and v['fixtureInputsSha256']==v['replayFixtureInputsSha256']==hashlib.sha256(p.read_bytes()).hexdigest()
    parent=json.loads((ROOT/'evidence/reference-investigations/data-metrics-20261015/tooling-provenance.json').read_text())
    assert v['parentHelperSha256']==parent['toolArtifact']['files']['tool/Sources/NativeCapture/main.swift']
    original=json.loads((ROOT/'evidence/reference-investigations/data-metrics-20261015/captures.json').read_text())['captures'];rows={r['fixture']:r for r in j['fixtures']};assert len(rows)==len(j['fixtures'])==131
    assert set(rows)=={r['fixture'] for r in original}
    keys=['api','intrinsic','text','symbol','size','variant','format','currencyCode','value','delta','rtl','disabled','parentFont','environmentLocale']
    for c in original:assert all(rows[c['fixture']][k]==c[k] for k in keys)
    for r in rows.values():
        assert r['proposalWidth']==(-1 if r['intrinsic'] else 12 if r['fixture'] in ['icon-badge-narrow','kbd-very-narrow'] or r['api']=='BleeckerMetric' and r['variant']=='very-narrow' else 30 if r['fixture']=='kbd-narrow' else 60 if r['api']=='BleeckerStatCard' and r['variant']=='very-narrow' else 80 if r['api']=='BleeckerMetric' and r['variant']=='narrow' else 160 if r['api']=='BleeckerMetric' and r['variant']=='long' else 180 if r['api']=='BleeckerStatCard' and r['variant'] in ['narrow','long'] else 320),'Native layout proposal changed'
    numeric=json.loads((ROOT/'evidence/geometry/native-numeric-text.json').read_text());raw=ROOT/numeric['casesFile'];provenance=numeric['provenance']
    assert numeric['referenceRevision']==ref['revision'] and numeric['sourceArchiveSha256']==ref['sha256'] and numeric['accepted'] is False
    assert provenance['inputHashesVerified']==len(provenance['toolArtifact']['files'])==35 and provenance['cleanReplayByteIdentical'] is True
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==provenance['nativeOutputSha256']==provenance['replayOutputSha256']
    assert numeric['cases']==json.loads(raw.read_text()) and len(numeric['cases'])==40
    assert {(r['text'],r['dpr'],r['proposal'],r['numeric']) for r in numeric['cases']}==set(itertools.product(['12K','12,345.6789','$12,345.68','12,345.','6789'],[1,2],[80,240],[False,True]))
    for r in numeric['cases']:
        assert r['font']=='EncodeSans-SmBold' and r['rect']['height']==30*len(r['wrapped'])
        assert r['rect']['width']==max(math.ceil(line['advance']*r['dpr'])/r['dpr'] for line in r['wrapped']),'Native contextual line advance differs from view width'
    return {'numericTextCases':40,'numericReplayIdentical':True,'fixtures':131,'cleanInputHashes':35,'byteIdenticalReplay':True,'accepted':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
