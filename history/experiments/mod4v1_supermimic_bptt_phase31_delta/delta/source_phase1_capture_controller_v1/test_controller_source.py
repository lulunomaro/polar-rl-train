"""Pure SOURCE/metadata tests; never executes controller.main or Popen."""
from pathlib import Path
import ast,json,hashlib,unittest
import phase1_capture_parent_actual_wait_controller_v1 as c
HERE=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def stage(self,**change):
  value=dict(materialized=True,parent_launches=0,purpose='NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN');value.update(change);raw=json.dumps(value).encode();return raw,hashlib.sha256(raw).hexdigest()
 def test_materialized_receipt_only(self):
  raw,sha=self.stage();self.assertTrue(c.validate_stage(raw,sha)['materialized'])
 def test_stage_hash_mismatch(self):
  raw,sha=self.stage()
  with self.assertRaises(AssertionError):c.validate_stage(raw,'0'*64)
 def test_preflight_is_not_materialization(self):
  raw,sha=self.stage(materialized=False)
  with self.assertRaises(AssertionError):c.validate_stage(raw,sha)
 def test_prior_parent_launch_not_replayed(self):
  raw,sha=self.stage(parent_launches=1)
  with self.assertRaises(AssertionError):c.validate_stage(raw,sha)
 def test_old_purpose_not_relabelled(self):
  raw,sha=self.stage(purpose='OLD_BOUND_OR_QUALITY')
  with self.assertRaises(AssertionError):c.validate_stage(raw,sha)
 def test_only_original_parent_pin(self):
  self.assertEqual(c.PARENT,(9336,'d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'))
 def test_same_actual_wait_try_finally_as_executed_original(self):
  original=HERE.parent/'bound_probe_parent_actual_wait_controller_v1.py';raw=original.read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),'818e434162c6f4ae91ae50dfcd059ad2b53755accc7b074bf63e75b12c47f6e6')
  def branch(path):
   tree=ast.parse(path.read_text(encoding='utf-8'));main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');value=next(n for n in main.body if isinstance(n,ast.Try))
   class Normalize(ast.NodeTransformer):
    def visit_Constant(self,node):
     if type(node.value)is str:node.value='METADATA_STRING'
     return node
   return ast.dump(Normalize().visit(value),include_attributes=False)
  self.assertEqual(branch(original),branch(Path(c.__file__)))
 def test_original_identity_and_atomic_publication_unchanged(self):
  old=ast.parse((HERE.parent/'bound_probe_parent_actual_wait_controller_v1.py').read_text(encoding='utf-8'));new=ast.parse(Path(c.__file__).read_text(encoding='utf-8'))
  for name in('identity','put'):
   a=next(n for n in old.body if isinstance(n,ast.FunctionDef)and n.name==name);b=next(n for n in new.body if isinstance(n,ast.FunctionDef)and n.name==name);self.assertEqual(ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False))
 def test_no_new_resource_or_signal_imports(self):
  tree=ast.parse(Path(c.__file__).read_text(encoding='utf-8'));imports={a.name for n in tree.body if isinstance(n,ast.Import)for a in n.names};self.assertEqual(imports,{'argparse','json','hashlib','os','subprocess','time','traceback'});self.assertNotIn('fcntl',imports);self.assertNotIn('torch',imports);self.assertNotIn('signal',imports)
if __name__=='__main__':unittest.main(verbosity=2)
