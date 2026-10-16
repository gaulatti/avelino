import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('font_edges_source',ROOT/'scripts/verify-font-edges-source.py')
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)


class FontEdgeSourceContracts(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.directory=Path(self.temporary.name)/'source';shutil.copytree(source.DIRECTORY,self.directory)

    def edit(self,name,mutate):
        path=self.directory/name;data=json.loads(path.read_text());mutate(data)
        path.write_text(json.dumps(data,indent=2)+'\n')
        if name=='investigation.json':return
        manifest=self.directory/'investigation.json';report=json.loads(manifest.read_text())
        report['files'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
        if name=='captures/captures.json':
            path=self.directory/'clean-replay.json';replay=json.loads(path.read_text())
            row=next(r for r in replay['outputs'] if r['file']=='captures.json')
            row['originalSha256']=row['replaySha256']=report['files'][name]
            path.write_text(json.dumps(replay,indent=2)+'\n')
            report['files']['clean-replay.json']=hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(report,indent=2)+'\n')

    def rejected(self):
        with self.assertRaises(AssertionError):source.verify(self.directory)

    def test_complete_negative_inputs_and_zero_size_witnesses(self):
        self.assertEqual(source.verify(self.directory),dict(groups=72,zeroSizeImageMatches=216,sourceReplayFiles=217,accepted=False))

    def test_source_cannot_accept_linux(self):
        self.edit('investigation.json',lambda d:d.update(accepted=True));self.rejected()

    def test_missing_context(self):
        self.edit('captures/captures.json',lambda d:d['captures'].pop());self.rejected()

    def test_duplicate_context(self):
        self.edit('captures/captures.json',lambda d:d['captures'].__setitem__(1,d['captures'][0]));self.rejected()

    def test_negative_size_cannot_be_relabelled_positive(self):
        self.edit('captures/captures.json',lambda d:d['captures'][0]['configuration'].update(size=14));self.rejected()

    def test_negative_size_cannot_become_zero_height(self):
        def empty(d):
            for state in d['captures'][0]['states'][1:]:
                state['partInstances']['label'][0]['height']=0
        self.edit('captures/captures.json',empty);self.rejected()

    def test_probe_cannot_change_public_result(self):
        self.edit('captures/captures.json',lambda d:d['captures'][0].update(publicProbedIdentical=False));self.rejected()

    def test_nonfinite_text_acceptance_cannot_follow_finite_inputs(self):
        self.edit('investigation.json',lambda d:d.update(nonfiniteTextLayoutAcceptance='passed'));self.rejected()

    def test_other_weight_acceptance_cannot_follow_regular(self):
        self.edit('investigation.json',lambda d:d.update(otherWeightCombinationsAcceptance='passed'));self.rejected()

    def test_precompiled_input_rejected(self):
        self.edit('tooling-provenance.json',lambda d:d.update(compiledInputs=['Sabella.o']));self.rejected()

    def test_incomplete_replay_rejected(self):
        self.edit('clean-replay.json',lambda d:d['outputs'].pop());self.rejected()

    def test_unsealed_file_rejected(self):
        (self.directory/'unexpected.json').write_text('{}\n');self.rejected()


if __name__=='__main__':unittest.main()
