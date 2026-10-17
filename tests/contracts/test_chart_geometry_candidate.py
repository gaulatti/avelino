"""Prevent readiness checks from accepting unresolved native chart differences."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('chart_geometry_candidate',ROOT/'scripts/verify-chart-geometry-candidate.py');candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
class ChartGeometryCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=json.loads((candidate.DIRECTORY/'candidate.json').read_text())
    def setUp(self):self.report=copy.deepcopy(self.original)
    def refused(self):
        with self.assertRaises(AssertionError):candidate.validate_report(self.report)
    def test_complete_evidence_recomputes(self):candidate.verify()
    def test_cannot_claim_acceptance(self):self.report['accepted']=True;self.refused()
    def test_cannot_change_pin(self):self.report['reference']='other';self.refused()
    def test_cannot_change_base(self):self.report['baseRevision']='other';self.refused()
    def test_cannot_drop_fractional_gate(self):self.report['remainingAcceptance'].remove('nativeFractionalFontLayout');self.refused()
    def test_cannot_drop_proposal_gate(self):self.report['remainingAcceptance'].remove('intrinsicProposals');self.refused()
    def test_cannot_drop_readers(self):self.report['remainingAcceptance'].remove('readers');self.refused()
    def test_cannot_raise_metric_matches(self):self.report['canonicalComparison']['nativeMetricMatches']+=1;self.refused()
    def test_cannot_accept_supplement(self):self.report['supplementalComparison']['exactMatches']=1;self.refused()
    def test_cannot_approve_exception(self):self.report['approvedExceptions']=['font'];self.refused()
    def test_cannot_rewrite_expected(self):self.report['expectedImagesChanged']=True;self.refused()
    def test_cannot_claim_physical_display(self):self.report['validation']['physicalDisplay']=True;self.refused()
    def test_cannot_claim_hardware_gpu(self):self.report['validation']['hardwareAcceleration']=True;self.refused()
    def test_cannot_claim_old_full_suite_for_new_module(self):self.report['historicalFullQtSuite']['currentModuleTestedByThatRun']=True;self.refused()
    def test_cannot_hide_first_failed_test(self):self.report['attempts'][0]['exitCode']=0;self.refused()
    def test_cannot_hide_strict_exit(self):next(r for r in self.report['attempts'] if r['name']=='charts-geometry-comparison-v1')['exitCode']=0;self.refused()
if __name__=='__main__':unittest.main()
