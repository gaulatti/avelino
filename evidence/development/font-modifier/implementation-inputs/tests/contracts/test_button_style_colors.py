import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('button_style_colors',ROOT/'scripts/verify-button-style-colors.py')
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)

class ButtonStylePlatformColors(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.directory=Path(self.temporary.name)/'colors';shutil.copytree(source.DIRECTORY,self.directory)
    def edit(self,name,change):
        p=self.directory/name;data=json.loads(p.read_text());change(data);p.write_text(json.dumps(data))
    def refused(self):
        with self.assertRaises(AssertionError):source.verify(self.directory)
    def test_complete_replay_and_original_png_samples(self):
        self.assertEqual(source.verify(self.directory),dict(sourceReplayFiles=1,pngSamples=64,accepted=False))
    def test_platform_colors_cannot_accept_linux(self):
        self.edit('result.json',lambda d:d.update(accepted=True));self.refused()
    def test_prebuilt_inputs_cannot_be_replay(self):
        self.edit('provenance.json',lambda d:d.update(compiledInputs=['colors']));self.refused()
    def test_duplicate_sample_cannot_replace_context(self):
        self.edit('result.json',lambda d:d['samples'].__setitem__(1,d['samples'][0]));self.refused()
    def test_forged_source_pixel_refused(self):
        self.edit('result.json',lambda d:d['samples'][0].update(rgba=[0,0,0,255],predicted=[0,0,0,255]));self.refused()
    def test_incorrect_opacity_refused(self):
        self.edit('result.json',lambda d:d['samples'][0].update(opacity=.3));self.refused()
    def test_compilation_cannot_be_ui_replay(self):
        self.edit('replay-result.json',lambda d:d.update(uiInteraction=True));self.refused()
    def test_unsealed_output_refused(self):
        (self.directory/'extra.json').write_text('{}');self.refused()

if __name__=='__main__':unittest.main()
