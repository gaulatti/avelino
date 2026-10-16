#!/usr/bin/env python3
"""Verify pinned native data-display evidence without approving Linux parity."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/data-metrics-20261015'
LOCALES={'en_US','de_DE','es_CL','fr_FR','ja_JP','ar_EG','hi_IN'}
FORMATS={'number','currency','percent','compact'}
CURRENCIES={'USD','JPY','CLP','KWD','EUR','XXX','INVALID'}
METRIC_VARIANTS={'normal','intrinsic','narrow','very-narrow','empty','long','multiline','rtl','disabled','parent-font30','environment-de'}
STAT_VARIANTS={'normal','intrinsic','narrow','very-narrow','empty','long','rtl','disabled','parent-font30','environment-de'}
KBD_VARIANTS={'normal','empty','space','long','multiline','unicode','intrinsic','narrow','very-narrow','rtl','disabled','parent-font30'}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify(directory=DIRECTORY):
    directory=Path(directory);report=json.loads((directory/'investigation.json').read_text())
    reference=json.loads((ROOT/'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['reference']==reference['revision'] and report['accepted'] is False and report['existingExpectedImagesChanged'] is False
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual==set(report['files'])|{'investigation.json'},'Missing or extra native data-display evidence'
    for name,h in report['files'].items():
        p=Path(name);assert not p.is_absolute() and '..' not in p.parts
        assert digest(directory/name)==h,name
    data=json.loads((directory/'captures.json').read_text());cases=data['captures'];assert data['reference']==reference['revision'] and data['processLocale']=='en_US'
    fixtures={'button-anchor'}|{'icon-badge-'+size+'-'+variant+'-'+symbol for size,variant,symbol in itertools.product(['md','lg'],['primary','subtle','outlined'],['house','arrow.left.arrow.right','minus'])}|{'icon-badge-'+v for v in ['intrinsic','narrow','rtl','disabled','parent-font30']}|{'metric-'+f+'-'+v for f,v in itertools.product(FORMATS,METRIC_VARIANTS)}|{'metric-value-'+v for v in ['negative','small','jpy','clp','kwd','eur','percent','compact']}|{'stat-card-'+d+'-'+v for d,v in itertools.product(['none','zero','positive','negative'],STAT_VARIANTS)}|{'stat-card-format-'+f for f in ['currency','percent','compact']}|{'kbd-'+v for v in KBD_VARIANTS}
    assert len(cases)==1048 and len(fixtures)==131
    assert {(c['fixture'],c['appearance'],c['textScale'],c['dpr']) for c in cases}=={(f,*axes) for f in fixtures for axes in itertools.product(['light','dark'],[1,1.5],[1,2])},'Incomplete native data-display matrix'
    for c in cases:
        assert c['source']==reference['revision'] and c['status']=='source investigation only; no baseline or parity approval'
        assert c['captureMethod']=='SwiftUI.ImageRenderer/CoreGraphics' and c['environmentDisplayScale']==c['dpr']
        for key in ['path','instrumentedPath','layoutWitnessPath']:
            assert Path(c[key]).name==c[key] and c[key].endswith('.png')
        raw=(directory/c['path']).read_bytes()
        assert c['instrumentedPngByteIdentical'] is True and raw==(directory/c['instrumentedPath']).read_bytes(),'Root instrumentation identity failed'
        assert c['layoutWitnessPngByteIdentical'] is True and raw==(directory/c['layoutWitnessPath']).read_bytes(),'Layout witness identity failed'
        frame=(240,96) if c['api']=='BleeckerButton' else (720,1000)
        assert (c['width'],c['height'])==frame
        assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==tuple(n*c['dpr'] for n in frame)
        for rect in [c['componentRect'],*c['layoutWitnessRects'].values()]:
            assert set(rect)=={'x','y','width','height'} and all(math.isfinite(n) for n in rect.values())
            assert rect['width']>=0 and rect['height']>=0
        assert c['componentSize']=={k:c['componentRect'][k] for k in ['width','height']}
        assert c['processLocale']=='en_US' and c['environmentLocale']==('de_DE' if c['variant']=='environment-de' else 'en_US')
        r=c['layoutWitnessRects'];fonts=c['layoutWitnessFonts']
        if c['api']=='BleeckerIconBadge':
            edge=36 if c['size']=='md' else 48
            assert c['componentSize']=={'width':edge,'height':edge},'Source badge fixed extent changed'
            assert set(r)=={'icon'} and set(fonts)=={'icon'}
        elif c['api'] in {'BleeckerMetric','BleeckerStatCard'}:
            assert fonts['label']=={'pointSize':10,'postScriptName':'EncodeSans-Bold'}
            assert fonts['value']=={'pointSize':24,'postScriptName':'EncodeSans-SmBold'}
            assert r['value']['y']-r['label']['y']-r['label']['height']==4,'Source metric label/value gap changed'
            assert r['metric']['height']==r['label']['height']+4+r['value']['height']
            if c['api']=='BleeckerStatCard':
                assert (r['badge']['width'],r['badge']['height'])==(36,36)
                assert r['spacer']['width']>=8
                assert c['componentSize']['width']==r['row']['width']+48 and c['componentSize']['height']==r['row']['height']+48,'Source card padding changed'
                if c['delta'] is None:assert 'delta' not in r and c['formattedDelta'] is None
                else:
                    assert fonts['delta']=={'pointSize':11,'postScriptName':'EncodeSans-SmBold'}
                    assert r['delta']['y']-r['badge']['y']-r['badge']['height']==8
                    assert c['formattedDelta'].startswith('+' if c['delta']>=0 else '-'),'Source signed delta changed'
            else:assert set(r)=={'metric','label','value'}
        elif c['api']=='BleeckerKbd':
            assert fonts['key']=={'pointSize':10,'postScriptName':'.AppleSystemUIFontMonospaced-Medium'},'Native mono face changed'
            assert c['componentSize']=={'width':r['key']['width']+12,'height':max(22,r['key']['height'])},'Source key-label padding changed'
    def check_formats(j,locale):
        rows=j['formatting'];assert j['processLocale']==locale and len(rows)==190
        values={r['value'] for r in rows};assert len(values)==19 and {'nan','infinity','-infinity','-0.0'}<=values
        assert {(r['value'],r['format'],r['currencyCode']) for r in rows}=={(v,f,code) for v in values for f in FORMATS for code in (CURRENCIES if f=='currency' else {'USD'})}
        assert all(r['processLocale']==locale and isinstance(r['text'],str) and r['text'] for r in rows)
    check_formats(data,'en_US')
    for locale in LOCALES:
        j=json.loads((directory/('locale-'+locale)/'captures.json').read_text());assert j['captures']==[];check_formats(j,locale)
    english={(r['value'],r['format'],r['currencyCode']):r['text'] for r in data['formatting']}
    for code,text in {'USD':'$1,234.57','JPY':'¥1,235','CLP':'CLP\u00a01,235','KWD':'KWD\u00a01,234.568'}.items():assert english[('1234.56789','currency',code)]==text,'Source currency precision changed'
    bykey={(c['fixture'],c['appearance'],c['textScale'],c['dpr']):c for c in cases}
    for format in FORMATS:
        a=bykey[('metric-'+format+'-normal','light',1,2)];b=bykey[('metric-'+format+'-environment-de','light',1,2)]
        assert a['formattedValue']==b['formattedValue'] and a['componentSize']==b['componentSize'],'Metric unexpectedly follows environment locale'
    a=bykey[('stat-card-positive-normal','light',1,2)];b=bykey[('stat-card-positive-environment-de','light',1,2)]
    assert a['formattedValue']==b['formattedValue'] and a['formattedDelta']=='+12.345679%' and b['formattedDelta']=='+12,345679\u00a0%','Stat-card delta environment locale changed'
    fixed_scale_pairs=0
    for c in cases:
        if c['api']=='BleeckerButton' or c['textScale']!=1:continue
        other=bykey[(c['fixture'],c['appearance'],1.5,c['dpr'])]
        assert (directory/c['path']).read_bytes()==(directory/other['path']).read_bytes(),'Source fixed styles changed with text scale'
        fixed_scale_pairs+=1
    locale_image_pairs=0
    for appearance,scale,dpr in itertools.product(['light','dark'],[1,1.5],[1,2]):
        for format in FORMATS:
            a=bykey[('metric-'+format+'-normal',appearance,scale,dpr)];b=bykey[('metric-'+format+'-environment-de',appearance,scale,dpr)]
            assert (directory/a['path']).read_bytes()==(directory/b['path']).read_bytes(),'Public metric image unexpectedly follows environment locale'
            locale_image_pairs+=1
        for delta in ['none','zero','positive','negative']:
            a=bykey[('stat-card-'+delta+'-normal',appearance,scale,dpr)];b=bykey[('stat-card-'+delta+'-environment-de',appearance,scale,dpr)]
            equal=(directory/a['path']).read_bytes()==(directory/b['path']).read_bytes()
            assert equal is (delta=='none'),'Public stat-card delta locale image changed'
            locale_image_pairs+=1
    provenance=json.loads((directory/'tooling-provenance.json').read_text())
    assert provenance['referenceRevision']==reference['revision'] and provenance['referenceArchiveSha256']==reference['sha256']
    assert provenance['toolArtifact']['sha256']==report['sourceToolArtifact'] and len(provenance['toolArtifact']['files'])==36
    replay=json.loads((directory/'clean-replay.json').read_text())
    assert replay['inputHashesVerified']==36 and replay['filesCompared']==replay['byteIdenticalFiles']==3160 and replay['changedFiles']==[],'Native data-display replay failed'
    assert len(replay['results'])==3160
    for r in replay['results']:
        p=Path(r['path']);assert not p.is_absolute() and '..' not in p.parts
        assert r['byteIdentical'] is True and r['sha256']==r['replaySha256']==digest(directory/r['path']),'Clean replay output mismatch'
    return {'captures':1048,'publicInstrumentationIdentity':1048,'layoutWitnessIdentity':1048,'localeFormatterWitnesses':1330,'processLocales':7,'fixedTextScaleImagePairs':fixed_scale_pairs,'localeOwnershipImagePairs':locale_image_pairs,'byteIdenticalReplayFiles':3160,'accepted':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
