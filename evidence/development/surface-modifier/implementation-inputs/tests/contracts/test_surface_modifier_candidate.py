"""Reject incomplete or self-approved surface candidate evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('surface_candidate',ROOT/'scripts/verify-surface-modifier-candidate.py')
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
class SurfaceCandidateIntegrity(unittest.TestCase):
 def setUp(self):
  self.temporary=tempfile.TemporaryDirectory();self.directory=Path(self.temporary.name)/'candidate';shutil.copytree(source.DIRECTORY,self.directory)
  self.report=json.loads((self.directory/'candidate.json').read_text())
 def tearDown(self):self.temporary.cleanup()
 def save(self): (self.directory/'candidate.json').write_text(json.dumps(self.report))
 def update(self,name,value):
  p=self.directory/name;p.write_text(json.dumps(value));self.report['files'][name]=hashlib.sha256(p.read_bytes()).hexdigest();self.save()
 def refused(self):
  with self.assertRaises((AssertionError,FileNotFoundError)):source.verify(self.directory)
 def test_complete_corpus_remains_unaccepted(self):self.assertEqual(source.verify(self.directory),self.report['strictComparison'])
 def test_acceptance_cannot_be_forged(self):self.report['accepted']=True;self.save();self.refused()
 def test_centered_maps_cannot_accept_baselines(self):self.report['baselineAcceptance']='passed';self.save();self.refused()
 def test_missing_closed_context_rejected_even_with_refreshed_manifest(self):
  name='captures/capture-results.json';d=json.loads((self.directory/name).read_text());d['records'].pop();self.update(name,d);self.refused()
 def test_comparison_totals_cannot_hide_failures(self):self.report['strictComparison']['exactPixelAndGeometryMatches']=416;self.save();self.refused()
 def test_new_tolerance_rejected_even_with_refreshed_manifest(self):
  name='comparison/comparison.json';d=json.loads((self.directory/name).read_text());d['results'][0]['tolerance']='one channel';self.update(name,d);self.refused()
 def test_missing_runtime_profile_rejected_even_with_refreshed_manifest(self):
  name=next(n for n in self.report['files'] if n.startswith('runtime/surface-modifier-'));(self.directory/name).unlink();del self.report['files'][name];self.save();self.refused()
 def test_retained_history_step_cannot_be_skipped(self):
  name=next(n for n in self.report['files'] if n.startswith('runtime/surface-modifier-'));d=json.loads((self.directory/name).read_text());d['retainedHistories'][0]['steps'].pop();self.update(name,d);self.refused()
 def test_extra_unrecorded_capture_rejected(self):
  (self.directory/'captures/unrecorded.png').write_bytes(b'not a capture');self.refused()
if __name__=='__main__':unittest.main()
