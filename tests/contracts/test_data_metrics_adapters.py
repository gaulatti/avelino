import hashlib,importlib.util,json
from pathlib import Path
import tempfile,unittest,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
class DataMetricsAdapters(unittest.TestCase):
    def test_embedded_formatter_inputs_equal_sealed_sources(self):
        data=json.loads((ROOT/'tests/consumer/native-metric-formatting.json').read_text());rows=[]
        self.assertEqual(data['reference'],'fe8a1d462fbd793d883fb92086a16aa2947e32c9')
        for name,h in sorted(data['sourceFiles'].items()):
            p=ROOT/name;self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),h);source=json.loads(p.read_text())
            if 'formatting' in source:rows.extend({**r,'group':'original'} for r in source['formatting'])
            else:
                group='wide-double' if 'additionalFormatting' in source else 'compact-boundaries'
                for r in source.get('additionalFormatting',source.get('results')):
                    rows.append({'bits':r['bits'].zfill(16),'format':'percent' if r['format']=='signedPercent' else r['format'],
                        'signedPercent':r['format']=='signedPercent','currencyCode':r['currencyCode'],'processLocale':r['locale'],'text':r['text'],'group':group})
        order=lambda r:json.dumps(r,sort_keys=True)
        self.assertEqual(sorted(rows,key=order),sorted(data['cases'],key=order));self.assertEqual(len(rows),49448)
    def test_native_adapter_inputs_and_numeric_context_are_verified(self):
        spec=importlib.util.spec_from_file_location('native_inputs',ROOT/'scripts/verify-data-metrics-inputs.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertEqual(module.verify(),{'numericTextCases':40,'numericReplayIdentical':True,'fixtures':131,'cleanInputHashes':35,'byteIdenticalReplay':True,'accepted':False})
    def test_prepared_proposal_keeps_source_width_and_formatter_data(self):
        spec=importlib.util.spec_from_file_location('proposal',ROOT/'scripts/verify-proposals.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertEqual(module.verify(ROOT/'evidence/reference-proposals/data-metrics-20261015'),1048)
if __name__=='__main__':unittest.main()
