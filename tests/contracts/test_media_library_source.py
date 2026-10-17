"""Keep public grid observations and unresolved source differences reviewable."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('media_library_source',ROOT/'scripts/verify-media-library-source.py');source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
class MediaLibrarySource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=json.loads((source.DIRECTORY/'investigation.json').read_text())
    def setUp(self):self.report=copy.deepcopy(self.original)
    def refused(self):
        with self.assertRaises(AssertionError):source.validate_report(self.report)
    def test_complete_source_evidence_recomputes(self):source.verify()
    def test_cannot_claim_acceptance(self):self.report['accepted']=True;self.refused()
    def test_cannot_change_pin(self):self.report['reference']='other';self.refused()
    def test_cannot_hide_sizing_witness_difference(self):self.report['summary']['sizingWitnessMatches']=496;self.refused()
    def test_cannot_drop_sizing_gate(self):self.report['remainingAcceptance'].remove('nativeSizingWitnessDifference');self.refused()
    def test_cannot_drop_lazy_timing_gate(self):self.report['remainingAcceptance'].remove('nativeLazyViewportTiming');self.refused()
    def test_cannot_drop_linux_implementation(self):self.report['remainingAcceptance'].remove('LinuxImplementation');self.refused()
    def test_cannot_drop_physical_gate(self):self.report['remainingAcceptance'].remove('physicalDisplaysInput');self.refused()
    def test_cannot_drop_readers(self):self.report['remainingAcceptance'].remove('readers');self.refused()
    def test_cannot_approve_exception(self):self.report['approvedExceptions']=['sizing'];self.refused()
    def test_cannot_rewrite_expected(self):self.report['expectedImagesChanged']=True;self.refused()
    def test_cannot_add_tolerance(self):self.report['tolerance']='one pixel';self.refused()
    def test_cannot_drop_history_step(self):self.report['summary']['historySteps']=1007;self.refused()
    def test_cannot_drop_edge_context(self):self.report['summary']['edgeContexts']=104;self.refused()
    def test_cannot_change_source_file_scope(self):self.report['sourceOnlyArtifact']['containsPinnedSourceFiles']=88;self.refused()
    def test_cannot_claim_independent_download(self):self.report['sourceOnlyArtifact']['downloadAvailability']='passed';self.refused()
if __name__=='__main__':unittest.main()
