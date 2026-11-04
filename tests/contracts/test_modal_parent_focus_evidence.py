import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('modal_parent_focus', ROOT / 'scripts/verify-modal-parent-focus.py')
EVIDENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVIDENCE)


class ModalParentFocusEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.limits = json.loads((EVIDENCE.DIRECTORY / 'validation.json').read_text())
        records = json.loads((EVIDENCE.DIRECTORY / 'records.json').read_text())
        row = records['attempt5/proof/display/modal-wayland-software-scaled.json']
        cls.report = json.loads(gzip.decompress((EVIDENCE.DIRECTORY / row['stored']).read_bytes()))

    def test_captured_profiles_and_source_bindings_recompute(self):
        EVIDENCE.verify()

    def test_transient_keyboard_focus_cannot_count_as_parent_ready(self):
        value = copy.deepcopy(self.report)
        next(row for row in value['focusTransitions'] if row['phase'] == 'sheet-focus-negative-control')['parentKeyboardReady'] = True
        with self.assertRaises(AssertionError):
            EVIDENCE.focus_report(value)

    def test_parent_quick_focus_cannot_be_dropped(self):
        value = copy.deepcopy(self.report)
        next(row for row in value['focusTransitions'] if row['phase'] == 'before-parent-traversal')['parentRootActiveFocus'] = False
        with self.assertRaises(AssertionError):
            EVIDENCE.focus_report(value)

    def test_local_pass_cannot_promote_native_acceptance_or_failed_ci(self):
        for key in ['accepted', 'nativeFocusAccepted', 'nativeRasterAccepted', 'readerAccepted', 'priorX86SessionAccepted']:
            with self.subTest(key=key), self.assertRaises(AssertionError):
                EVIDENCE.limits(dict(self.limits, **{key: True}))
        with self.assertRaises(AssertionError):
            EVIDENCE.limits(dict(self.limits, priorLinuxConclusion='success'))


if __name__ == '__main__':
    unittest.main()
