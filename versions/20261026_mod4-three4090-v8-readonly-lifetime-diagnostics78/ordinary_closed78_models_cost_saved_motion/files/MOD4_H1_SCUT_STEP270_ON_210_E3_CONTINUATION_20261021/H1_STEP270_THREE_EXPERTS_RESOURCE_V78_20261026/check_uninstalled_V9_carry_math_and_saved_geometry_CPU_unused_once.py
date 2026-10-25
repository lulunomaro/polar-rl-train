"""Pure CPU algebra/source review and prior small derived geometry, no raw/model/policy/physics."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,time,traceback
import numpy as np
import torch
N=Path(__file__).resolve().parent;T=N.parent;M=T/'H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026';R=M/'reports'
try:
 old=(M/'reference_sources/actual78_V8_reward.original_bytes.txt').read_text('utf8');p=M/'candidate_v1/h1_step270_path_reward_v1.py';new=p.read_text('utf8')
 before=ast.parse(old);after=ast.parse(new)
 recipe=next(x.value for x in after.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RECIPE' for t in x.targets));v=next(x for x in recipe.keywords if x.arg=='version');assert ast.literal_eval(v.value)=='step270_full_path_clearance_carry_v9_reward_only';v.value=ast.Constant('step270_sampled_leg_excess_v8_reward_only')
 fn=next(x for x in after.body if isinstance(x,ast.FunctionDef) and x.name=='path_increment');joint=next(x for x in fn.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='joint' for t in x.targets));assert ast.dump(joint)==ast.dump(ast.parse("joint=((current-.10)/(RECIPE['path_target_x_m']-.10)).clamp(0.,1.)*clearance.square()").body[0]);joint.value=ast.parse('((current-.10)/.25).clamp(0.,1.)*clearance.square()',mode='eval').body
 assert ast.dump(before)==ast.dump(after)
 spec=importlib.util.spec_from_file_location('uninstalled_carry_v9_math',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 rng=torch.get_rng_state().clone();n=20000;front=torch.linspace(-.10,.75,n);h=torch.full((n,),.27);origin=torch.zeros(n);two=lambda x:x[:,None].expand(n,2).clone();yes=torch.ones(n,dtype=torch.bool);no=~yes
 def calc(prev,cur,previous):
  return mod.path_increment(previous_front=two(prev),current_front=two(cur),wheel_bottom=two(h),origin_x=origin,active=yes,airborne=yes,launched=yes,clean_upright=yes,vx=torch.full((n,),.8),takeoff=no,edge_event=no,landing=no,recovery=no,previous_joint_potential=previous)
 keep=front.clone();r=calc(front,front,((front-.10)/.50).clamp(0,1));assert torch.count_nonzero(r['clearance_transport'])==0
 a=torch.full((n,),.35);b=torch.full((n,),.60);ab=calc(a,b,torch.full((n,),.5));ba=calc(b,a,torch.ones(n));assert torch.equal(ab['clearance_transport'],torch.full((n,),4.)) and torch.equal(ab['clearance_transport']+ba['clearance_transport'],torch.zeros(n))
 assert torch.equal(front,keep) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 scopes=[]
 for window in (76,77):
  U=T/f'H1_STEP270_CLOSED{window}_SAVED_REPLAY_AFTER_V8_20261026'
  with np.load(U/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False) as z,np.load(U/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False) as k:
   front=k['wheel_max'][:,:,:,0].min(-1);rear=k['wheel_min'][:,:,:,0].min(-1);bottom=k['wheel_min'][:,:,:,2].min(-1);clearance=np.clip(bottom/.27,0,1);old_joint=np.clip((front-.10)/.25,0,1)*clearance**2;new_joint=np.clip((front-.10)/.50,0,1)*clearance**2
   mask=z['continuous_no_reset'][None,:]&(z['takeoff_count']>0)&(bottom>=.27)&(front>=.35)
   saturated=mask&(old_joint>=1-1e-6)&(rear<.35)
   scopes.append(dict(window=window,scope='Existing small derived selected48controls only, no new extraction/raw read; not matched cohorts or reward replay',continuous_launched_clear_leading_cross_envframes=int(mask.sum()),old_potential_saturated_while_rear_before_edge_envframes=int(saturated.sum()),hypothetical_new_joint_on_these_mean=float(new_joint[saturated].mean()) if saturated.any() else None,no_actual_reward_or_return_recomputed=True))
 result=dict(epoch=time.time(),passed_CPU_math_and_source_only=True,exact_AST_changes=['recipe version','one path_increment joint denominator expression'],other_reward_V8_sample_excess_gate_weights_and_all_code_exact=True,float32_environments=n,stationary_zero_increment=True,signed_forward_reverse_telescopes=True,old_leading_edge_saturation1_new_at_edge_point5_new_existing_target1=True,old_total_potential_scale8_retained=True,saved_geometry_descriptions=scopes,no_model_raw_remote_GPU_policy_physics_or_current78_change=True,not_installed_admitted_or_learning_gain=True,future_source_checker_SDK_CPU_and_new_namespace_required=True)
 with (R/'V9_UNINSTALLED_CARRY_MATH_AND_PRIOR_DERIVED_GEOMETRY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
 print(json.dumps(result))
except BaseException:
 with (R/('V9_MATH_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_current_training_change=True,no_same_once_rerun=True),f,indent=2)
 raise
