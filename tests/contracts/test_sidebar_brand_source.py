import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('sidebar_brand_source',ROOT/'scripts/verify-sidebar-brand-source.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
class SidebarBrandSourceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/'source';shutil.copytree(verifier.DIRECTORY,self.directory)
    def change(self,name,operation):
        p=self.directory/name;j=json.loads(p.read_text());operation(j);p.write_text(json.dumps(j))
        p=self.directory/'investigation.json';j=json.loads(p.read_text());j['files'][name]=hashlib.sha256((self.directory/name).read_bytes()).hexdigest();p.write_text(json.dumps(j))
    def test_source_identity_cannot_be_claimed_when_false(self):
        self.change('captures.json',lambda j:j['captures'][0].update(layoutWitnessPngByteIdentical=False))
        with self.assertRaisesRegex(AssertionError,'layout identity'):verifier.verify(self.directory)
    def test_one_point_uniform_render_cannot_be_reclassified(self):
        self.change('captures.json',lambda j:next(c for c in j['captures'] if c['fixture']=='brand-mark-size1.0').update(expectedEmpty=False))
        with self.assertRaisesRegex(AssertionError,'uniform case classification'):verifier.verify(self.directory)
    def test_click_cannot_change_caller_selection(self):
        self.change('captures.json',lambda j:next(c for c in j['behavior'] if c['action']=='activate' and not c['initialSelected']).update(selectedAfterAction=True))
        with self.assertRaisesRegex(AssertionError,'selection ownership'):verifier.verify(self.directory)
    def test_full_rectangle_cannot_drop_corner_hit(self):
        self.change('captures.json',lambda j:next(c for c in j['behavior'] if c['action']=='corner').update(calls=0))
        with self.assertRaisesRegex(AssertionError,'callback transition'):verifier.verify(self.directory)
if __name__=='__main__':unittest.main()
