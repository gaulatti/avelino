import copy
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
capture=module('button_style_input_contracts','capture-button-style-cases.py')
compare=module('button_style_adapter_contracts','compare-button-style-captures.py')
SOURCE=json.loads((capture.SOURCE/'captures/captures.json').read_text())

class ButtonStyleAdapters(unittest.TestCase):
    def setUp(self):
        self.row=copy.deepcopy(next(r for r in SOURCE['captures'] if r['configuration']['fixture']=='multi-parent-hstack'))
        f=self.row['configuration']
        self.meta=dict(renderedVariant=f['variant'],renderedSize=f['size'],renderedDisabled=f['disabled'],renderedRtl=f['rtl'],
            renderedWidthOffer=-1,renderedMaximumWidth=-1,buttonStylePartInstances=copy.deepcopy(self.row['states'][1]['partInstances']),
            buttonStyleState={k:self.row['states'][1][k] for k in ['count','calls','mountValues']},
            renderedLabelObjects=[dict(objectName=n) for n in ['buttonStyleFirst','buttonStyleSecond']])
    def test_complete_matrix_is_preserved(self):
        self.assertEqual(len(capture.definitions(SOURCE)['fixtures']),88)
        data=compare.observations(self.row,self.meta)
        self.assertEqual(data['partFramesStatus'],'passed');self.assertEqual(data['stateStatus'],'passed')
    def test_missing_context_rejected(self):
        source=copy.deepcopy(SOURCE);source['captures'].pop()
        with self.assertRaises(AssertionError):capture.definitions(source)
    def test_duplicate_context_rejected(self):
        source=copy.deepcopy(SOURCE);source['captures'][1]=source['captures'][0]
        with self.assertRaises(AssertionError):capture.definitions(source)
    def test_invalid_source_probe_cannot_supply_cases(self):
        source=copy.deepcopy(SOURCE);source['captures'][0]['publicProbedIdentical']=False
        with self.assertRaises(AssertionError):capture.definitions(source)
    def test_flat_parts_cannot_collapse(self):
        self.meta['buttonStylePartInstances']['body'].pop()
        self.assertEqual(compare.observations(self.row,self.meta)['partFramesStatus'],'failed')
    def test_padding_drift_cannot_hide_behind_parent_frame(self):
        self.meta['buttonStylePartInstances']['body'][0]['width']+=1
        self.assertEqual(compare.observations(self.row,self.meta)['partFramesStatus'],'failed')
    def test_state_must_come_from_rendered_producer(self):
        self.meta['disabled']=True;self.meta['renderedDisabled']=not self.row['configuration']['disabled']
        self.assertEqual(compare.observations(self.row,self.meta)['stateStatus'],'failed')
    def test_forged_initial_counter_rejected(self):
        self.meta['buttonStyleState']['count']=1
        self.assertEqual(compare.observations(self.row,self.meta)['stateStatus'],'failed')
    def test_missing_live_label_objects_rejected(self):
        self.meta['renderedLabelObjects'].pop()
        self.assertEqual(compare.observations(self.row,self.meta)['stateStatus'],'failed')
    def test_full_comparison_reaches_pixels_and_source_frames(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';images=source/'captures';images.mkdir(parents=True)
            candidate=root/'candidate';candidate.mkdir();name=self.row['paths'][0]
            image=Image.new('RGB',(640,400),'white');image.save(images/name);image.save(candidate/name)
            metadata={**self.row['configuration'],**self.meta,'api':'BleeckerButtonStyle',
                      'appearance':self.row['appearance'],'textScale':self.row['textScale'],'dpr':self.row['dpr']}
            (candidate/(name+'.json')).write_text(json.dumps(metadata))
            (images/'captures.json').write_text(json.dumps({'captures':[self.row]}))
            (source/'investigation.json').write_text(json.dumps({'files':{'captures/'+name:capture.digest(images/name)}}))
            with patch.object(compare,'SOURCE',source),patch.object(compare.native,'verify'):
                self.assertEqual(compare.compare(candidate,root/'result'),0)
            result=json.loads((root/'result/comparison.json').read_text())
            self.assertEqual(result['results'][0]['referenceRevision'],capture.REFERENCE)
            self.assertEqual(result['summary']['exactPixelAndGeometryMatches'],1)
            self.assertFalse(result['accepted'])

if __name__=='__main__':unittest.main()
