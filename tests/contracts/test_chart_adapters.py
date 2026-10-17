"""Keep every source input and history step in the strict chart comparison."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
inputs=load('chart_adapter_inputs','capture-charts.py')
witness=load('chart_adapter_witnesses','generate-chart-witnesses.py')
class ChartAdapters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.corpus=inputs.rows()
    def setUp(self):
        self.row=next(r for r in self.corpus if r['kind']=='closed' and r['configuration']['id']=='line-default')
        self.meta={key:copy.deepcopy(self.row[key]) for key in ['configuration','appearance','textScale','dpr','kind','frame','metrics']}
        self.meta['state']=dict(appearances=1,disappearances=0,wrapperInstances=1)
    def observe(self):return inputs.observations(self.row,self.meta)
    def test_complete_inputs_and_all_steps(self):
        self.assertEqual(len(self.corpus),1744)
        self.assertEqual({k:sum(r['kind']==k for r in self.corpus) for k in ['closed','edge','history']},dict(closed=960,edge=400,history=384))
        self.assertEqual({r['step'] for r in self.corpus if r['kind']=='history'},set(range(8)))
        self.assertEqual({r['configuration']['kind'] for r in self.corpus},set(inputs.APIS))
    def test_projection_preserves_source(self):self.assertEqual(json.loads(inputs.PROJECTION.read_text()),witness.projected())
    def test_acceptance_cannot_be_claimed(self):
        data=witness.projected();data['accepted']=True
        with self.assertRaises(AssertionError):inputs.rows(data)
    def test_missing_edge_fails(self):
        data=witness.projected();data['edges'].pop()
        with self.assertRaises(AssertionError):inputs.rows(data)
    def test_missing_history_step_fails(self):
        data=witness.projected();data['histories'][0]['steps'].pop()
        with self.assertRaises(AssertionError):inputs.rows(data)
    def test_exact_observations_pass(self):
        value=self.observe();self.assertEqual([value[k] for k in ['layoutStatus','nativeFrameStatus','nativeMetricsStatus','stateStatus']],['passed']*4)
    def test_fractional_metric_change_is_not_tolerated(self):
        self.meta['metrics']['points'][0]['yPosition']+=1e-9;self.assertEqual(self.observe()['nativeMetricsStatus'],'failed')
    def test_missing_point_fails(self):
        self.meta['metrics']['points'].pop();self.assertEqual(self.observe()['nativeMetricsStatus'],'failed')
    def test_missing_domain_fails(self):
        del self.meta['metrics']['seriesDomain'];self.assertEqual(self.observe()['nativeMetricsStatus'],'failed')
    def test_extra_diagnostic_fields_do_not_replace_source_metrics(self):
        self.meta['metrics']['nativeRasterAcceptance']='pending';self.assertEqual(self.observe()['nativeMetricsStatus'],'passed')
    def test_caller_recreation_fails(self):
        self.meta['state']['wrapperInstances']=2;self.assertEqual(self.observe()['stateStatus'],'failed')
    def test_changed_configuration_fails(self):
        self.meta['configuration']['area']=True;self.assertEqual(self.observe()['stateStatus'],'failed')
    def test_history_restore_must_be_observed(self):
        self.row=next(r for r in self.corpus if r['kind']=='history' and r['step']==7)
        self.meta={key:copy.deepcopy(self.row[key]) for key in ['configuration','appearance','textScale','dpr','kind','frame','metrics']}
        self.meta['state']=dict(appearances=1,disappearances=0,wrapperInstances=1)
        self.assertEqual(self.observe()['stateStatus'],'failed')
        self.meta['restoredInitialPixelsAndGeometry']=True;self.assertEqual(self.observe()['stateStatus'],'passed')
    def test_nan_bar_source_is_not_excluded(self):
        rows=[r for r in self.corpus if r['kind']=='edge' and r['configuration']['id']=='bar-y-nan-one']
        self.assertEqual(len(rows),8)
        self.assertEqual({r['configuration']['points'][1]['y'] for r in rows},{'__native_nan__'})
    def test_edge_metrics_are_unobserved(self):
        self.row=next(r for r in self.corpus if r['kind']=='edge');self.assertEqual(self.observe()['nativeMetricsStatus'],'unobserved')
    def test_bool_cannot_replace_metric_number(self):self.assertFalse(inputs.subset(True,1))
if __name__=='__main__':unittest.main()
