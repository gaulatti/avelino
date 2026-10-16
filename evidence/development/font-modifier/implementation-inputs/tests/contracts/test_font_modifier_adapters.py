"""Protect the complete native-to-catalog font contract without granting parity."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
inputs=load('font_adapter_inputs','capture-font-modifier-cases.py')
compare=load('font_adapter_comparison','compare-font-modifier-captures.py')
witness=load('font_adapter_witnesses','generate-font-modifier-witnesses.py')
class FontModifierAdapters(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.corpus=inputs.rows()
 def setUp(self):
  self.row=next(r for r in self.corpus if r['definition']['fixture']=='baseline-primary-regular' and r['source']['appearance']=='light' and r['source']['textScale']==1 and r['source']['dpr']==1)
  state=self.row['source']['states'][1]
  self.meta=dict(renderedFamily='primary',renderedSize=14,renderedWeight='regular',renderedTextScale=1,renderedResolvedPixelSize=14,renderedRtl=False,
   fontModifierParts=copy.deepcopy(state['partInstances']),fontModifierBaselines=copy.deepcopy(state['baselines']),
   fontModifierState={k:state[k] for k in ['appearances','disappearances','callerInstances']})
 def observe(self):return compare.observations(self.row,self.meta)
 def test_all_native_contexts_projected(self):
  self.assertEqual(len(self.corpus),1656);self.assertEqual(len(inputs.definitions(self.corpus)['fixtures']),207)
  self.assertEqual({kind:sum(r['kind']==kind for r in self.corpus) for kind in inputs.CORPORA},{'caller':864,'baseline':720,'negative':72})
 def test_projection_matches_packaged_resource(self):self.assertEqual((ROOT/'tests/consumer/native-font-modifier-witnesses.json').read_text(),witness.projected())
 def test_native_witness_pixel_failures_remain_in_matrix(self):
  self.assertEqual(sum(not r['source']['publicWitnessIdentical'] for r in self.corpus),3)
 def test_exact_measurements_pass(self):
  r=self.observe();self.assertEqual([r[k] for k in ['partFramesStatus','baselineStatus','stateStatus']],['passed']*3)
 def test_missing_emitted_view_fails(self):
  del self.meta['fontModifierParts']['label'];self.assertEqual(self.observe()['partFramesStatus'],'failed')
 def test_extra_wrapper_fails(self):
  self.meta['fontModifierParts']['wrapper']=self.meta['fontModifierParts']['root'];self.assertEqual(self.observe()['partFramesStatus'],'failed')
 def test_changed_caller_allocation_fails(self):
  self.meta['fontModifierParts']['label'][0]['width']+=1;self.assertEqual(self.observe()['partFramesStatus'],'failed')
 def test_missing_baseline_fails(self):
  del self.meta['fontModifierBaselines']['label'];self.assertEqual(self.observe()['baselineStatus'],'failed')
 def test_invented_centered_baseline_fails(self):
  self.row=next(r for r in self.corpus if r['definition']['fixture']=='caller-primary-regular');self.assertEqual(self.observe()['baselineStatus'],'failed')
 def test_caller_recreation_fails(self):
  self.meta['fontModifierState']['callerInstances']=2;self.assertEqual(self.observe()['stateStatus'],'failed')
 def test_font_environment_must_reach_scope(self):
  self.meta['renderedFamily']='secondary';self.assertIn('renderedFamily',self.observe()['stateErrors'])
 def test_fractional_mono_is_not_rounded(self):
  self.row=next(r for r in self.corpus if r['definition']['fixture']=='caller-size-mono-0.49' and r['source']['textScale']==1)
  self.meta['renderedResolvedPixelSize']=12;self.assertIn('renderedResolvedPixelSize',self.observe()['stateErrors'])
 def test_finite_negative_resolves_twelve(self):
  self.row=next(r for r in self.corpus if r['kind']=='negative');self.meta['renderedResolvedPixelSize']=-14
  self.assertEqual(self.observe()['stateErrors']['renderedResolvedPixelSize']['reference'],12)
 def test_resource_cannot_claim_acceptance(self):
  d=json.loads(witness.projected());self.assertIs(d['accepted'],False);self.assertEqual(d['reference'],inputs.REFERENCE)
if __name__=='__main__':unittest.main()
