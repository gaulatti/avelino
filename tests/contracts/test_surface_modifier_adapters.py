"""Keep all native surface callers and their unresolved acceptance visible."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
inputs=load('surface_adapter_inputs','capture-surface-modifier-cases.py')
compare=load('surface_adapter_comparison','surface-modifier-observations.py')
witness=load('surface_adapter_witnesses','generate-surface-modifier-witnesses.py')
class SurfaceModifierAdapters(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.corpus=inputs.rows()
 def setUp(self):
  self.row=next(r for r in self.corpus if r['definition']['fixture']=='surface-content-multi' and r['source']['appearance']=='light' and r['source']['textScale']==1 and r['source']['dpr']==1)
  state=self.row['source']['states'][1]
  self.meta=dict(renderedRadius=12,renderedRtl=False,renderedTextScale=1,surfaceModifierParts=copy.deepcopy(state['partInstances']),surfaceModifierBaselines={},
   surfaceModifierState={k:state[k] for k in ['appearances','disappearances','callerInstances','actions','counter']})
 def observe(self):return compare.observations(self.row,self.meta)
 def test_all_closed_contexts_projected(self):
  self.assertEqual(len(self.corpus),416);self.assertEqual(len(inputs.definitions(self.corpus)['fixtures']),52)
 def test_unresolved_os_contexts_retained(self):
  self.assertEqual({r['definition']['fixture'] for r in self.corpus if r['definition']['parentFont'] or r['definition']['content'] in ['button','system-font']},{'surface-parent-font32','surface-content-button','surface-content-system-font'})
 def test_packaged_projection_matches(self):self.assertEqual((ROOT/'tests/consumer/native-surface-modifier-witnesses.json').read_text(),witness.projected())
 def test_all_retained_histories_projected(self):
  d=json.loads(witness.projected());self.assertEqual(len(d['histories']),10);self.assertTrue(all(len(h['steps'])==6 for h in d['histories']))
 def test_exact_frames_and_state_pass(self):
  r=self.observe();self.assertEqual(r['partFramesStatus'],'passed');self.assertEqual(r['stateStatus'],'passed');self.assertEqual(r['baselineStatus'],'not-requested')
 def test_flat_children_cannot_collapse(self):
  self.meta['surfaceModifierParts']['styled']=self.meta['surfaceModifierParts']['styled'][:1];self.assertEqual(self.observe()['partFramesStatus'],'failed')
 def test_extra_wrapper_fails(self):
  self.meta['surfaceModifierParts']['wrapper']=self.meta['surfaceModifierParts']['root'];self.assertEqual(self.observe()['partFramesStatus'],'failed')
 def test_small_geometry_change_fails(self):
  self.meta['surfaceModifierParts']['first'][0]['width']+=1e-8;self.assertEqual(self.observe()['partFramesStatus'],'failed')
 def test_nonfinite_bounds_fail(self):
  self.meta['surfaceModifierParts']['first'][0]['width']=float('nan');self.assertEqual(self.observe()['partFramesStatus'],'failed')
 def test_boolean_bounds_fail(self):
  self.meta['surfaceModifierParts']['first'][0]['width']=True;self.assertEqual(self.observe()['partFramesStatus'],'failed')
 def test_malformed_frame_map_fails(self):
  self.meta['surfaceModifierParts']=[];self.assertEqual(self.observe()['partFramesStatus'],'failed')
 def test_invented_baseline_fails(self):
  self.meta['surfaceModifierBaselines']={'root':12};self.assertEqual(self.observe()['baselineStatus'],'failed')
 def test_missing_empty_baseline_map_fails(self):
  del self.meta['surfaceModifierBaselines'];self.assertEqual(self.observe()['baselineStatus'],'failed')
 def test_changed_radius_fails(self):
  self.meta['renderedRadius']=0;self.assertIn('renderedRadius',self.observe()['stateErrors'])
 def test_boolean_radius_fails(self):
  self.meta['renderedRadius']=True;self.assertIn('renderedRadius',self.observe()['stateErrors'])
 def test_caller_recreation_fails(self):
  self.meta['surfaceModifierState']['callerInstances']=2;self.assertEqual(self.observe()['stateStatus'],'failed')
 def test_boolean_state_cannot_replace_a_count(self):
  self.meta['surfaceModifierState']['callerInstances']=True;self.assertEqual(self.observe()['stateStatus'],'failed')
 def test_missing_caller_state_fails(self):
  self.meta['surfaceModifierState']=None;self.assertEqual(self.observe()['stateStatus'],'failed')
 def test_unrequested_action_fails(self):
  self.meta['surfaceModifierState']['actions']=1;self.assertEqual(self.observe()['stateStatus'],'failed')
 def test_color_group_binding_loop_is_rejected(self):
  with self.assertRaisesRegex(AssertionError,'binding or font diagnostic'):inputs.verify_capture_log('<Unknown File>: QML ColorGroup: Binding loop detected for property "windowText"')
 def test_font_diagnostic_is_rejected(self):
  with self.assertRaises(AssertionError):inputs.verify_capture_log('QFont::setPointSizeF: Point size <= 0')
 def test_projection_cannot_accept_guides_or_mirror(self):
  d=json.loads(witness.projected());self.assertIs(d['accepted'],False);self.assertTrue(d['baselineAcceptance'].startswith('pending'));self.assertTrue(all(c['baselines']=={} for c in d['contexts']))
if __name__=='__main__':unittest.main()
