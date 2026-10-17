"""Execute sealed source functions on CPU fixtures; never infer an unrecorded live gate."""
from pathlib import Path
import os,ast,json,time,types,sys,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';C=B/'frozen_public4_final_linux_v1/payload/frozen_shared/runtime/isaac/mod4'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def function_namespace(path,names):
 tree=ast.parse(path.read_text('utf8'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert {n.name for n in nodes}==set(names)
 module=ast.Module(body=nodes,type_ignores=[]);ns={'torch':torch};exec(compile(module,str(path),'exec'),ns);return ns

def main():
 torch.set_num_threads(1);rng=torch.get_rng_state().clone();orientation=function_namespace(C/'scut_flat_rescue.py',['orientation'])['orientation'];skills=function_namespace(C/'skills_isaac.py',['_robot','_jump_active','ang_vel_xy_jump_exempt'])
 cmd=torch.zeros(4,3);g=torch.tensor([[.2,.1,-.9746794]]).repeat(4,1);omega=torch.zeros(4,3);data=types.SimpleNamespace(projected_gravity_b=g,root_ang_vel_b=omega);env=types.SimpleNamespace(scene={'robot':types.SimpleNamespace(data=data)},command_manager=types.SimpleNamespace(get_command=lambda name:cmd),num_envs=4,device='cpu',h1_phase=types.SimpleNamespace(request_for_action=torch.tensor([False,True,False,True])))
 tests=[]
 for rate in (0.,2.,10.):
  omega[:,:2]=rate
  tests.append(dict(rate_rad_s=rate,orientation_pitch=orientation(env,'pitch').tolist(),orientation_pitch_velocity_label=orientation(env,'pitch_velocity').tolist(),orientation_roll_velocity_label=orientation(env,'roll_velocity').tolist(),ang_vel_xy_with_no_legacy_jump_state=skills['ang_vel_xy_jump_exempt'](env).tolist()))
 assert all(tests[0][k]==row[k] for row in tests for k in ('orientation_pitch','orientation_pitch_velocity_label','orientation_roll_velocity_label'))
 assert tests[0]['ang_vel_xy_with_no_legacy_jump_state']==[0.]*4 and tests[2]['ang_vel_xy_with_no_legacy_jump_state']==[200.]*4
 omega[:,:2]=2.;states=[]
 for name,legacy in [('absent',None),('all_inactive',torch.zeros(4)),('all_active',torch.ones(4)),('mixed',torch.tensor([0.,1.,0.,1.]))]:
  if legacy is None:
   if hasattr(env,'_mod4_jump'):del env._mod4_jump
  else:env._mod4_jump={'active':legacy}
  out=skills['ang_vel_xy_jump_exempt'](env);states.append(dict(legacy_state=name,actual_H1_public4_requests=env.h1_phase.request_for_action.tolist(),rate_penalty=out.tolist()))
 assert states[0]['rate_penalty']==states[1]['rate_penalty']==[8.]*4 and states[2]['rate_penalty']==[0.]*4 and states[3]['rate_penalty']==[8.,0.,8.,0.]
 # Execute original configure with a CPU-only manager-constructor fixture, not an installed SDK claim.
 p=C/'h1_reward_scope_v1.py';tree=ast.parse(p.read_text('utf8'));masked=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MASKED' for t in n.targets));ns={'torch':torch};exec(compile(tree,str(p),'exec'),ns)
 class Term:
  def __init__(self,func,weight,params=None):self.func=func;self.weight=weight;self.params={} if params is None else params
 old_package=sys.modules.get('isaaclab');old_managers=sys.modules.get('isaaclab.managers');package=types.ModuleType('isaaclab');manager=types.ModuleType('isaaclab.managers');manager.RewardTermCfg=Term;package.managers=manager;sys.modules['isaaclab']=package;sys.modules['isaaclab.managers']=manager
 def original(e):return torch.tensor([1.,2.,3.,4.])
 rewards=types.SimpleNamespace(**{k:Term(original,-1.) for k in [*masked,'flat_orientation_y','flat_orientation_y_v','flat_orientation_x_v','ang_vel_xy','action_rate','action_acc','torques','joint_power']});cfg=types.SimpleNamespace(rewards=rewards)
 try:ns['configure'](cfg)
 finally:
  for name,old in [('isaaclab',old_package),('isaaclab.managers',old_managers)]:
   if old is None:sys.modules.pop(name,None)
   else:sys.modules[name]=old
 assert len(cfg._h1_reward_axis)==7
 for name in masked:
  term=getattr(rewards,name);assert term.func==ns['request_masked_original'];assert torch.equal(term.func(env,**term.params),torch.tensor([1.,0.,3.,0.]))
 untouched=['flat_orientation_y','flat_orientation_y_v','flat_orientation_x_v','ang_vel_xy','action_rate','action_acc','torques','joint_power']
 assert all(getattr(rewards,name).func is original and getattr(rewards,name).weight==-1. for name in untouched)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 # Bind actual source files to both the closed candidate and the sealed evaluation package.
 train=B/'paid_mean_public4_v2/payload/h1/job0/runtime/isaac/mod4';source_rows=[]
 for name in ['scut_flat_rescue.py','skills_isaac.py','h1_reward_scope_v1.py','h1_takeoff_progress_reward_v2.py','mod4_task.py']:
  assert H(C/name)==H(train/name);source_rows.append(dict(name=name,sealed_eval_SHA=H(C/name),closed_candidate_source_SHA=H(train/name),byteexact=True))
 out=dict(epoch=time.time(),trial_id='public4-v2-ce3-sealed-orientation-rate-masks-cpu-20261018',source_SHA='ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90',actual_source_bindings=source_rows,source_function_fixture_rate_sweep=tests,legacy_jump_active_fixture_states=states,orientation_velocity_named_terms_use_projected_gravity_and_command_not_actual_angular_rate=True,H1_seven_request_masks=masked,orientation_rate_energy_and_action_costs_not_in_H1_seven_masks=untouched,H1_public4_flag_alone_does_not_control_legacy_jump_active_rate_exemption=True,actual_ended_GPU_legacy_jump_active_readback_not_recorded_unknown=True,no_claim_actual_H1_flight_rate_penalty_was_zero_or_unique_regression_cause=True,mocked_constructor_fixture_not_actual_loaded_RewardManager_proof=True,no_reward_weight_or_function_or_gate_or_runtime_or_new_paid_window_changed=True,CPU_RNG_unchanged0CUDA0optimizer=True,lookup_miss_skills_py_corrected_to_actual_import_skills_isaac_preserved=True)
 with (R/'PUBLIC4_V2_FINAL_SEALED_ORIENTATION_RATE_REWARD_MASKS_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(orientation_velocity_labels_not_angular_rate=True,sealed_candidate_eval_sources_byteexact=True,H1_seven_masks=masked,legacy_active_remains_actual_unknown=True,no_reward_changed=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('PUBLIC4_FINAL_REWARD_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_live_reward_change=True),f,indent=2)
  raise
