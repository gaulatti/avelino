"""Keep scale probes, native identity and the fresh source replay intact."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('chart_geometry_source',ROOT/'scripts/verify-chart-geometry-source.py');source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
class ChartGeometrySource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=json.loads((source.DIRECTORY/'investigation.json').read_text())
    def setUp(self):self.report=copy.deepcopy(self.original)
    def refused(self):
        with self.assertRaises(AssertionError):source.validate_report(self.report)
    def test_complete_source_recomputes(self):source.verify()
    def test_cannot_claim_acceptance(self):self.report['accepted']=True;self.refused()
    def test_cannot_change_pin(self):self.report['reference']='other';self.refused()
    def test_cannot_drop_context(self):self.report['contexts']=124;self.refused()
    def test_cannot_drop_scale(self):self.report['requestedDprs'].remove(1.75);self.refused()
    def test_cannot_change_actual_backing(self):self.report['actualBackingDpr']=1.75;self.refused()
    def test_cannot_drop_replay_file(self):self.report['freshSourceReplayExactFiles']=502;self.refused()
    def test_cannot_drop_fractional_layout_gate(self):self.report['remainingAcceptance'].remove('nativeFractionalFontLayout');self.refused()
    def test_cannot_claim_physical_acceptance(self):self.report['remainingAcceptance'].remove('physicalDisplaysInput');self.refused()
    def test_cannot_approve_exception(self):self.report['approvedExceptions']=['font'];self.refused()
    def test_cannot_rewrite_expected_image(self):self.report['expectedImagesChanged']=True;self.refused()
    def test_cannot_claim_download_availability(self):self.report['sourceOnlyArtifact']['downloadAvailability']='passed';self.refused()
if __name__=='__main__':unittest.main()
