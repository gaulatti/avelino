import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('tooltip_source', ROOT / 'scripts/verify-tooltip-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class TooltipSourceContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / 'source'
        shutil.copytree(source.DIRECTORY, self.directory)

    def edit(self, name, mutate):
        path = self.directory / name
        data = json.loads(path.read_text())
        mutate(data)
        path.write_text(json.dumps(data, indent=2) + '\n')
        if name == 'investigation.json':
            return
        manifest = self.directory / 'investigation.json'
        report = json.loads(manifest.read_text())
        report['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        # Refresh hashes to prove the verifier checks the observations as well.
        if name.startswith('closed/'):
            replay_path = self.directory / 'clean-replay.json'
            replay = json.loads(replay_path.read_text())
            row = next(r for r in replay['outputs'] if r['file'] == name.removeprefix('closed/'))
            row['originalSha256'] = row['replaySha256'] = report['files'][name]
            replay_path.write_text(json.dumps(replay, indent=2) + '\n')
            report['files']['clean-replay.json'] = hashlib.sha256(replay_path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(report, indent=2) + '\n')

    def rejected(self):
        with self.assertRaises(AssertionError):
            source.verify(self.directory)

    def test_complete_source_corpus(self):
        self.assertEqual(source.verify(self.directory), dict(closedCases=168, closedReplayFiles=673,
                                                           nativePanelCases=1, accepted=False))

    def test_source_cannot_accept_linux(self):
        self.edit('investigation.json', lambda d: d.update(accepted=True))
        self.rejected()

    def test_missing_profile(self):
        self.edit('closed/captures.json', lambda d: d['captures'].pop())
        self.rejected()

    def test_duplicate_profile(self):
        self.edit('closed/captures.json', lambda d: d['captures'].__setitem__(1, d['captures'][0]))
        self.rejected()

    def test_wrapper_cannot_add_padding(self):
        def padded(d):
            for state in d['captures'][0]['states'][1:3]:
                state['parts']['root']['width'] += 2
        self.edit('closed/captures.json', padded)
        self.rejected()

    def test_closed_identity_cannot_establish_popup_acceptance(self):
        self.edit('investigation.json', lambda d: d.update(nativePopupAcceptance='passed'))
        self.rejected()

    def test_prebuilt_inputs_rejected(self):
        self.edit('tooling-provenance.json', lambda d: d.update(compiledInputs=['Sabella.o']))
        self.rejected()

    def test_incomplete_replay_rejected(self):
        self.edit('clean-replay.json', lambda d: d['outputs'].pop())
        self.rejected()

    def test_hint_update_cannot_reset_caller(self):
        self.edit('native-v1/hint-update.json', lambda d: d.update(afterCount=0))
        self.rejected()

    def test_sharing_indicator_is_not_tooltip(self):
        def sharing(d):
            next(w for w in d['windows'] if w['class'] == 'NSToolTipPanel')['class'] = 'NSLocalWindowSharingWindow'
        self.edit('native-v2/state-after-live-hint-capture.json', sharing)
        self.rejected()

    def test_missing_real_entry_rejected(self):
        self.edit('native-v2/state-before-live-hint.json', lambda d: d.update(mouseEvents=[]))
        self.rejected()

    def test_popup_rebuild_cannot_claim_pixel_replay(self):
        self.edit('active-clean-build/source-build-result.json', lambda d: d.update(automaticPixelReplay=True))
        self.rejected()

    def test_inactive_diagnostic_cannot_be_accepted(self):
        self.edit('diagnostics/popup-v4/classification.json', lambda d: d.update(nativePopupAcceptance='passed'))
        self.rejected()

    def test_unsealed_file_rejected(self):
        (self.directory / 'unexpected.json').write_text('{}\n')
        self.rejected()


if __name__ == '__main__':
    unittest.main()
