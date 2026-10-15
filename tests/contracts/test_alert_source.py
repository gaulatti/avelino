import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('alert_source',ROOT/'scripts/verify-alert-source.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
class AlertSourceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/'source';shutil.copytree(verifier.DIRECTORY,self.directory)
    def change(self,name,operation):
        p=self.directory/name;j=json.loads(p.read_text());operation(j);p.write_text(json.dumps(j))
        p=self.directory/'investigation.json';j=json.loads(p.read_text());j['files'][name]=hashlib.sha256((self.directory/name).read_bytes()).hexdigest();p.write_text(json.dumps(j))
    def test_false_instrumentation_identity_is_refused(self):
        self.change('captures.json',lambda j:j['captures'][0].update(instrumentedPngByteIdentical=False))
        with self.assertRaisesRegex(AssertionError,'instrumentation identity'):verifier.verify(self.directory)
    def test_disabled_activation_is_refused(self):
        self.change('captures.json',lambda j:next(c for c in j['behavior'] if c['action']=='disabled-click').update(counter=1))
        with self.assertRaisesRegex(AssertionError,'lifecycle transition'):verifier.verify(self.directory)
    def test_uninstrumented_text_bounds_cannot_be_changed(self):
        self.change('text-layout/measurements.json',lambda j:j[0].update(componentWidth=j[0]['componentWidth']+1))
        with self.assertRaisesRegex(AssertionError,'measurement changed'):verifier.verify(self.directory)
    def test_untrusted_hosted_renderer_cannot_be_accepted(self):
        directory=Path(self.temp.name)/'boundaries'
        shutil.copytree(ROOT/'evidence/reference-investigations/prose-boundaries-20261015',directory)
        p=directory/'investigation.json';j=json.loads(p.read_text());j['untrustedContextWitnesses']=[];p.write_text(json.dumps(j))
        with self.assertRaisesRegex(AssertionError,'Untrusted hosted renderer'):verifier.verify_boundaries(directory)
if __name__=='__main__':unittest.main()
