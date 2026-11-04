#!/usr/bin/env python3
"""Audit native history/edit observations without granting parity acceptance."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/file-input-search-history-20261021'


def verify():
    read=lambda name:json.loads((DIRECTORY/name).read_text())
    files=read('files.json')
    assert set(files)=={str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name!='files.json'}
    for name,row in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        raw=(DIRECTORY/name).read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
    report=read('observations.json');build=read('swiftui/build.json');trace=read('swiftui/output/ui-trace.json')
    assert report['reference']==build['reference']==trace['reference']=='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['cachedLibraryObjectSha256']==build['libraryObjectSha256']=='61d1e55c6f9c17c841eded420066c72b5611ec51af8c5a4821306f1751ea6514'
    assert build['exitCode']==0 and build['libraryUnchanged'] is True
    assert build['sourceLibraryChanged'] is build['independentNativeLibraryRebuild'] is build['injectedCompletion'] is build['accepted'] is False
    for key in ['independentNativeLibraryRebuild','completeNativeAxAttributesArchived','completeScreenshotBytesArchived','nativeReaderAccepted','physicalInputAccepted','nativeRasterAccepted','expectedImagesChanged','referenceChanged','tolerancesChanged','accepted']:
        assert report[key] is False,key
    assert report['noOwnerResultRecorded'] is True and trace['steps'][-1]['results']==[]
    termination=read('termination.json');assert termination['psExitCode']==1 and termination['processPresent'] is False
    assert termination['lastRecordedOwnerResults']==[] and termination['pid']==trace['pid']
    index=read('controlled-cua/index.json');assert index['appleActionCodeArchived'] is index['accepted'] is False
    assert len(index['interactions'])==18
    interactions=[read('controlled-cua/'+name) for name in index['interactions']]
    for interaction in interactions:
        assert interaction['status']=='completed' and interaction['completeImageBytesArchived'] is False
        assert 'actionArguments' not in interaction
        for image in interaction['imageMetadata']:assert image['mimeType']=='image/jpeg' and image['completeImageBytesArchived'] is False
    before=interactions[3]['text'];back=interactions[5]['text'];forward=interactions[6]['text'];display=interactions[7]['text']
    assert 'Filename: avelinoulnacerulean' in before and before.count('URL: file:')==report['forward']['matchingBeforeBack']==1
    assert 'row (selected)' in interactions[4]['text']
    assert 'search text field Search' in back and re.search(r'\d+ button forward\n',back)
    assert 'row (selected)' not in back and 'Value: avelino-file-search-fixtures, ID: where popup' in back
    for text in [forward,display]:
        assert 'Filename: avelinoulnacerulean' in text and 'Help: Search in “avelino-file-search-fixtures”, Value: 1' in text
        assert text.count('URL: file:')==report['forward']['unexpectedRecursiveFileRows']==8
        assert '/unrelated-control-20261020.txt' in text and '/leaf.txt' in text
        assert 'row (selected)' not in text and 'Loading' not in text and 'busy indicator' not in text
    assert report['forward']['membershipEquivalenceVerified'] is False
    new=interactions[9]['text'];assert 'Filename: avelino-search-cedarfield-20261020' in new
    assert 'This Mac, Help: Search your entire computer, Value: 1' in new and 'button (disabled) forward' in new
    projections=json.loads(interactions[16]['text']);assert projections['completeSerializedTextArchived'] is False
    values=projections['observations'];assert len(values)==4
    raw='\n'.join(values[0]['searchControls']);key_undo='\n'.join(values[1]['searchControls']);menu_undo='\n'.join(values[2]['searchControls'])
    assert 'Value: avelinoulnacerulean, ID: Search' in raw and 'menu button Filename' not in raw
    assert 'Name Contains “avelinoulnacerulean”' in raw and 'Value: avelinoulnacerulean, ID: Search' in key_undo
    assert 'Filename: avelino-search-cedarfield-20261020' in menu_undo and 'Name Contains “avelinoulnacerulean”' in menu_undo
    assert report['undo']['atomicSingleStepAssumed'] is report['wholeTokenReplacement']['resultMatchingVerified'] is False
    restored=values[3];assert restored['outsideControlledRows']==0 and len(restored['controlledRootRows'])==3
    assert all('cedarfield-20261020' in url.lower() for url in restored['controlledRootRows'])
    assert 'Choose file…' in interactions[17]['text']
    print('Native Back/Forward discrepancy, whole-token replacement and multi-step Undo observations verified; native acceptance remains pending')


if __name__=='__main__':verify()
