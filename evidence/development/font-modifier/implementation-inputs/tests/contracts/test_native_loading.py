import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('native_loading',ROOT/'scripts/verify-native-loading.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)

class NativeLoadingIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/'native';shutil.copytree(verifier.DIRECTORY,self.directory)
    def change(self,operation):
        path=self.directory/'captures.json';j=json.loads(path.read_text());operation(j);path.write_text(json.dumps(j))
        report_path=self.directory/'investigation.json';report=json.loads(report_path.read_text());report['files'][path.name]=hashlib.sha256(path.read_bytes()).hexdigest();report_path.write_text(json.dumps(report))
    def test_missing_native_descendant_is_refused(self):
        self.change(lambda j:j['captures'][0].update(nativeProgressIndicators=[]))
        with self.assertRaisesRegex(AssertionError,'actual native progress descendant'):verifier.verify(self.directory)
    def test_placeholder_renderer_is_refused(self):
        self.change(lambda j:j['captures'][0].update(captureMethod='SwiftUI.ImageRenderer/CoreGraphics'))
        with self.assertRaisesRegex(AssertionError,'ImageRenderer placeholders'):verifier.verify(self.directory)
    def test_hidden_native_progress_is_refused(self):
        self.change(lambda j:j['captures'][0]['nativeProgressIndicators'][0].update(hidden=True))
        with self.assertRaisesRegex(AssertionError,'visible and correctly sized'):verifier.verify(self.directory)

if __name__=='__main__':unittest.main()
