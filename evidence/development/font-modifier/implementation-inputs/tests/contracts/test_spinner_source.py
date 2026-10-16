import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('spinner_source',ROOT/'scripts/verify-spinner-source.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
class SpinnerSourceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/'source';shutil.copytree(verifier.DIRECTORY,self.directory)
    def change(self,operation):
        path=self.directory/'captures.json';j=json.loads(path.read_text());operation(j);path.write_text(json.dumps(j))
        report_path=self.directory/'investigation.json';report=json.loads(report_path.read_text());report['files'][path.name]=hashlib.sha256(path.read_bytes()).hexdigest();report_path.write_text(json.dumps(report))
    def test_wrong_medium_size_is_refused(self):
        self.change(lambda j:next(c for c in j['captures'] if c['size']=='md' and c['api']=='BleeckerLoadingSpinner')['nativeProgressIndicators'][0].update(width=20))
        with self.assertRaisesRegex(AssertionError,'source spinner size'):verifier.verify(self.directory)
    def test_wrong_animation_model_is_refused(self):
        self.change(lambda j:j['captures'][0]['nativeProgressIndicators'][0]['layers'][1]['animations'][0].update(duration=0.9))
        with self.assertRaisesRegex(AssertionError,'native animation model'):verifier.verify(self.directory)
    def test_false_phase_zero_identity_is_refused(self):
        self.change(lambda j:j['phases'][0].update(unmodifiedPngByteIdentical=False))
        with self.assertRaisesRegex(AssertionError,'phase identity claim'):verifier.verify(self.directory)
if __name__=='__main__':unittest.main()
