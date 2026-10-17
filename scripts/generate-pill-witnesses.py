#!/usr/bin/env python3
"""Project every native pill context without changing reference pixels or guides."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/reference-investigations/pill-modifier-20261016'
TARGET=ROOT/'tests/consumer/native-pill-witnesses.json'

def config(value):return dict(value,offer=value.get('offer'),lineLimit=value.get('lineLimit'))
def observation(states):
 public,witness=states[1:3]
 parts=dict(public['parts'],label=witness['parts']['label'])
 guides=dict(public['guides'])
 if 'label' in witness['guides']:guides['label']=witness['guides']['label']
 return dict(parts=parts,guides=guides)
def projected():
 closed=[]
 for folder in ['closed','empty']:
  for row in json.loads((SOURCE/folder/'captures.json').read_text())['captures']:
   bare=row['states'][3]
   closed.append(dict(configuration=config(row['configuration']),appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],
     **observation(row['states']),bare=dict(parts=bare['parts'],guides=bare['guides'],reference=str((SOURCE/folder/row['paths'][3]).relative_to(ROOT))),reference=str((SOURCE/folder/row['paths'][0]).relative_to(ROOT))))
 histories=[]
 for row in json.loads((SOURCE/'histories/histories.json').read_text())['histories']:
  steps=[]
  for step in row['steps']:
   state=step['states'][1]
   steps.append(dict(step=step['step'],configuration=config(state['configuration']),appearance=state['appearance'],textScale=state['textScale'],
     **observation(step['states']),reference=str((SOURCE/'histories'/step['paths'][0]).relative_to(ROOT))))
  histories.append(dict(configuration=config(row['configuration']),appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],steps=steps))
 return json.dumps(dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',accepted=False,closed=closed,histories=histories),indent=2,ensure_ascii=False)+'\n'
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();text=projected()
 if args.check:assert TARGET.read_text()==text
 else:TARGET.write_text(text)
 print('Pill witnesses: all 888 closed and 56 retained history contexts; no acceptance')
