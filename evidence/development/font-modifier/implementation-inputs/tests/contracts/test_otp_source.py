import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('otp_source', ROOT / 'scripts/verify-otp-source.py')
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


class OTPSourceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='avelino-otp-source-')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'evidence'
        shutil.copytree(verifier.DIRECTORY, self.directory)

    def change(self, name, mutation):
        path = self.directory / name
        data = json.loads(path.read_text())
        mutation(data)
        path.write_text(json.dumps(data, indent=2) + '\n')
        manifest = self.directory / 'investigation.json'
        report = json.loads(manifest.read_text())
        report['files'][name] = verifier.digest(path)
        manifest.write_text(json.dumps(report, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)

    def test_source_replay_and_public_corpus_are_intact(self):
        self.assertEqual(verifier.verify(self.directory)['cleanReplayIdenticalFiles'], 897)

    def test_duplicate_capture_cannot_replace_a_missing_context(self):
        self.change('captures/captures.json', lambda d: d['captures'].__setitem__(0, d['captures'][1]))
        self.rejected()

    def test_constructor_getter_cannot_sanitize_caller_code(self):
        def mutate(data):
            row = next(r for r in data['captures'] if r['fixture'] == 'unfiltered-initial')
            row['native']['code'] = '123'
        self.change('captures/captures.json', mutate)
        self.rejected()

    def test_placeholder_cannot_use_a_different_length(self):
        self.change('captures/captures.json', lambda d: next(r for r in d['captures'] if r['fixture'] == 'default-length')['native'].__setitem__('placeholder', '•••••'))
        self.rejected()

    def test_inherited_font_cannot_replace_explicit_monospace_20(self):
        self.change('captures/captures.json', lambda d: next(r for r in d['captures'] if r['fixture'] == 'parent-font32')['native'].__setitem__('fontPointSize', 32))
        self.rejected()

    def test_han_numeric_values_cannot_be_replaced_with_ascii_letters(self):
        def mutate(data):
            data['singleScalarNumbers'].remove(0x4e00)
            data['singleScalarNumbers'].append(0x41)
        self.change('native-otp-semantics.json', mutate)
        self.rejected()

    def test_attached_marks_cannot_be_discarded(self):
        def mutate(data):
            row = next(r for r in data['markContexts'] if r['base'] == 49 and r['mark'] == 0x900)
            row['filteredScalars'] = [49, 50]
        self.change('native-otp-graphemes.json', mutate)
        self.rejected()

    def test_native_boundary_differences_cannot_be_replaced_with_unicode17(self):
        def mutate(data):
            expected = json.loads((self.directory / 'grapheme-inputs.json').read_text())['cases']
            for row in data['officialTests']:
                row['boundaries'] = expected[row['index']]['boundaries']
                row['matchesOfficial'] = True
        self.change('native-otp-graphemes.json', mutate)
        self.rejected()

    def test_original_qt_failure_cannot_be_replaced_with_a_passing_projection(self):
        self.change('qt-probe/qt-otp-semantics.json', lambda d: d['summary'].__setitem__('numericScalarDifferences', 0))
        self.rejected()

    def test_rendered_editing_value_cannot_be_conflated_with_filtered_model(self):
        def mutate(data):
            trace = next(r for r in data['traces'] if r['bindingMode'] == 'projected-state' and r['fixture'] == 'empty')
            state = next(r for r in trace['events'] if r['action'] == 'insert-settled')['state']
            state['fieldValue'] = state['code']
        self.change('state-bindings/state-bindings.json', mutate)
        self.rejected()

    def test_native_large_insertion_cannot_inherit_qt_default_limit(self):
        def mutate(data):
            trace = next(r for r in data['traces'] if r['fixture'] == 'large-insert')
            next(r for r in trace['steps'] if r['action'] == 'insert-40001')['state']['fieldValue'] = 'a' * 32767
        self.change('edges/edges.json', mutate)
        self.rejected()

    def test_composition_cannot_commit_before_unmark(self):
        def mutate(data):
            trace = next(r for r in data['traces'] if r['fixture'] == 'marked-text')
            next(r for r in trace['steps'] if r['action'] == 'mark-two')['state']['code'] = '一二'
        self.change('edges/edges.json', mutate)
        self.rejected()

    def test_compiled_product_cannot_replace_a_fresh_source_input(self):
        self.change('tooling-provenance.json', lambda d: d.__setitem__('compiledInputs', ['Sabella.o']))
        self.rejected()

    def test_changed_replay_cannot_be_declared_identical(self):
        self.change('clean-replay-comparison.json', lambda d: d['files'][0].__setitem__('identical', False))
        self.rejected()

    def test_source_investigation_cannot_approve_linux_parity(self):
        path = self.directory / 'investigation.json'
        data = json.loads(path.read_text());data['accepted'] = True
        path.write_text(json.dumps(data))
        self.rejected()


if __name__ == '__main__':
    unittest.main()
