"""Execute exact sealed source reward functions on CPU; no reward/command/runtime mutation."""
from pathlib import Path
import ast,json,time,hashlib,types,os,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';K=W/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017';C=K/'e2_closed112_frozen_prepared_v10/payload/frozen_shared/runtime/isaac/mod4';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 source=C/'scut_flat_rescue.py';task=C/'mod4_task.py';tree=ast.parse(source.read_text('utf8'));names=('exponential','forward_error','linear_exp','linear_square','linear_gap');functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(functions)==5;ns=dict(torch=torch);exec(compile(ast.Module(body=functions,type_ignores=[]),'actual_source_reward_functions_CPU','exec'),ns)
 cfg=ast.parse(task.read_text('utf8'));assert any(isinstance(n,ast.Import) and any(a.name=='scut_flat_rescue' and a.asname=='scut_rescue' for a in n.names) for n in cfg.body)
 bindings={}
 for n in ast.walk(cfg):
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('track_lin_vel','track_lin_vel_tight','track_lin_vel_huge_gap','track_lin_vel_square','run_velocity_error') for t in n.targets):
   bindings[n.targets[0].id]=ast.unparse(n.value)
 assert 'scut_rescue.linear_exp' in bindings['track_lin_vel'] and 'scut_rescue.linear_exp' in bindings['track_lin_vel_tight'] and 'scut_rescue.linear_square' in bindings['track_lin_vel_square'] and 'scut_rescue.linear_gap' in bindings['track_lin_vel_huge_gap']
 manifest=json.loads((K/'payload/e2/job0/original_run_manifest.json').read_bytes());assert float(manifest['env']['RM_W_RUN_VEL_ERROR'])==0.
 exact=[]
 for name in ('MOD4_TWO72_V6_FINALS_LATEST101_FROZEN_SAME_SCOPE_HANDOFF_20261017','MOD4_V7_FINALS_AND_CLOSED101_FROZEN_RESIDUAL_20261017'):
  root=W/name/'payload/e2/job0/runtime/isaac/mod4'
  for filename in ('mod4_task.py','scut_flat_rescue.py'):
   p=root/filename;assert H(p)==H(C/filename);exact.append(dict(path=str(p),SHA=H(p)))
 rng=torch.get_rng_state().clone();robot=types.SimpleNamespace(data=types.SimpleNamespace(projected_gravity_b=torch.tensor([[0.,0.,-1.]]),root_lin_vel_b=torch.zeros(1,3)));command=torch.tensor([[.5,0.,4.]]);env=types.SimpleNamespace(scene={'robot':robot},command_manager=types.SimpleNamespace(get_command=lambda name:command));cases=[]
 def values():return dict(forward_error=float(ns['forward_error'](env)),track_lin=float(ns['linear_exp'](env,std=.25)),track_tight=float(ns['linear_exp'](env,std=.01)),track_square=float(ns['linear_square'](env,sigma=.25)),track_gap=float(ns['linear_gap'](env,gap=.5)))
 for vx in (.5,.6,1.5):
  robot.data.root_lin_vel_b[0]=torch.tensor([vx,0.,0.]);baseline=values()
  for vy in (-1.,-.3,0.,.3,1.):
   robot.data.root_lin_vel_b[0,1]=vy;actual=values();assert actual==baseline;cases.append(dict(vx=vx,vy=vy,command_vx=.5,command_vy=0.,actual_source_four_linear_terms=actual))
 robot.data.root_lin_vel_b[0]=torch.tensor([.5,0.,0.]);good=values();robot.data.root_lin_vel_b[0,0]=1.5;bad=values();assert good['track_lin']!=bad['track_lin'] and good['track_tight']!=bad['track_tight'] and good['track_square']!=bad['track_square'] and good['track_gap']!=bad['track_gap']
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_exact_source_binding_and_actual_function_CPU_sensitivity=True,source_reward=dict(path=str(source),SHA=H(source)),source_task=dict(path=str(task),SHA=H(task)),matching_actual_training_package_files=exact,source_reward_bindings=bindings,actual_manifest_RM_W_RUN_VEL_ERROR=manifest['env']['RM_W_RUN_VEL_ERROR'],actual_exact_source_functions_ignore_direct_lateral_velocity_in_four_linear_terms=True,CPU15_cases=cases,forward_error_counterexample_changes_all_four_terms=True,total_reward_indirect_lateral_effects_not_ruled_out=True,captured_frozen_reward_manager_readback_preserved_in_companion_report=True,no_fresh20k_live_reward_manager_observation_claim=True,diagnostic_source_target_mismatch_candidate_not_unique_regression_cause_proof=True,adding_lateral_reward_or_changing_body_command_requires_explicit_scope_review_not_done=True,no_reward_LR_STD_command_threshold_or_GPU_mutation=True,zeroRNG0CUDA0PPO0charge=True,lookup_scup_rescue_py_missing_alias_resolved_from_actual_import=True)
 with (R/'E2_EFFECTIVE_SEALED_SOURCE_LINEAR_REWARDS_DIRECT_VY_INSENSITIVITY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(actual_source_linear_terms_direct_vy_insensitive=True,cases=len(cases),training_package_files_exact=len(exact),no_reward_change=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E2_LINEAR_REWARD_BINDING_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_reward_change=True),f,indent=2)
  raise
