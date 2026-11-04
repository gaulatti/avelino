import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('stepper_native_names', ROOT / 'scripts/verify-stepper-native-names.py')
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


class StepperNativeNamesEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = E.Capsule(E.DIRECTORY)
        cls.native = E.Capsule(E.NATIVE)
        cls.validation = json.loads((E.DIRECTORY / 'validation.json').read_text())

    def report(self):
        return self.runtime.record('reader1/output/operator-report.json')

    def log(self):
        return self.runtime.raw('reader1/output/orca-debug.log')

    def test_retained_native_and_linux_execution_domains_recompute(self):
        E.verify()

    def test_native_calls_must_match_the_original_responses(self):
        calls = self.native.record('native-cua-calls.json')
        calls[1]['payload']['call_id'] = 'wrong-call'
        with self.assertRaises(AssertionError):
            E.native_calls(calls, self.native.record('native-cua-responses.json'), {})

    def test_native_action_requests_cannot_be_replaced_by_static_values(self):
        states = {name: self.native.record(name + '-state.json') for name in ['add', 'remove', 'lower', 'outside']}
        states['add']['requests'] = []
        with self.assertRaises(AssertionError):
            E.native_calls(self.native.record('native-cua-calls.json'), self.native.record('native-cua-responses.json'), states)

    def test_native_speech_cannot_be_inferred_from_ax_observation(self):
        value = json.loads((E.NATIVE / 'provenance.json').read_text())
        value['nativeSpeechMeasured'] = True
        with self.assertRaises(AssertionError):
            E.native_provenance(value)

    def test_names_repair_cannot_change_the_paint_recipe(self):
        before = self.runtime.raw('source1/implementation/src/Avelino/BleeckerStepper.qml')
        after = self.runtime.raw('source2/implementation/src/Avelino/BleeckerStepper.qml')
        after = after.replace(b'BleeckerTheme.palette.card', b'BleeckerTheme.palette.background')
        with self.assertRaises(AssertionError):
            E.library_change(before, after)

    def test_historical_execution_cannot_be_relabelled_as_its_older_source(self):
        value = json.loads((E.DIRECTORY / 'runtime-binding.json').read_text())
        value['sourceParent'] = '601436f5cfb3551872ff1a397f606829cbfcba39'
        with mock.patch.object(E, 'PARENT', value['sourceParent']), self.assertRaises(AssertionError):
            E.binding(self.runtime, value)

    def test_separate_consumer_header_override_cannot_be_omitted(self):
        value = json.loads((E.DIRECTORY / 'runtime-binding.json').read_text())
        value['consumerOverridePaths'] = []
        with self.assertRaises(AssertionError):
            E.binding(self.runtime, value)

    def test_changed_runtime_requires_new_execution(self):
        executed = json.loads((E.DIRECTORY / 'runtime-binding.json').read_text())['files']
        current = copy.deepcopy(executed); current['src/Avelino/BleeckerStepper.qml'] = '0' * 64
        with self.assertRaises(AssertionError):
            E.candidate(current, executed)

    def test_inventory_snapshot_cannot_be_replaced_by_another_payload(self):
        value = json.loads((E.DIRECTORY / 'inventory-binding.json').read_text())
        value['candidateSha256'] = '0' * 64
        with self.assertRaises(AssertionError):
            E.inventory_snapshot(value)

    def test_another_library_cannot_reuse_reader_speech(self):
        installed = self.runtime.record('source2/package-producer.json')['installedFiles']
        value = self.runtime.record('reader1/controller/inputs.json')
        value['installedPrefixFiles']['lib/qml/Avelino/libAvelino.so'] = '0' * 64
        with self.assertRaises(AssertionError):
            E.package_inputs(value, installed)

    def test_reader_requires_the_native_name_in_actual_speech(self):
        with self.assertRaises(AssertionError):
            E.reader(self.report(), self.log().replace(b'Add', b'XXX'))

    def test_bound_button_cannot_be_enabled(self):
        value = self.runtime.record('reader1/output/lower-bound.json')
        E.buttons(value['tree'])['Remove']['states'].append('<enum ATSPI_STATE_ENABLED of type Atspi.StateType>')
        row = next(row for row in self.report()['phases'] if row['phase'] == 'lower-bound')
        with self.assertRaises(AssertionError):
            E.snapshot(value, row, value['targetPid'])

    def test_keyboard_action_must_retain_actual_button_focus(self):
        value = self.runtime.record('reader1/output/keyboard-increment.json')
        node = E.buttons(value['tree'])['Add']
        node['states'] = [item for item in node['states'] if 'ATSPI_STATE_FOCUSED ' not in item]
        row = next(row for row in self.report()['phases'] if row['phase'] == 'keyboard-increment')
        with self.assertRaises(AssertionError):
            E.snapshot(value, row, value['targetPid'])

    def test_consumer_must_match_native_binding_requests(self):
        value = self.runtime.record('consumer2/runtime/dpr1/report.json')
        value['nativeBehaviorTraces'][0]['requests'] = ['999']
        with self.assertRaises(AssertionError):
            E.consumer_report(value, 1)

    def test_consumer_cannot_acknowledge_an_uncaptured_session(self):
        value = self.runtime.record('consumer2/runtime/dpr1/capture-result.json')
        value['acknowledgedAfterActualSessionCapture'] = False
        with self.assertRaises(AssertionError):
            E.capture(value)

    def test_raw_image_differences_cannot_be_hidden_in_the_summary(self):
        value = self.runtime.record('visual/comparison.json')
        value['readerPairs'][0]['changedPixels'] = 1
        record = self.runtime.record
        with mock.patch.object(self.runtime, 'record', side_effect=lambda name: value if name == 'visual/comparison.json' else record(name)):
            with self.assertRaises(AssertionError):
                E.visual(self.runtime)

    def test_partial_checks_cannot_promote_acceptance_or_invent_reruns(self):
        keys = ['accepted', 'nativeReaderAccepted', 'numericSpeechAccepted', 'nativeRasterAccepted',
                'rawLinuxImagesAllExact', 'physicalInputAccepted', 'independentMachineAccepted',
                'fullQt58Rerun', 'consumerLibraryBuildRerun', 'expectedImagesChanged']
        for key in keys:
            value = copy.deepcopy(self.validation); value[key] = True
            with self.subTest(key=key), self.assertRaises(AssertionError):
                E.limits(value)


if __name__ == '__main__':
    unittest.main()
