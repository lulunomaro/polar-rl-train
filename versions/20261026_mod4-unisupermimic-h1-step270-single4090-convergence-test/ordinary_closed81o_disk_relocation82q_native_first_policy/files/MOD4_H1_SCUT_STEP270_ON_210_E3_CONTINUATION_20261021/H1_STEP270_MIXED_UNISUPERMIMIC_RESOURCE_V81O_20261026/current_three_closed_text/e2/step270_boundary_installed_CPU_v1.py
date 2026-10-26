
from pathlib import Path
import ast,hashlib,json,types
import torch
def check(B):
 B=Path(B);auth=json.loads((B/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json').read_bytes());repair=auth['arena_boundary_repair_CPU'];p=B/'h1_step270_sdk_runtime_candidate.py';old=B/'boundary_reference_sources/h1_step270_sdk_runtime_original.py'
 H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert H(p)==repair['candidate_runtime']['SHA'] and H(old)==repair['old_runtime']['SHA']=='5106639e761abfb51d0ea4a2be3249895f6eb502c2e030c0a1f56565d914f36d'
 a=ast.parse(old.read_text('utf8'));b=ast.parse(p.read_text('utf8'));strip=lambda t:ast.dump(ast.Module(body=[n for n in t.body if not(isinstance(n,ast.FunctionDef) and n.name=='out_of_authored_floor')],type_ignores=[]),include_attributes=False)
 assert strip(a)==strip(b)
 fn=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name=='out_of_authored_floor');ns={'torch':torch,'tensor':lambda x:x,'wheel_bounds':lambda e:(e.lo,e.hi)};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(p),'exec'),ns)
 class Scene(dict):pass
 origins=torch.tensor([[-176.25,-175.],[176.25,175.]])
 def env(root,lo,hi):
  scene=Scene(robot=types.SimpleNamespace(data=types.SimpleNamespace(root_pos_w=root)));scene.env_origins=origins;return types.SimpleNamespace(scene=scene,lo=lo,hi=hi)
 rng=torch.get_rng_state().clone();root=torch.zeros(20000,3);lo=torch.full((20000,2,3),-.1);hi=torch.full((20000,2,3),.1);f=ns['out_of_authored_floor'];assert not f(env(root,lo,hi)).any()
 hi[11843,1,1]=177.50027465820312;v=f(env(root,lo,hi));assert int(v.sum())==1 and bool(v[11843])
 hi[11843,1,1]=177.5;assert not f(env(root,lo,hi)).any()
 hi[0,0,0]=float('nan')
 try:f(env(root,lo,hi))
 except RuntimeError:pass
 else:raise AssertionError('Nonfinite footprint not rejected')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 return dict(passed=True,actual_installed_boundary_function_CPU=True,all_other_runtime_AST_exact=True,missing_queries_still_rejected_no_flat_fallback=True,ordinary_per_environment_exit_only=True,no_Kit_PhysX_GPU_actor_optimizer_RNG=True,not_future_GPU_success=True)
