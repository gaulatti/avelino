import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('path_assistive_lifetime', ROOT / 'scripts/verify-path-assistive-lifetime.py')
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


class PathAssistiveLifetimeEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capsule = E.Capsule(E.DIRECTORY)
        cls.validation = json.loads((E.DIRECTORY / 'validation.json').read_text())
        cls.runtime = json.loads((E.DIRECTORY / 'runtime-binding.json').read_text())

    def report(self, fixture='file-input'):
        return self.capsule.record('consumer-runtime/output/' + fixture + '-dpr1/report.json')

    def test_complete_retained_execution_does_not_freeze_future_candidates(self):
        with mock.patch.object(E, 'candidate', side_effect=AssertionError('Historical audit must not inspect a future candidate')):
            E.verify()

    def test_partial_qt_run_cannot_be_relabelled_as_the_full_suite(self):
        value = copy.deepcopy(self.validation); value['fullQt58Rerun'] = True
        with self.assertRaises(AssertionError): E.limits(value)

    def test_native_or_physical_acceptance_cannot_be_inferred(self):
        for key in ['accepted', 'nativeReaderAccepted', 'nativeRasterAccepted', 'physicalInputAccepted', 'physicalListeningAccepted', 'independentMachineAccepted']:
            with self.subTest(key=key):
                value = copy.deepcopy(self.validation); value[key] = True
                with self.assertRaises(AssertionError): E.limits(value)

    def test_recorded_crash_needs_both_signal_and_failing_application_exit(self):
        log = self.capsule.raw('source3/controller/path-assistive-destruction.log').decode()
        with self.assertRaises(AssertionError): E.crash(log, 0)
        with self.assertRaises(AssertionError): E.crash(log.replace('Received signal 11 (SIGSEGV)', 'environment failure'), 139)

    def test_partial_or_failed_qt_output_cannot_pass(self):
        log = self.capsule.raw('validation/file-input-ui-dpr1.log').decode()
        with self.assertRaises(AssertionError): E.qt_log(log.replace('38 passed, 0 failed', '37 passed, 1 failed'), 'FileInputUiTests', 38)

    def test_date_wrapper_move_cannot_change_undo_history_or_geometry(self):
        before = self.capsule.raw('source3/implementation/src/Avelino/daterangeinput.cpp').decode()
        after = self.capsule.raw('source4/implementation/src/Avelino/daterangeinput.cpp').decode()
        header = self.capsule.raw('source4/implementation/src/Avelino/assistivetextinput_p.h').decode()
        with self.assertRaises(AssertionError): E.helper_move(before, after, header.replace('->m_undoState)', '->m_undoState++)'))
        with self.assertRaises(AssertionError): E.helper_move(before, after.replace('return input->positionAt(', 'return 1+input->positionAt('), header)

    def test_separately_compiled_consumer_overrides_must_be_explicit(self):
        value = copy.deepcopy(self.runtime); value['consumerOverridePaths'] = []
        with self.assertRaises(AssertionError): E.binding(self.capsule, value)

    def test_new_private_source_cannot_be_omitted_from_runtime(self):
        value = copy.deepcopy(self.runtime); value['files'].pop('tests/consumer/pathinputobserver.h')
        with self.assertRaises(AssertionError): E.binding(self.capsule, value)

    def test_different_historical_parent_cannot_reuse_execution(self):
        value = copy.deepcopy(self.runtime); value['sourceParent'] = 'cc1047e29eac2ec4ee3e8d0a18f92ec68b6f23bc'
        with self.assertRaises(AssertionError): E.binding(self.capsule, value)

    def test_changed_runtime_needs_new_execution(self):
        value = copy.deepcopy(self.runtime['files']); value['src/Avelino/filechooserpathinput.cpp'] = '0' * 64
        with self.assertRaises(AssertionError): E.candidate(value, self.runtime['files'])

    def test_inventory_snapshot_needs_the_actual_retained_blob(self):
        value = json.loads((E.DIRECTORY / 'inventory-binding.json').read_text()); value['candidateSha256'] = '0' * 64
        with self.assertRaises(AssertionError): E.inventory_snapshot(value)

    def test_reader_or_consumer_cannot_use_a_different_installed_library(self):
        value = self.capsule.record('consumer-runtime/controller/inputs.json')
        installed = self.capsule.record('package1/controller/result.json')['installedFiles']
        value['installedFiles']['lib/qml/Avelino/libAvelino.so'] = '0' * 64
        with self.assertRaises(AssertionError): E.package_inputs(value, installed)

    def test_source_free_claim_cannot_include_the_build_tree(self):
        value = self.capsule.record('consumer-runtime/controller/inputs.json'); value['consumerBuildMounted'] = True
        installed = self.capsule.record('package1/controller/result.json')['installedFiles']
        with self.assertRaises(AssertionError): E.package_inputs(value, installed)

    def test_lost_destruction_callback_cannot_pass_the_installed_consumer(self):
        value = self.report(); value['assistiveLifetime'][0]['destroyed'] = 0
        with self.assertRaises(AssertionError): E.consumer_report(value, 'file-input', 1)

    def test_stale_replacement_cannot_emit_an_edit(self):
        value = self.report(); value['assistiveSelectionCallbacks'][0]['editNotifications'] = 1
        with self.assertRaises(AssertionError): E.consumer_report(value, 'file-input', 1)

    def test_retained_native_frame_failure_cannot_be_promoted(self):
        value = self.report(); value['nativeFrameComparisonStatus'] = 'passed'
        with self.assertRaises(AssertionError): E.consumer_report(value, 'file-input', 1)

    def test_date_consumer_must_cover_both_endpoints_and_all_owners(self):
        value = self.report('date-range'); value['assistiveInput'][0] = copy.deepcopy(value['assistiveInput'][1])
        with self.assertRaises(AssertionError): E.consumer_report(value, 'date-range', 1)

    def test_capture_acknowledgement_needs_a_real_completed_capture(self):
        value = self.capsule.record('consumer-runtime/output/file-input-dpr1/capture-result.json')
        module = self.capsule.record('package1/controller/result.json')['installedFiles']['lib/qml/Avelino/libAvelino.so']
        value['acknowledgedAfterActualSessionCapture'] = False
        with self.assertRaises(AssertionError): E.capture_result(value, module)

    def test_blank_placeholder_is_not_a_full_session_capture(self):
        raw = io.BytesIO(); Image.new('RGB', (2560, 1920), 'black').save(raw, format='PNG')
        with self.assertRaises(AssertionError): E.capture_image(raw.getvalue())

    def test_reader_profile_and_editable_interface_cannot_be_relabelled(self):
        value = self.capsule.record('readers/goto1/output/operator-controls-v1/result.json')
        session = self.capsule.record('readers/goto1/output/session-result.json')
        profile = copy.deepcopy(session['profile']); profile['scaled'] = True
        with self.assertRaises(AssertionError): E.reader_report(value, 'goto', profile, session)
        value['directAssistiveTextEdit'] = 'unsupported'
        with self.assertRaises(AssertionError): E.reader_report(value, 'goto', session['profile'], session)


if __name__ == '__main__':
    unittest.main()
