import importlib.util,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
class CaptureFailurePreservation(unittest.TestCase):
    def test_timeout_keeps_partial_diagnostics_after_staging_cleanup(self):
        spec=importlib.util.spec_from_file_location('capture_failure',ROOT/'scripts/capture-proposals.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'repo';root.mkdir();(root/'scripts').mkdir();(root/'scripts/verify-proposals.py').write_text('def verify(path): return None\n')
            for name in ['CMakeLists.txt','CMakePresets.json']:(root/name).write_text('fixture')
            catalog=root/'catalog';catalog.write_text('fixture')
            reference=root/'reference';reference.mkdir();(reference/'proposal.json').write_text(json.dumps({'referenceRevision':'test','status':'test-only error-path fixture'}));(reference/'fixtures.json').write_text('{}')
            case={'api':'BleeckerButton','fixture':'timeout','path':'timeout.png','textScale':1,'dpr':1,'appearance':'light','sha256':'0'*64};(reference/'captures.json').write_text(json.dumps({'captures':[case]}))
            output=root/'staging/captures'
            with patch.object(module,'ROOT',root),patch.object(module.subprocess,'check_output',return_value='test metadata'),patch.object(module.subprocess,'run',side_effect=subprocess.TimeoutExpired(['catalog'],30,output=b'partial stdout',stderr=b'partial stderr')):
                self.assertEqual(module.capture(catalog,reference,output,jobs=1),1)
            report=json.loads((output/'capture-results.json').read_text());self.assertEqual(report['status'],'failed');self.assertEqual(report['results'][0]['exitCode'],124);self.assertTrue(report['results'][0]['timedOut'])
            self.assertIn('30-second deadline',report['results'][0]['runtimeErrors'][0]);archived=Path(report['failureArtifact']);self.assertTrue(archived.is_dir())
            shutil.rmtree(output.parent)
            self.assertEqual(json.loads((archived/'capture-results.json').read_text()),report)
            diagnostics=(archived/'timeout.png.stderr.txt').read_bytes();self.assertIn(b'partial stdout',diagnostics);self.assertIn(b'partial stderr',diagnostics)
if __name__=='__main__':unittest.main()
