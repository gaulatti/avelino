"""Reject incomplete, ineffective or self-approved native pill evidence."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('pill_modifier_source', ROOT / 'scripts/verify-pill-modifier-source.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class PillModifierSourceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name) / 'candidate'
        shutil.copytree(source.DIRECTORY, self.directory, copy_function=os.link)
        self.report = json.loads((self.directory / 'investigation.json').read_text())

    def tearDown(self):
        self.temporary.cleanup()

    def replace(self, name, data):
        # Break the test hardlink before writing; canonical evidence stays untouched.
        path = self.directory / name
        path.unlink()
        path.write_bytes(data)

    def save(self):
        self.replace('investigation.json', json.dumps(self.report).encode())

    def update(self, name, value):
        self.replace(name, json.dumps(value).encode())
        self.report['files'][name] = hashlib.sha256((self.directory / name).read_bytes()).hexdigest()
        self.save()

    def refused(self):
        with self.assertRaises((AssertionError, FileNotFoundError)):
            source.verify(self.directory)

    def test_complete_source_corpus_and_corrected_histories_remain_unaccepted(self):
        self.assertEqual(source.verify(self.directory), self.report['summary'])

    def test_source_cannot_claim_linux_acceptance(self):
        self.report['accepted'] = True
        self.save()
        self.refused()

    def test_linux_gate_cannot_be_closed_by_native_captures(self):
        self.report['remainingAcceptance'].remove('LinuxImplementation')
        self.save()
        self.refused()

    def test_missing_closed_context_rejected_after_manifest_refresh(self):
        name = 'closed/captures.json'
        data = json.loads((self.directory / name).read_text())
        data['captures'].pop()
        self.update(name, data)
        self.refused()

    def test_probe_flag_cannot_hide_a_changed_public_image(self):
        data = json.loads((self.directory / 'closed/captures.json').read_text())['captures']
        target = data[0]['paths'][1]
        donor = next(r for r in data if r['configuration']['id'] == 'style-primary19')['paths'][1]
        self.replace('closed/' + target, (self.directory / 'closed' / donor).read_bytes())
        self.report['files']['closed/' + target] = hashlib.sha256((self.directory / 'closed' / target).read_bytes()).hexdigest()
        self.save()
        self.refused()

    def test_unrequested_center_guide_cannot_be_invented(self):
        name = 'closed/captures.json'
        data = json.loads((self.directory / name).read_text())
        data['captures'][0]['states'][1]['guides']['root'] = 0
        self.update(name, data)
        self.refused()

    def test_baseline_query_cannot_be_lost(self):
        name = 'closed/captures.json'
        data = json.loads((self.directory / name).read_text())
        row = next(r for r in data['captures'] if r['configuration']['parentLayout'] == 'baseline')
        row['states'][1]['guideQueries']['root'] = []
        self.update(name, data)
        self.refused()

    def test_padded_label_cannot_be_collapsed_into_the_outer_frame(self):
        name = 'closed/captures.json'
        data = json.loads((self.directory / name).read_text())
        row = data['captures'][0]
        row['states'][2]['parts']['label'] = row['states'][1]['parts']['styled']
        self.update(name, data)
        self.refused()

    def test_empty_font_case_cannot_be_dropped(self):
        name = 'empty/captures.json'
        data = json.loads((self.directory / name).read_text())
        data['captures'].pop()
        self.update(name, data)
        self.refused()

    def test_text_step_must_change_the_rendered_concat_run(self):
        name = 'histories/histories.json'
        data = json.loads((self.directory / name).read_text())
        row = next(r for r in data['histories'] if r['configuration']['id'] == 'style-concat')
        for initial, text in zip(row['steps'][0]['paths'], row['steps'][1]['paths']):
            target = 'histories/' + text
            self.replace(target, (self.directory / 'histories' / initial).read_bytes())
            self.report['files'][target] = hashlib.sha256((self.directory / target).read_bytes()).hexdigest()
        self.save()
        self.refused()

    def test_retained_wrapper_cannot_be_recreated(self):
        name = 'histories/histories.json'
        data = json.loads((self.directory / name).read_text())
        data['histories'][0]['steps'][3]['states'][1]['wrapperInstances'] = 2
        self.update(name, data)
        self.refused()

    def test_middle_history_step_cannot_be_skipped(self):
        name = 'histories/histories.json'
        data = json.loads((self.directory / name).read_text())
        data['histories'][0]['steps'].pop(3)
        self.update(name, data)
        self.refused()

    def test_clean_replay_cannot_skip_an_output(self):
        name = 'clean-replay-comparison.json'
        data = json.loads((self.directory / name).read_text())
        data['hashes'].pop(next(iter(data['hashes'])))
        self.update(name, data)
        self.refused()

    def test_pinned_source_cannot_be_changed(self):
        name = 'source-audit.json'
        data = json.loads((self.directory / name).read_text())
        data['files']['Sources/Sabella/Tokens.swift'] = '0' * 64
        self.update(name, data)
        self.refused()

    def test_private_type_cannot_be_claimed_as_a_public_constructor(self):
        name = 'api/results.json'
        data = json.loads((self.directory / name).read_text())
        data[1]['exitCode'] = 0
        self.update(name, data)
        self.refused()

    def test_original_ineffective_trace_cannot_be_accepted(self):
        name = 'diagnostic-comparison.json'
        data = json.loads((self.directory / name).read_text())
        data['originalConcatTextTraceEffective'] = True
        self.update(name, data)
        self.refused()


if __name__ == '__main__':
    unittest.main()
