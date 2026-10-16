import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('modal_source', ROOT / 'scripts/verify-modal-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class ModalSourceContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / 'source'
        shutil.copytree(source.DIRECTORY, self.directory)

    def edit(self, name, mutate):
        path = self.directory / name
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value, indent=2) + '\n')
        if name == 'investigation.json':
            return
        manifest = self.directory / 'investigation.json'
        report = json.loads(manifest.read_text())
        report['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        for prefix, report_name, hash_key in [('captures/', 'capture-continuity.json', 'currentSha256'),
                                              (('captures/', 'behavior/'), 'clean-replay.json', 'replaySha256')]:
            if name.startswith(prefix):
                report_path = self.directory / report_name
                data = json.loads(report_path.read_text())
                row = next(r for r in data['outputs'] if r['file'] == name)
                row['originalSha256'] = row[hash_key] = report['files'][name]
                report_path.write_text(json.dumps(data, indent=2) + '\n')
                report['files'][report_name] = hashlib.sha256(report_path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(report, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            source.verify(self.directory)

    def test_complete_native_corpus(self):
        self.assertEqual(source.verify(self.directory), dict(captures=288, behaviorTraces=14,
                                                           behaviorSnapshots=60, replayFiles=977, accepted=False))

    def test_native_measurements_cannot_approve_linux(self):
        self.edit('investigation.json', lambda d: d.update(accepted=True))
        self.rejected()

    def test_missing_display_context_is_rejected(self):
        self.edit('captures/captures.json', lambda d: d['captures'].pop())
        self.rejected()

    def test_duplicate_context_is_rejected(self):
        self.edit('captures/captures.json', lambda d: d['captures'].__setitem__(1, d['captures'][0]))
        self.rejected()

    def test_empty_and_zero_content_cannot_be_collapsed(self):
        def collapse(data):
            row = next(r for r in data['captures'] if r['configuration']['fixture'] == 'content-zero')
            for key in ['probed', 'witness']:
                row[key]['parts']['root']['height'] -= 40
        self.edit('captures/captures.json', collapse)
        self.rejected()

    def test_sheet_close_must_update_parent_presentation(self):
        def retain(data):
            trace = next(t for t in data['traces'] if t['id'] == 'sheet-close')
            trace['events'][-1]['state'].update(presented=True, sheetCount=1, sheetDismissCount=0)
        self.edit('behavior/behavior.json', retain)
        self.rejected()

    def test_disabled_close_cannot_dismiss_sheet(self):
        def close(data):
            trace = next(t for t in data['traces'] if t['id'] == 'sheet-disabled-close')
            trace['events'][-1]['state'].update(presented=False, sheetCount=0, sheetDismissCount=1)
        self.edit('behavior/behavior.json', close)
        self.rejected()

    def test_visible_remount_must_activate_fresh_counter(self):
        def suppress(data):
            trace = next(t for t in data['traces'] if t['id'] == 'counter-lifecycle')
            trace['events'][-1]['state']['calls'].pop()
        self.edit('behavior/behavior.json', suppress)
        self.rejected()

    def test_retained_content_does_not_mean_window_stays_open(self):
        def retain(data):
            trace = next(t for t in data['traces'] if t['id'] == 'ordinary')
            trace['events'][-1]['state']['windowVisible'] = True
        self.edit('behavior/behavior.json', retain)
        self.rejected()

    def test_content_state_must_reset_at_mount_boundary(self):
        def retain(data):
            trace = next(t for t in data['traces'] if t['id'] == 'counter-lifecycle')
            trace['events'][-1]['state']['mountValues'][-1] = 3
        self.edit('behavior/behavior.json', retain)
        self.rejected()

    def test_inactive_ax_root_cannot_establish_reader_acceptance(self):
        self.edit('investigation.json', lambda d: d.update(screenReaderAcceptance='passed'))
        self.rejected()

    def test_input_after_dismissal_cannot_establish_remount_behavior(self):
        self.edit('investigation.json', lambda d: d.update(postDismissalInputEvidence='accepted'))
        self.rejected()

    def test_prebuilt_inputs_are_rejected(self):
        self.edit('tooling-provenance.json', lambda d: d.update(compiledInputs=['Sabella.o']))
        self.rejected()

    def test_complete_replay_is_required(self):
        self.edit('clean-replay.json', lambda d: d['outputs'].pop())
        self.rejected()

    def test_unsealed_files_are_rejected(self):
        (self.directory / 'unexpected.json').write_text('{}\n')
        self.rejected()


if __name__ == '__main__':
    unittest.main()
