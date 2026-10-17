#!/usr/bin/env python3
"""Measure the pinned native marker's physical pixel coverage without changing frames."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PROJECTION=ROOT/'tests/consumer/native-pill-witnesses.json'
def projected():
    data=json.loads(PROJECTION.read_text());rows=[]
    for row in data['closed']:
        if row['configuration']['parentLayout']=='baseline':
            for value in [row,row['bare']]:rows.append((value,row['dpr']))
    for history in data['histories']:
        if history['configuration']['parentLayout']=='baseline':
            rows.extend((step,history['dpr']) for step in history['steps'])
    assert len(rows)==1024
    result=[]
    for row,dpr in rows:
        frame=row['parts']['reference'][0];path=ROOT/row['reference']
        left,top=math.floor(frame['x']*dpr+0.5),math.floor(frame['y']*dpr+0.5)
        width,height=int(frame['width']*dpr),int(frame['height']*dpr)
        assert width==3*dpr and height==30*dpr
        with Image.open(path) as source:
            image=source.convert('RGBA');points=[]
            for y in range(top-1,top+height+1):
                for x in range(left-1,left+width+1):
                    if image.getpixel((x,y))==(44,87,132,255):points.append((x,y))
        assert len(points)==width*height,(row['reference'],frame,len(points))
        assert min(x for x,y in points)==left and max(x for x,y in points)==left+width-1
        assert min(y for x,y in points)==top and max(y for x,y in points)==top+height-1
        result.append(dict(reference=row['reference'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dpr=dpr,frame=frame,paintBounds=[left,top,width,height],opaqueBluePixels=len(points)))
    return dict(reference=data['reference'],accepted=False,observations=result,policy='The native sharp marker paints exactly 3*dpr by 30*dpr opaque blue pixels at the nearest physical pixel origin; its emitted frame stays fractional. No native expectation or tolerance changes.')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    text=json.dumps(projected(),indent=2)+'\n'
    if args.check:assert args.output.read_text()==text
    else:
        assert not args.output.exists();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print('Native pill marker: 1024 sharp physical-pixel rectangles; fractional frames preserved')
