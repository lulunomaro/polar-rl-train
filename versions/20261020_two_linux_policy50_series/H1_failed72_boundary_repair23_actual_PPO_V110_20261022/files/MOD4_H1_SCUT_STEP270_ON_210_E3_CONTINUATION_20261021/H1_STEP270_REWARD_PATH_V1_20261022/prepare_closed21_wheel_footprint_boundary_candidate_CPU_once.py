"""Narrow ordinary arena-boundary repair candidate; no GPU or training mutation."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;N=T/'H1_STEP270_REWARD_RESOURCE_BRANCH_V21_20261022';R=B/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
FUNCTION='''def out_of_authored_floor(env):
    # Ordinary episode boundary: the complete wheels must remain over authored floor.
    root=tensor(env.scene['robot'].data.root_pos_w)
    if not torch.isfinite(root).all():raise RuntimeError('Nonfinite root position at terrain boundary guard')
    origins=env.scene.env_origins
    lower=origins[:,:2].amin(0)-2.5;upper=origins[:,:2].amax(0)+2.5
    lo,hi=wheel_bounds(env)
    if not torch.isfinite(lo).all() or not torch.isfinite(hi).all():raise RuntimeError('Nonfinite wheel footprint at terrain boundary guard')
    return ((root[:,:2]<lower)|(root[:,:2]>upper)).any(-1)|((lo[:,:,:2]<lower)|(hi[:,:,:2]>upper)).any(-1).any(-1)
'''
def main():
 import torch
 torch.set_num_threads(2)
 closed=json.loads((N/'reports/H1_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closed['actual_finite_transport_returned'] and not closed['complete_models']['h1'] and closed['original_canonical_cost_settled']
 old=N/'current_pair_closed_text/h1/h1_step270_sdk_runtime_candidate.py';assert H(old)=='5106639e761abfb51d0ea4a2be3249895f6eb502c2e030c0a1f56565d914f36d'
 source=old.read_text('utf8');tree=ast.parse(source);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='out_of_authored_floor');lines=source.splitlines(keepends=True);new=''.join(lines[:fn.lineno-1])+FUNCTION+''.join(lines[fn.end_lineno:])
 draft=B/'wheel_footprint_boundary_candidate_V1_UNINSTALLED';draft.mkdir();p=draft/'h1_step270_sdk_runtime_candidate.py';p.write_text(new,encoding='utf8')
 nt=ast.parse(new);strip=lambda tr:ast.dump(ast.Module(body=[x for x in tr.body if not(isinstance(x,ast.FunctionDef) and x.name=='out_of_authored_floor')],type_ignores=[]),include_attributes=False)
 assert strip(tree)==strip(nt)
 from types import SimpleNamespace as S
 rng=torch.get_rng_state().clone();scope={'torch':torch,'tensor':lambda x:x,'wheel_bounds':lambda e:(e.lo,e.hi)};exec(compile(ast.Module(body=[next(x for x in nt.body if isinstance(x,ast.FunctionDef) and x.name=='out_of_authored_floor')],type_ignores=[]),str(p),'exec'),scope)
 # The two explicit origins reproduce the saved finite global floor bounds.
 origins=torch.tensor([[-176.25,-175.],[176.25,175.]],dtype=torch.float32)
 def env(root,lo,hi):return S(scene={'robot':S(data=S(root_pos_w=root))},lo=lo,hi=hi)
 class Scene(dict):pass
 def make(root,lo,hi):
  e=env(root,lo,hi);e.scene=Scene(e.scene);e.scene.env_origins=origins;return e
 root=torch.zeros((20000,3));lo=torch.zeros((20000,2,3));hi=torch.zeros_like(lo);lo[:,:,:2]=-.1;hi[:,:,:2]=.1
 f=scope['out_of_authored_floor'];tests=[]
 def check(name,e,expected):
  actual=f(e);assert torch.equal(actual,expected);tests.append(dict(name=name,passed=True,terminated_environments=int(actual.sum())))
 check('all20k_inside',make(root.clone(),lo.clone(),hi.clone()),torch.zeros(20000,dtype=torch.bool))
 for axis,upper in [(0,178.75),(1,177.5)]:
  l=lo.clone();h=hi.clone();h[0,1,axis]=upper;expected=torch.zeros(20000,dtype=torch.bool)
  check('exact_floor_edge_axis'+str(axis),make(root.clone(),l,h),expected)
  h[0,1,axis]=torch.nextafter(torch.tensor(upper),torch.tensor(float('inf')));expected[0]=True
  check('one_representable_step_outside_axis'+str(axis),make(root.clone(),l,h),expected)
 bad=json.loads(next((N/'current_pair_closed_text/h1/job0/production').glob('ACTUAL_BAD_TERRAIN_QUERY_*.json')).read_bytes());row=bad['actual_bad_rows'][0];point=torch.tensor(row['actual_start']);bounds=bad['actual_floor_xy_bounds'];assert row['hit'] is False and point[1]>bounds[1][1]
 l=lo.clone();h=hi.clone();h[11843,1,1]=point[1];expected=torch.zeros(20000,dtype=torch.bool);expected[11843]=True
 check('actual_failed_wheel_ray_outside_root_only_blindspot',make(root.clone(),l,h),expected)
 r=root.clone();r[9,0]=-179.;expected=torch.zeros(20000,dtype=torch.bool);expected[9]=True
 check('existing_root_exit_still_terminates',make(r,lo.clone(),hi.clone()),expected)
 for name,which in [('nonfinite_root',0),('nonfinite_wheel',1)]:
  r=root.clone();l=lo.clone();h=hi.clone()
  if which:r[0,0]=0;h[0,0,0]=float('nan')
  else:r[0,0]=float('nan')
  try:f(make(r,l,h))
  except RuntimeError:tests.append(dict(name=name,passed=True,rejected=True))
  else:raise AssertionError(name)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('V110_WHEEL_FOOTPRINT_BOUNDARY_REPAIR_CANDIDATE_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,scope='Ordinary per-environment arena exit covers actual complete wheel collider footprint; no ground fallback or tolerance change',old_runtime=dict(path=str(old),SHA=H(old)),candidate_runtime=dict(path=str(p),SHA=H(p)),all_other_normalized_AST_exact=True,tests=tests,recorded_miss=row,actual_floor_xy_bounds=bounds,recorded_ray_y_excess_m=float(point[1])-bounds[1][1],original_missing_query_guards_and_reward_methods_AST_exact=True,root_only_blindspot_confirmed_but_prior_control_prevention_not_yet_measured=True,no_claim_of_actual_GPU_repair_or_skill=True,no_new_native_query_physics_actor_optimizer_RNG_or_GO=True))
 print(json.dumps(dict(candidate_CPU_passed=True,cases=len(tests),runtime_SHA=H(p),not_installed=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('V110_BOUNDARY_CANDIDATE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
