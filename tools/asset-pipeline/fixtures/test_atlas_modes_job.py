"""Pure contract tests for explicit shared packing/preserved baking."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline.job import validate
from pipeline.common import PipelineError

class AtlasModeJobs(unittest.TestCase):
    def test_valid_opt_ins(self):
        validate({'objects':['A'],'out_dir':'x','pack':True,'gap_margin':9/2048,
                  'min_gap_px':8},'uv')
        validate({'objects':['A'],'out_dir':'x','preserve_layout':True,'alpha':False},'bake')

    def test_bad_options_fail(self):
        for options in [{'pack':'yes'},{'preserve_layout':1},{'gap_margin':float('nan')},
                        {'min_gap_px':-1},{'gap_margin':.5}]:
            with self.subTest(options=options), self.assertRaises(PipelineError):
                validate({'objects':['A'],'out_dir':'x',**options},'uv')
        for field in ('unwrap','pack','alpha','export'):
            with self.subTest(field=field), self.assertRaises(PipelineError):
                validate({'objects':['A'],'out_dir':'x','preserve_layout':True,
                          field:('x.glb' if field=='export' else True)},'bake')

if __name__=='__main__': unittest.main()
