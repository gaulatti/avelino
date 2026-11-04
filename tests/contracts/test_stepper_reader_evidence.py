import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('stepper_reader', ROOT / 'scripts/verify-stepper-reader.py')
EVIDENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


class StepperReaderEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capsule = EVIDENCE.Capsule(EVIDENCE.DIRECTORY)
        cls.validation = json.loads((EVIDENCE.DIRECTORY / 'validation.json').read_text())

    def report(self):
        return self.capsule.record('reader2/output/operator-report.json')

    def log(self):
        return self.capsule.raw('reader2/output/orca-debug.log')

    def test_retained_reader_results_and_gap_recompute(self):
        EVIDENCE.verify()

    def test_reader_must_prove_named_speech_in_its_phase(self):
        with self.assertRaises(AssertionError):
            EVIDENCE.reader(self.report(), b'')

    def test_assistive_increment_cannot_keep_the_old_value(self):
        value = self.report()
        next(row for row in value['phases'] if row['phase'] == 'assistive-increment')['observations']['value'] = '2'
        with self.assertRaises(AssertionError):
            EVIDENCE.reader(value, self.log())

    def test_outside_field_must_receive_actual_keyboard_text(self):
        value = self.report(); value['phases'][-1]['observations']['text'] = ''
        with self.assertRaises(AssertionError):
            EVIDENCE.reader(value, self.log())

    def test_bound_button_cannot_remain_enabled(self):
        value = self.capsule.record('reader2/output/lower-bound.json')
        button = EVIDENCE.named(value['tree'], 'Decrease Quantity', 'push button')
        button['states'].append('<enum ATSPI_STATE_ENABLED of type Atspi.StateType>')
        row = next(row for row in self.report()['phases'] if row['phase'] == 'lower-bound')
        with self.assertRaises(AssertionError):
            EVIDENCE.snapshot(value, row, value['targetPid'])

    def test_tree_value_must_match_owner_observation(self):
        value = self.capsule.record('reader2/output/assistive-increment.json')
        node = EVIDENCE.named(value['tree'], '3', 'label'); node['name'] = '2'
        row = next(row for row in self.report()['phases'] if row['phase'] == 'assistive-increment')
        with self.assertRaises(AssertionError):
            EVIDENCE.snapshot(value, row, value['targetPid'])

    def test_keyboard_action_requires_focused_button(self):
        value = self.capsule.record('reader2/output/keyboard-increment.json')
        node = EVIDENCE.named(value['tree'], 'Increase Quantity', 'push button')
        node['states'] = [item for item in node['states'] if 'ATSPI_STATE_FOCUSED ' not in item]
        row = next(row for row in self.report()['phases'] if row['phase'] == 'keyboard-increment')
        with self.assertRaises(AssertionError):
            EVIDENCE.snapshot(value, row, value['targetPid'])

    def test_another_package_cannot_reuse_reader_evidence(self):
        value = self.capsule.record('reader2/controller/inputs.json')
        installed = copy.deepcopy(value['installedPrefixFiles'])
        value['installedPrefixFiles']['lib/qml/Avelino/libAvelino.so'] = '0' * 64
        with self.assertRaises(AssertionError):
            EVIDENCE.inputs(value, installed)

    def test_source_mount_cannot_be_claimed_as_source_free(self):
        value = self.capsule.record('reader2/controller/inputs.json')
        value['command'].extend(['--mount', 'type=bind,source=/code,target=/work,readonly'])
        with self.assertRaises(AssertionError):
            EVIDENCE.inputs(value, value['installedPrefixFiles'])

    def test_historical_runtime_cannot_be_assigned_to_parent(self):
        value = json.loads((EVIDENCE.DIRECTORY / 'runtime-binding.json').read_text())
        value['sourceCommit'] = '601436f5cfb3551872ff1a397f606829cbfcba39'
        files = self.capsule.record('reader2/output/producer-inputs.json')['sourceFiles']
        with mock.patch.object(EVIDENCE, 'SOURCE', value['sourceCommit']), self.assertRaises(AssertionError):
            EVIDENCE.producer_binding(value, files)

    def test_new_utterance_cannot_be_hidden_by_the_gap_summary(self):
        log = bytearray(self.log()); report = self.report()
        start = next(row for row in report['phases'] if row['phase'] == 'assistive-increment')['readerLogBytes']
        log[start:start + 14] = b'SPEECH OUTPUT:'
        with self.assertRaises(AssertionError):
            EVIDENCE.speech_gap(report, bytes(log))

    def test_observations_cannot_promote_acceptance_or_claim_new_suite(self):
        keys = ['accepted', 'applicationSourcesChanged', 'qtSuiteRerunForThisEvidence',
                'nativeRasterAccepted', 'nativeGeometryAccepted', 'nativeReaderAccepted',
                'physicalInputAccepted', 'independentMachineAccepted',
                'numericValueSpeechAccepted', 'numericValueSpeechObservedInActionWindows', 'expectedImagesChanged']
        for key in keys:
            value = copy.deepcopy(self.validation); value[key] = True
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.limits(value)


if __name__ == '__main__':
    unittest.main()
