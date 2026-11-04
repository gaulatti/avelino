"""Exercise the real display validator against the recorded installed consumers."""
import ast
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('display_file_input_history', ROOT / 'scripts/verify-path-assistive-lifetime.py')
H = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(H)


class FileInputDisplayContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = (ROOT / 'scripts/check-display-sessions.sh').read_text()
        marker = 'python3 - "$prefix" "$protocol" "$backend" "$configuration" "$fixture" <<\'PY\'\n'
        python = script.split(marker, 1)[1].split('\nPY', 1)[0]
        parsed = ast.parse(python)
        branch = next(n for n in ast.walk(parsed) if isinstance(n, ast.If) and ast.unparse(n.test) == "fixture == 'file-input'")
        cls.validation = compile(ast.Module(body=branch.body, type_ignores=[]), 'check-display-sessions.sh:file-input', 'exec')
        cls.current = H.Capsule(ROOT / 'evidence/development/file-input-height-20261024')
        cls.prior = H.Capsule(ROOT / 'evidence/development/path-assistive-lifetime-20261024')

    def report(self):
        return self.current.record('runtime/output/file-input-dpr1/report.json')

    def validate(self, record):
        exec(self.validation, {'record': record})

    def test_all_fourteen_actual_height_file_input_profiles_pass_the_validator(self):
        reports = [n for n in self.current.records if n.endswith('/report.json') and n.startswith(('runtime/output/', 'display/output/', 'canonical/output/'))]
        count = 0
        for name in reports:
            value = self.current.record(name)
            if value['fixture'] == 'file-input':
                with self.subTest(report=name): self.validate(value)
                count += 1
        self.assertEqual(count, 14)

    def test_pre_height_published_consumer_also_passes(self):
        for dpr in [1, 2]:
            self.validate(self.prior.record(f'consumer-runtime/output/file-input-dpr{dpr}/report.json'))

    def test_old_thirty_action_contract_is_incomplete(self):
        value = self.report(); value['actions'] = value['actions'][:-2]
        with self.assertRaises(AssertionError): self.validate(value)

    def test_old_key_event_count_is_incomplete(self):
        value = self.report(); value['keyEvents'] = 164
        with self.assertRaises(AssertionError): self.validate(value)

    def test_action_count_cannot_hide_missing_edit_phase(self):
        value = self.report()
        next(a for a in value['actions'] if a['phase'] == 'go-to-assistive-edit-undo-redo')['phase'] = 'unrelated'
        with self.assertRaises(AssertionError): self.validate(value)

    def test_destruction_callback_must_actually_destroy_once(self):
        value = self.report(); value['assistiveLifetime'][0]['destroyed'] = 0
        with self.assertRaises(AssertionError): self.validate(value)

    def test_vetoed_replacement_cannot_emit_an_edit(self):
        value = self.report(); value['assistiveSelectionCallbacks'][0]['editNotifications'] = 1
        with self.assertRaises(AssertionError): self.validate(value)

    def test_editing_cannot_deliver_an_owner_result(self):
        value = self.report(); value['assistiveEditing']['ownerResults'] = 1
        with self.assertRaises(AssertionError): self.validate(value)

    def test_native_or_physical_acceptance_cannot_be_promoted(self):
        for key in ['accepted', 'nativeRasterAcceptance', 'physicalInputAcceptance', 'readerAcceptance']:
            value = self.report(); value[key] = True if key == 'accepted' else 'passed'
            with self.subTest(key=key), self.assertRaises(AssertionError): self.validate(value)


if __name__ == '__main__':
    unittest.main()
