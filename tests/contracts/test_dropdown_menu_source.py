"""Keep native menu measurements distinct from Linux and physical acceptance."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('dropdown_source', ROOT / 'scripts/verify-dropdown-menu-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class DropdownMenuSource(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((source.DIRECTORY / 'investigation.json').read_text())

    def refused(self):
        with self.assertRaises(AssertionError):
            source.validate_report(self.report)

    def test_complete_source_record_recomputes(self):
        source.verify()

    def test_cannot_claim_linux_acceptance(self):
        self.report['accepted'] = True
        self.refused()

    def test_cannot_drop_native_contexts(self):
        self.report['summary']['closedContexts'] = 32
        self.refused()

    def test_cannot_hide_pixel_witness_failure(self):
        self.report['summary']['pixelWitnessMatches'] = 255
        self.refused()

    def test_cannot_replace_sizing_with_caller_frames(self):
        self.report['summary']['sizingQueriesPerBranch'] = 256
        self.refused()

    def test_cannot_call_mixed_queue_trace_normal_pointer_acceptance(self):
        self.report['normalPointerAcceptance'] = 'passed'
        self.refused()

    def test_cannot_call_content_view_capture_full_window_acceptance(self):
        self.report['menuShadowBackdropAcceptance'] = 'passed'
        self.refused()

    def test_cannot_change_reference(self):
        self.report['reference'] = 'different'
        self.refused()

    def test_cannot_rebaseline_existing_expectations(self):
        self.report['expectedImagesChanged'] = True
        self.refused()

    def test_cannot_approve_tolerance(self):
        self.report['tolerance'] = 'subpixel'
        self.refused()

    def test_cannot_hide_label_conversion_gate(self):
        self.report['remainingAcceptance'].remove('nativeLabelConversionAndBuilderTiming')
        self.refused()

    def test_cannot_claim_prebuilt_inputs_are_source_only(self):
        self.report['sourceOnlyArtifact']['prebuiltLibraryInputs'] = True
        self.refused()

    def test_cannot_claim_independent_machine_replay(self):
        self.report['sourceOnlyArtifact']['downloadAvailability'] = 'passed'
        self.refused()


if __name__ == '__main__':
    unittest.main()
