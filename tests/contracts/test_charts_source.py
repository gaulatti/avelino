"""Guard the native chart corpus against false acceptance and lost evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('charts_source',ROOT/'scripts/verify-charts-source.py')
charts=importlib.util.module_from_spec(spec);spec.loader.exec_module(charts)

class NativeChartsSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((charts.DIRECTORY/'investigation.json').read_text())
        cls.state=json.loads((charts.DIRECTORY/'captures/closed-line-default/captures.json').read_text())['rows'][0]['states'][1]
    def setUp(self):self.report=copy.deepcopy(self.original);self.actual=copy.deepcopy(self.state)
    def refused(self):
        with self.assertRaises(AssertionError):charts.validate_report(self.report)
    def state_refused(self):
        with self.assertRaises(AssertionError):charts.wrapper(self.actual)
    def test_complete_source_corpus_recomputes(self):charts.verify()
    def test_source_cannot_claim_acceptance(self):self.report['accepted']=True;self.refused()
    def test_source_pin_cannot_change(self):self.report['reference']='other';self.refused()
    def test_tolerance_cannot_be_invented(self):self.report['tolerance']='one pixel';self.refused()
    def test_exception_cannot_be_self_approved(self):self.report['approvedExceptions']=['chart-font'];self.refused()
    def test_expected_images_cannot_be_replaced(self):self.report['expectedImagesChanged']=True;self.refused()
    def test_linux_implementation_cannot_be_closed(self):self.report['remainingAcceptance'].remove('LinuxImplementation');self.refused()
    def test_reader_gate_cannot_be_closed(self):self.report['remainingAcceptance'].remove('readers');self.refused()
    def test_fixture_cannot_be_dropped(self):self.report['summary']['fixtures']=119;self.refused()
    def test_nonfinite_inputs_cannot_be_erased(self):self.report['summary']['edgeCases']=49;self.refused()
    def test_native_nonfinite_variation_cannot_be_accepted(self):self.report['remainingAcceptance'].remove('nativeNonfiniteInputDeterminism');self.refused()
    def test_sizing_proposals_cannot_be_reduced(self):self.report['summary']['sizingQueries']=12000;self.refused()
    def test_history_step_cannot_be_erased(self):self.report['summary']['historySteps']=383;self.refused()
    def test_wrapper_recreation_cannot_pass(self):self.actual['wrapperInstances']=2;self.state_refused()
    def test_disappearance_cannot_pass(self):self.actual['disappearances']=1;self.state_refused()
    def test_application_activation_cannot_be_called_prohibited(self):self.actual['applicationActive']=True;self.state_refused()
    def test_nonfinite_measured_frame_cannot_pass(self):self.actual['frame']['width']=float('nan');self.state_refused()
    def test_truncated_accessibility_snapshot_cannot_pass(self):self.actual['accessibility']['truncated']=True;self.state_refused()

if __name__=='__main__':unittest.main()
