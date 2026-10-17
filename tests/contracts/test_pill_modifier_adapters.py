"""Preserve the entire native pill matrix and strict observation boundaries."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
inputs=load('pill_adapter_inputs','capture-pill-modifier-cases.py')
witness=load('pill_adapter_witnesses','generate-pill-witnesses.py')
class PillModifierAdapters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.corpus=inputs.rows()
    def setUp(self):
        self.row=next(r for r in self.corpus if r['kind']=='public' and r['configuration']['id']=='baseline-default')
        self.meta={key:copy.deepcopy(self.row[key]) for key in ['configuration','appearance','textScale','dpr','kind','parts','guides']}
        self.meta['state']=dict(appearances=1,disappearances=0,callerInstances=1)
    def observe(self):return inputs.observations(self.row,self.meta)
    def test_complete_matrix_includes_bare_and_histories(self):
        self.assertEqual(len(self.corpus),2112)
        self.assertEqual({k:sum(r['kind']==k for r in self.corpus) for k in ['public','bare','history']},dict(public=888,bare=888,history=336))
        self.assertEqual({r['step'] for r in self.corpus if r['kind']=='history'},set(range(6)))
    def test_packaged_projection_is_exact(self):self.assertEqual(inputs.PROJECTION.read_text(),witness.projected())
    def test_acceptance_cannot_be_claimed(self):
        data=json.loads(witness.projected());data['accepted']=True
        with self.assertRaises(AssertionError):inputs.rows(data)
    def test_missing_context_fails(self):
        data=json.loads(witness.projected());data['closed'].pop()
        with self.assertRaises(AssertionError):inputs.rows(data)
    def test_missing_history_step_fails(self):
        data=json.loads(witness.projected());data['histories'][0]['steps'].pop()
        with self.assertRaises(AssertionError):inputs.rows(data)
    def test_exact_observations_pass(self):
        value=self.observe();self.assertEqual([value[k] for k in ['partFramesStatus','baselineStatus','stateStatus']],['passed']*3)
    def test_missing_label_is_not_ignored(self):
        del self.meta['parts']['label'];self.assertEqual(self.observe()['partFramesStatus'],'failed')
    def test_added_wrapper_is_not_ignored(self):
        self.meta['parts']['wrapper']=self.meta['parts']['styled'];self.assertEqual(self.observe()['partFramesStatus'],'failed')
    def test_fractional_change_is_not_tolerated(self):
        self.meta['parts']['label'][0]['width']+=1e-9;self.assertEqual(self.observe()['partFramesStatus'],'failed')
    def test_requested_baseline_cannot_be_missing(self):
        del self.meta['guides']['label'];self.assertEqual(self.observe()['baselineStatus'],'failed')
    def test_center_baseline_cannot_be_invented(self):
        self.row=dict(self.row,guides={});self.assertEqual(self.observe()['baselineStatus'],'failed')
    def test_caller_recreation_fails(self):
        self.meta['state']['callerInstances']=2;self.assertEqual(self.observe()['stateStatus'],'failed')
    def test_changed_configuration_fails(self):
        self.meta['configuration']['text']='forged';self.assertEqual(self.observe()['stateStatus'],'failed')
    def test_history_restore_must_be_observed(self):
        self.row=next(r for r in self.corpus if r['kind']=='history' and r['step']==5)
        self.meta={key:copy.deepcopy(self.row[key]) for key in ['configuration','appearance','textScale','dpr','kind','parts','guides']}
        self.meta['state']=dict(appearances=1,disappearances=0,callerInstances=1)
        self.assertIn('restoredInitialPixelsAndGeometry',self.observe()['stateErrors'])
        self.meta['restoredInitialPixelsAndGeometry']=True;self.assertEqual(self.observe()['stateStatus'],'passed')
    def test_qml_font_warnings_fail_capture(self):
        with self.assertRaises(AssertionError):inputs.verify_capture_log('Could not find any constructor for value type QQuickFontValueType')
    def test_decimal_context_name_is_not_truncated(self):
        self.assertEqual(inputs.report_path(Path('captures/light-text1.5-dpr2')),Path('captures/light-text1.5-dpr2.json'))
if __name__=='__main__':unittest.main()
