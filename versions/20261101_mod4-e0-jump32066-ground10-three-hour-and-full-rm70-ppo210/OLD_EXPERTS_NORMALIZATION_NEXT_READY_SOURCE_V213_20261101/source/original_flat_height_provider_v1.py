"""Original flat task's cached root-height getter; no new ground cache or query."""
from pathlib import Path
import ast,hashlib,importlib
EXPECTED_TASK_SHA='30ce41126a1a9b78a1c2b446281b28f4555c28052bfaa7c0e9a76079cf561fc5'
def validate_flat_height_source(path,contract):
 p=Path(path);raw=p.read_bytes();assert contract['kind']=='original_mod4_task_flat_root_height_readonly_v1' and contract['task_source_SHA']==EXPECTED_TASK_SHA and hashlib.sha256(raw).hexdigest()==EXPECTED_TASK_SHA
 tree=ast.parse(raw);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='root_height_above_ground');body=[n for n in fn.body if not(isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))]
 expected=ast.parse("def expected(env):\n robot=env.scene['robot']\n return robot.data.root_pos_w[:,2]-getattr(env,'_mod4_ground_z',torch.zeros(env.num_envs,device=env.device))").body[0].body
 assert ast.dump(ast.Module(body=body,type_ignores=[]),include_attributes=False)==ast.dump(ast.Module(body=expected,type_ignores=[]),include_attributes=False),'Original readonly height getter source changed'
 flat=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='ground_height');branch=next(n for n in flat.body if not(isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant)))
 assert isinstance(branch,ast.If) and ast.dump(branch.test,include_attributes=False)==ast.dump(ast.parse("TERRAIN=='flat'",mode='eval').body,include_attributes=False)
 return dict(passed=True,source_SHA=EXPECTED_TASK_SHA,root_height_getter='root_height_above_ground',original_missing_cache_fallback_legal=True,authored_flat_ground_world_z0_source_known=True,no_new_cache_injection_or_SDK_or_raycast=True)
class OriginalFlatHeightProvider:
 def __init__(self,env,t,contract,ground_module=None):
  module=ground_module if ground_module is not None else importlib.import_module('mod4_task')
  assert module.TERRAIN=='flat','Readonly flat provider must not enter field/raycast domain'
  self.proof=validate_flat_height_source(module.__file__,contract);fn=module.root_height_above_ground
  assert Path(fn.__code__.co_filename).resolve()==Path(module.__file__).resolve()
  self.env=env;self.t=t;self.getter=fn;self.contract=contract;self.height()
 def height(self):
  value=self.getter(self.env);value=value.torch if hasattr(value,'torch') else value
  assert self.t.is_tensor(value) and tuple(value.shape)==(self.env.num_envs,) and value.is_floating_point() and bool(self.t.isfinite(value).all())
  return value
 def ground_z(self):
  root=self.env.scene['robot'].data.root_pos_w;root=root.torch if hasattr(root,'torch') else root
  return root[:,2]-self.height()
