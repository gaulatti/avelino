#!/usr/bin/env python3
"""Verify native getter evidence without granting font or rendering parity."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/date-range-font-20261018'


def verify():
    read=lambda name:json.loads((DIRECTORY/name).read_text())
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    files=read('files.json')
    assert set(files)=={str(p.relative_to(DIRECTORY))for p in DIRECTORY.rglob('*')if p.is_file()and p!=DIRECTORY/'files.json'}
    for name,row in files.items():
        path=DIRECTORY/name
        assert path.stat().st_size==row['bytes']and digest(path)==row['sha256'],name
    result=read('result.json');assert result['accepted']is False and result['fixtures']==48 and result['editors']==96
    assert result['allBeforeAfterAndOriginalImagesIdentical']is True
    rows=read('metrics.json')['rows'];assert len(rows)==48
    for row in rows:
        name=row['configuration']['id'];assert row['getterCaptureStable']and len(row['editors'])==2
        before=DIRECTORY/'output'/f'{name}.png';after=DIRECTORY/'output'/f'{name}-after.png'
        original=ROOT/'evidence/reference-investigations/date-range-20261018/output'/f'{name}-light-text1.0-dpr1.0-mode0.png'
        assert before.read_bytes()==after.read_bytes()==original.read_bytes()
        for editor in row['editors']:
            font=editor['font'];assert font['features']==[dict(type=6,selector=0)]
            assert font['widths'][' ']==font['widths']['0']
            assert all(font['widths'][str(digit)]==font['widths']['0']for digit in range(10))
            assert editor['shortDateFormat']and editor['shortDateString']
    for version in [2,3,4]:
        assert all(step['exitCode']==0 for step in read(f'attempts/v{version}/commands.json'))
    assert read('attempts/v1/commands.json')[-1]['exitCode']==1
    assert 'main actor-isolated' in (DIRECTORY/'attempts/v1/build.log').read_text()
    replay=read('source-only-replay/result.json')
    assert replay==dict(accepted=False,exitCode=0,extractedWithoutPrebuiltProducts=True,exactReplayFiles=97,allOutputBytesEqual=True,independentMachine=False)
    archive=read('source-only-replay/artifact.json')
    assert archive['files']==93 and archive['pinnedSourceFiles']==89 and archive['compiledOutputs']is False
    assert len(archive['sourceFiles'])==93 and all(step['exitCode']==0 for step in read('source-only-replay/commands.json'))
    replayFiles=read('source-only-replay/output-checks.json');assert len(replayFiles)==97
    assert set(replayFiles)=={str(p.relative_to(DIRECTORY/'output'))for p in (DIRECTORY/'output').rglob('*')if p.is_file()}
    for name,row in replayFiles.items():
        path=DIRECTORY/'output'/name
        assert row['bytes']==path.stat().st_size and row['originalSha256']==row['replaySha256']==digest(path)
    visible=read('visible-pattern-observations.json');assert visible['accepted']is False and len(visible['overrides'])==1
    override=visible['overrides'][0]
    assert (override['locale'],override['calendar'],override['shortDateFormat'],override['visiblePattern'])==('ja_JP','gregorian','y/MM/dd','y/M/d')
    assert len(override['images'])==2
    for row in override['images']:assert digest(ROOT/row['path'])==row['sha256']
    print('Native date fonts: 48 unchanged before/after/original captures; 96 explicit monospaced-digit fonts; 97 exact source-only replay outputs; visible Japanese calendar distinction retained; Linux font/raster acceptance pending')


if __name__=='__main__':verify()
