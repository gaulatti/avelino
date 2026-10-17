"""Reject incomplete or falsely accepted Linux chart evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('chart_candidate',ROOT/'scripts/verify-chart-candidate.py')
charts=importlib.util.module_from_spec(spec);spec.loader.exec_module(charts)
class ChartCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((charts.DIRECTORY/'candidate.json').read_text())
        cls.profile=json.loads((charts.DIRECTORY/'captures/light-text1-dpr1.json').read_text())
        cls.projection=json.loads(charts.inputs.PROJECTION.read_text())
    def setUp(self):self.report=copy.deepcopy(self.original);self.actual=copy.deepcopy(self.profile)
    def rejects_report(self):
        with self.assertRaises(AssertionError):charts.validate_report(self.report)
    def rejects_profile(self):
        with self.assertRaises(AssertionError):charts.validate_profile(self.actual,self.projection)
    def test_complete_candidate_recomputes(self):charts.verify()
    def test_cannot_claim_acceptance(self):self.report['accepted']=True;self.rejects_report()
    def test_cannot_drop_nonfinite_gate(self):self.report['remainingAcceptance'].remove('nativeNonfiniteInputDeterminism');self.rejects_report()
    def test_cannot_add_exception(self):self.report['approvedExceptions']=['charts'];self.rejects_report()
    def test_missing_history_is_rejected(self):self.actual['histories'].pop();self.rejects_profile()
    def test_missing_edge_is_rejected(self):self.actual['edges'].pop();self.rejects_profile()
    def test_missing_data_step_is_rejected(self):self.actual['histories'][0]['steps'].pop(1);self.rejects_profile()
    def test_changed_configuration_is_rejected(self):self.actual['closed'][0]['configuration']['area']=True;self.rejects_profile()
    def test_forged_frame_match_is_rejected(self):self.actual['closed'][0]['nativeFrameMatches']=False;self.rejects_profile()
    def test_forged_metric_match_is_rejected(self):self.actual['closed'][0]['nativeMetricsMatch']=not self.actual['closed'][0]['nativeMetricsMatch'];self.rejects_profile()
    def test_changed_exact_metric_is_rejected(self):
        row=next(r for r in self.actual['closed'] if r['nativeMetricsMatch'])
        row['metrics']['seriesDomain']=['forged'];self.rejects_profile()
    def test_caller_recreation_is_rejected(self):self.actual['closed'][0]['state']['wrapperInstances']=2;self.rejects_profile()
    def test_missing_restore_is_rejected(self):self.actual['histories'][0]['steps'][-1]['restoredInitialPixelsAndGeometry']=False;self.rejects_profile()
    def test_disabled_input_checks_are_required(self):self.actual['inputContexts']=5;self.rejects_profile()
    def test_actual_qt_interfaces_are_required(self):self.actual['qtAccessibilityChecks']='pending';self.rejects_profile()
    def test_physical_acceptance_cannot_be_claimed(self):self.report['validation']['physicalDisplay']=True;self.rejects_report()
if __name__=='__main__':unittest.main()
