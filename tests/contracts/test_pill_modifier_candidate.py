"""Reject incomplete or falsely accepted pill candidate evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('pill_candidate',ROOT/'scripts/verify-pill-modifier-candidate.py')
candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
class PillModifierCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((candidate.DIRECTORY/'candidate.json').read_text())
        cls.profile=json.loads((candidate.DIRECTORY/'captures/light-text1-dpr1.json').read_text())
        cls.projection=json.loads((ROOT/'tests/consumer/native-pill-witnesses.json').read_text())
    def setUp(self):self.report=copy.deepcopy(self.original);self.actual=copy.deepcopy(self.profile)
    def refused(self):
        with self.assertRaises(AssertionError):candidate.validate_report(self.report)
    def profile_refused(self):
        with self.assertRaises(AssertionError):candidate.validate_pill_profile(self.actual,self.projection)
    def test_sealed_candidate_recomputes_all_native_results(self):candidate.verify()
    def test_cannot_claim_acceptance(self):self.report['accepted']=True;self.refused()
    def test_pin_cannot_change(self):self.report['reference']='unapproved';self.refused()
    def test_tolerance_cannot_change(self):self.report['tolerance']='one pixel';self.refused()
    def test_exception_cannot_be_approved(self):self.report['approvedExceptions']=['FONT-MONO-001'];self.refused()
    def test_expected_images_cannot_change(self):self.report['expectedImagesChanged']=True;self.refused()
    def test_partial_matrix_cannot_pass(self):self.report['strictComparison']['cases']=2111;self.refused()
    def test_historical_failures_cannot_be_erased(self):self.report['attempts'].pop();self.refused()
    def test_historical_failure_cannot_be_called_success(self):self.report['attempts'][0]['exitCode']=0;self.refused()
    def test_reader_gate_cannot_close(self):self.report['remainingAcceptance'].remove('readers');self.refused()
    def test_frame_flag_must_match_actual_geometry(self):self.actual['rows'][0]['modes'][0]['nativeFramesMatch']=not self.actual['rows'][0]['modes'][0]['nativeFramesMatch'];self.profile_refused()
    def test_caller_cannot_be_recreated(self):self.actual['histories'][0]['steps'][2]['state']['callerInstances']=2;self.profile_refused()
    def test_history_step_cannot_be_skipped(self):self.actual['histories'][0]['steps'].pop();self.profile_refused()
    def test_complete_restore_is_required(self):self.actual['histories'][0]['steps'][-1]['restoredInitialPixelsAndGeometry']=False;self.profile_refused()
    def test_emitted_guide_cannot_be_hidden(self):
        row=next(r for r in self.actual['rows'] if r['configuration']['id']=='baseline-style-primary19')
        del row['modes'][0]['guides']['label'];self.profile_refused()
    def test_bare_mode_cannot_be_dropped(self):self.actual['rows'][0]['modes'].pop();self.profile_refused()
    def test_alpha_difference_is_not_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            a,b=Path(temporary)/'a.png',Path(temporary)/'b.png'
            Image.new('RGBA',(1,1),(20,30,40,255)).save(a);Image.new('RGBA',(1,1),(20,30,40,254)).save(b)
            self.assertFalse(candidate.pixel_metrics(a,b)['matches'])
if __name__=='__main__':unittest.main()
