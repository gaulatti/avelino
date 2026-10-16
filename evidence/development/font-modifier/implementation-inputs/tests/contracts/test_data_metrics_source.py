import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('data_metrics_source',ROOT/'scripts/verify-data-metrics-source.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
class DataMetricsSourceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/'source';shutil.copytree(verifier.DIRECTORY,self.directory)
    def change(self,operation):
        p=self.directory/'captures.json';j=json.loads(p.read_text());operation(j);p.write_text(json.dumps(j))
        p=self.directory/'investigation.json';j=json.loads(p.read_text());j['files']['captures.json']=hashlib.sha256((self.directory/'captures.json').read_bytes()).hexdigest();p.write_text(json.dumps(j))
    def test_layout_identity_cannot_be_claimed_when_false(self):
        self.change(lambda j:j['captures'][0].update(layoutWitnessPngByteIdentical=False))
        with self.assertRaisesRegex(AssertionError,'Layout witness identity'):verifier.verify(self.directory)
    def test_badge_cannot_shrink_to_parent_proposal(self):
        def shrink(j):
            c=next(c for c in j['captures'] if c['fixture']=='icon-badge-narrow');c['componentSize']['width']=12;c['componentRect']['width']=12
        self.change(shrink)
        with self.assertRaisesRegex(AssertionError,'badge fixed extent'):verifier.verify(self.directory)
    def test_currency_cannot_use_wrong_minor_unit_precision(self):
        self.change(lambda j:next(r for r in j['formatting'] if r['value']=='1234.56789' and r['format']=='currency' and r['currencyCode']=='JPY').update(text='¥1,234.57'))
        with self.assertRaisesRegex(AssertionError,'currency precision'):verifier.verify(self.directory)
    def test_metric_cannot_follow_environment_locale(self):
        self.change(lambda j:next(c for c in j['captures'] if c['fixture']=='metric-currency-environment-de' and c['appearance']=='light' and c['textScale']==1 and c['dpr']==2).update(formattedValue='12.345,68 $'))
        with self.assertRaisesRegex(AssertionError,'Metric unexpectedly follows environment locale'):verifier.verify(self.directory)
    def test_delta_cannot_ignore_environment_locale(self):
        self.change(lambda j:next(c for c in j['captures'] if c['fixture']=='stat-card-positive-environment-de' and c['appearance']=='light' and c['textScale']==1 and c['dpr']==2).update(formattedDelta='+12.345679%'))
        with self.assertRaisesRegex(AssertionError,'delta environment locale'):verifier.verify(self.directory)
    def test_mono_candidate_cannot_replace_observed_native_face(self):
        self.change(lambda j:next(c for c in j['captures'] if c['api']=='BleeckerKbd')['layoutWitnessFonts']['key'].update(postScriptName='Generic Mono'))
        with self.assertRaisesRegex(AssertionError,'Native mono face changed'):verifier.verify(self.directory)
if __name__=='__main__':unittest.main()
