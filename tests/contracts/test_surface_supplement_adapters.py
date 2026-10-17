import importlib.util
import itertools
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('surface_supplement_projection',ROOT/'scripts/generate-surface-supplement-witnesses.py')
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)


class SurfaceSupplementAdapters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(source.TARGET.read_text())

    def test_projection_matches_sealed_native_observations(self):
        self.assertEqual(source.TARGET.read_text(),source.projected())
        self.assertIs(self.data['accepted'],False)

    def test_every_baseline_and_pointer_context_is_present(self):
        for name,count in [('nativeBaselineContexts',55),('nativeInputProfiles',36)]:
            rows=self.data[name]
            ids={r['configuration']['fixture'] for r in rows}
            self.assertEqual(len(ids),count)
            self.assertEqual(len(rows),count*8)
            self.assertEqual({(r['configuration']['fixture'],r['appearance'],r['textScale'],r['dpr']) for r in rows},
                             set(itertools.product(ids,['light','dark'],[1,1.5],[1,2])))

    def test_flat_children_retain_separate_guides(self):
        rows=[r for r in self.data['nativeBaselineContexts'] if r['configuration']['content']=='multi'
              and r['configuration']['parentLayout']=='zstack']
        self.assertEqual(len(rows),8)
        for row in rows:
            self.assertEqual(row['guides']['root'],[13,44])
            self.assertEqual(len(row['parts']['root']),2)

    def test_explicit_guides_are_not_clamped_to_caller_height(self):
        rows=[r for r in self.data['nativeBaselineContexts'] if r['configuration']['guide'] is not None]
        self.assertEqual(len(rows),24)
        for row in rows:
            self.assertEqual(row['guides']['caller'],[row['configuration']['guide']])

    def test_nested_unrequested_guides_are_not_invented(self):
        rows=[r for r in self.data['nativeBaselineContexts'] if r['configuration']['parentLayout']!='zstack']
        self.assertEqual(len(rows),48)
        for row in rows:self.assertEqual(set(row['guides']),{'parent','reference'})

    def test_fractional_points_and_full_counter_sequences_reach_both_modes(self):
        count=0
        for row in self.data['nativeInputProfiles']:
            self.assertEqual([r['mode'] for r in row['modes']],[0,3])
            self.assertTrue(any(not p['x'].is_integer() if isinstance(p['x'],float) else False for p in row['points']))
            for mode in row['modes']:
                self.assertEqual(len(mode['sequences']),len(row['points']))
                self.assertEqual(len(mode['activations']),len(row['points']))
                count+=len(mode['sequences'])
        self.assertEqual(count,57792)


if __name__=='__main__':unittest.main()
