"""Prevent source observations from being presented as Linux acceptance."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('spotlight_source', ROOT / 'scripts/verify-command-spotlight-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class CommandSpotlightSource(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((source.DIRECTORY / 'investigation.json').read_text())

    def refused(self):
        with self.assertRaises(AssertionError):
            source.validate_report(self.report)

    def test_cannot_claim_linux_acceptance(self):
        self.report['accepted'] = True
        self.refused()

    def test_cannot_drop_native_contexts(self):
        self.report['summary']['closedContexts'] = 32
        self.refused()

    def test_cannot_hide_a_native_state_witness_failure(self):
        self.report['summary']['historyStateWitnessMatches'] = 1535
        self.refused()

    def test_cannot_call_retained_caller_state_a_restore_pixel_match(self):
        self.report['summary']['retainedRestorePixelMatches'] = 64
        self.refused()

    def test_cannot_drop_local_key_attempts(self):
        self.report['summary']['publicKeyAttempts'] = 64
        self.refused()

    def test_cannot_omit_large_retained_list(self):
        self.report['summary']['historyDefinitions'] = 7
        self.refused()

    def test_cannot_replace_fixed_size_proposals_with_caller_frames(self):
        self.report['summary']['sizingQueriesPerBranch'] = 256
        self.refused()

    def test_cannot_add_tolerance(self):
        self.report['tolerance'] = 'subpixel'
        self.refused()

    def test_cannot_rebaseline_expected_images(self):
        self.report['expectedImagesChanged'] = True
        self.refused()

    def test_cannot_claim_independent_machine_replay(self):
        self.report['sourceOnlyArtifact']['downloadAvailability'] = 'passed'
        self.refused()

    def test_cannot_hide_native_lazy_state_gate(self):
        self.report['remainingAcceptance'].remove('nativeLazyRowRetentionAndMeasurement')
        self.refused()

    def test_cannot_change_reference(self):
        self.report['reference'] = 'different'
        self.refused()


if __name__ == '__main__':
    unittest.main()
