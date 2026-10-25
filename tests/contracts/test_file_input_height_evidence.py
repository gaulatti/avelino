import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('file_height_evidence', ROOT / 'scripts/verify-file-input-height.py')
E = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(E)


class FileInputHeightEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capsule = E.Capsule(E.DIRECTORY)
        cls.validation = json.loads((E.DIRECTORY / 'validation.json').read_text())
        cls.runtime = json.loads((E.DIRECTORY / 'runtime-binding.json').read_text())
        cls.historical = json.loads(E.OLD.HISTORY.git_files(E.PARENT, ['tests/consumer/native-file-input-witnesses.json'])['tests/consumer/native-file-input-witnesses.json'])

    def report(self):
        return self.capsule.record('runtime/output/file-input-dpr1/report.json')

    def test_complete_historical_audit_does_not_freeze_future_candidate(self):
        with mock.patch.object(E, 'candidate', side_effect=AssertionError('Historical audit inspected future runtime')):
            E.verify()

    def test_observe_mode_cannot_promote_native_or_physical_acceptance(self):
        for name in ['accepted', 'nativeReaderAccepted', 'physicalInputAccepted', 'physicalGpuAccepted', 'independentMachineAccepted', 'expectedImagesChanged']:
            value = copy.deepcopy(self.validation); value[name] = True
            with self.subTest(name=name), self.assertRaises(AssertionError): E.limits(value)

    def test_strict_pixels_cannot_gain_tolerance_masks_or_exceptions(self):
        for name, changed in [('pixelTolerance', 1), ('masks', ['border']), ('approvedExceptions', ['raster'])]:
            value = copy.deepcopy(self.validation); value[name] = changed
            with self.subTest(name=name), self.assertRaises(AssertionError): E.limits(value)

    def test_partial_component_or_session_results_cannot_pass(self):
        for name, changed in [('uiChecksEachDpr', 61), ('componentChecks', [5910, 6137]), ('runtimeProfiles', 21), ('nativeSizingResponses', 10367)]:
            value = copy.deepcopy(self.validation); value[name] = changed
            with self.subTest(name=name), self.assertRaises(AssertionError): E.limits(value)

    def test_executed_candidate_requires_exact_runtime_inputs(self):
        value = dict(self.runtime['files']); value['src/Avelino/buttonlabel.cpp'] = '0' * 64
        with self.assertRaises(AssertionError): E.candidate(value, self.runtime['files'])

    def test_consumer_override_must_remain_explicit(self):
        value = copy.deepcopy(self.runtime); value['consumerOverridePaths'] = []
        with self.assertRaises(AssertionError): E.binding(self.capsule, value)

    def test_wrong_historical_parent_cannot_reuse_run(self):
        value = copy.deepcopy(self.runtime); value['sourceParent'] = 'b93899f4a0b4381db0514ed8da230f1c0c837069'
        with self.assertRaises(AssertionError): E.binding(self.capsule, value)

    def test_direct_proposals_require_all_native_offers_in_order(self):
        value = self.report(); value['sizing'][0]['observations'].reverse()
        with self.assertRaises(AssertionError): E.proposals(value, self.historical)

    def test_native_expected_values_cannot_be_replaced(self):
        value = self.report(); value['sizing'][0]['nativeProposals']['zero']['height'] = 187
        with self.assertRaises(AssertionError): E.proposals(value, self.historical)

    def test_actual_proposal_cannot_be_copied_from_native_and_relabelled(self):
        value = self.report()
        row = next(x for x in value['sizing'] if x['matched'] < 15)
        observation = next(x for x in row['observations'] if not x['match'])
        observation['actual'] = copy.deepcopy(observation['native'])
        with self.assertRaises(AssertionError): E.proposals(value, self.historical)

    def test_retained_failure_cannot_be_relabelled_passed(self):
        value = self.report(); value['nativeDirectProposalComparisonStatus'] = 'passed'
        with self.assertRaises(AssertionError): E.proposals(value, self.historical)

    def test_proposals_cannot_keep_caller_or_parent_frame(self):
        for name in ['callerFrameOmitted', 'retainedControlSequence']:
            value = self.report(); value['sizing'][0][name] = False
            with self.subTest(name=name), self.assertRaises(AssertionError): E.proposals(value, self.historical)

    def test_infinite_dimension_adapter_cannot_become_finite(self):
        value = self.report(); value['sizing'][0]['observations'][-1]['qtOffer']['height'] = 300
        with self.assertRaises(AssertionError): E.proposals(value, self.historical)

    def test_capture_needs_actual_session_before_acknowledgement(self):
        value = self.capsule.record('runtime/output/file-input-dpr1/capture-result.json')
        value['acknowledgedAfterActualSessionCapture'] = False
        with self.assertRaises(AssertionError): E.capture(value)

    def test_source_free_run_cannot_mount_build_tree(self):
        value = self.capsule.record('runtime/output/file-input-dpr1/capture-result.json')
        value['consumerBuildMounted'] = True
        with self.assertRaises(AssertionError): E.capture(value)

    def test_session_requires_the_executed_consumer_and_installed_module(self):
        for name in ['consumerSha256', 'installedLibrarySha256']:
            value = self.capsule.record('runtime/output/file-input-dpr1/capture-result.json'); value[name] = '0' * 64
            with self.subTest(name=name), self.assertRaises(AssertionError): E.capture(value)

    def test_session_placeholder_is_not_display_evidence(self):
        raw = io.BytesIO(); Image.new('RGB', (2560, 1920), 'black').save(raw, format='PNG')
        with self.assertRaises(AssertionError): E.OLD.capture_image(raw.getvalue())

    def test_raster_failure_is_recomputed_from_unedited_images(self):
        value = json.loads((E.DIRECTORY / 'raster-comparison.json').read_text())['rows'][0]
        value['differentPixels'] = 0; value['exact'] = True
        with self.assertRaises(AssertionError): E.raster_row(self.capsule, value)

    def test_raster_pair_cannot_substitute_another_capture(self):
        value = json.loads((E.DIRECTORY / 'raster-comparison.json').read_text())['rows'][0]
        value['qtRecord'] = value['nativeRecord']
        with self.assertRaises(AssertionError): E.raster_row(self.capsule, value)


if __name__ == '__main__':
    unittest.main()
