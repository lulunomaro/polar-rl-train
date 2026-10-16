"""Future3060 source/recipe preparation while three training admissions continue."""
from pathlib import Path
import os,sys,time,json,hashlib,ast,copy,importlib.util,math
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
V=Path(__file__).resolve().parent;W=V.parent;U=W/'MOD4_UNIFIED_THREE_SLOT_H1_E2_E3_HANDOFF_20261017';R=V/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 source=U/'actual_human_recovered_three_slot_models/e2/model_update109.pt';expected='bccaf44227c286fee70518b61e3e3ead154c47caf2d5865d80b29b69716fdb33';assert H(source)==expected;rng=torch.get_rng_state().clone();torch.set_num_threads(2);ck=torch.load(source,map_location='cpu',weights_only=False)
 old=U/'e2_final112_frozen_source_guard_CPU_v1.py';s=old.read_text('utf8').replace('expected_step=651640','expected_step=653820').replace("['owned_phase_complete_updates']==112","['owned_phase_complete_updates']==109");adapter=s+'''
def build_E2_closed109_frozen_policy(vec,path,device):
 from pathlib import Path
 import hashlib
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()=='bccaf44227c286fee70518b61e3e3ead154c47caf2d5865d80b29b69716fdb33'
 checkpoint=torch.load(path,map_location='cpu',weights_only=False);validate_E2_source(checkpoint)
 assert checkpoint.get('history_architecture',{}).get('variant','A0')=='A0'
 assert [list(checkpoint['actor_state_dict'][k].shape) for k in ('mlp.0.weight','mlp.2.weight','mlp.4.weight','mlp.6.weight')]==[[256,35],[128,256],[64,128],[6,64]]
 # Existing observer advances one35-input decision/history tick; selectedreset only same rows.
 # Actual target must bind its original bytes/SDK and validate saved35-to-mean behavior.
 from frozen_history_policy import build_frozen_policy
 return build_frozen_policy(vec,path,device)
''';ast.parse(adapter);p=V/'e2_closed109_frozen35_source_adapter_v1.py';assert not p.exists();p.write_text(adapter,encoding='utf8');sp=importlib.util.spec_from_file_location('new_E2_source_guard_CPU_only',p);a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);good=a.validate_E2_source(ck);neg=[]
 for name in ('sourcekind','yawcap','sourcewidth','Adamstep','NaNstd','missing_typed','actor_inputdim','fake_E1_only','wrong_updates'):
  bad=copy.deepcopy(ck)
  if name=='sourcekind':bad['owned_new_expert_task']['kind']='E1_CURB35'
  elif name=='yawcap':bad['E2_moving4_command_state']['moving_yaw_cap']=6.
  elif name=='sourcewidth':bad['sensor_DR_state']['n']=80
  elif name=='Adamstep':next(iter(bad['optimizer_state_dict']['state'].values()))['step']+=1
  elif name=='NaNstd':bad['actor_state_dict']['distribution.std_param'][0]=float('nan')
  elif name=='missing_typed':del bad['sensor_physical_DR_rng_state']
  elif name=='actor_inputdim':bad['actor_state_dict']['mlp.0.weight']=bad['actor_state_dict']['mlp.0.weight'][:,:34]
  elif name=='fake_E1_only':bad['E1_terrain_state']={'fake':True};del bad['E2_moving4_command_state']
  elif name=='wrong_updates':bad['owned_phase_complete_updates']=112
  try:a.validate_E2_source(bad)
  except (AssertionError,KeyError):neg.append(name)
  else:raise AssertionError(name)
 groups=[dict(name='stand',vx=0.,vy=0.,wz=0.),dict(name='straight0p3',vx=.3,vy=0.,wz=0.),dict(name='straight1p0',vx=1.,vy=0.,wz=0.)]
 for direction in (0.,math.pi/2,math.pi/3,math.pi):
  for sign in (1.,-1.):groups.append(dict(name='world_'+str(len(groups)-3),profile='world_directional',world_speed_goal_m_s=.5,world_direction_rad=direction,signed_yaw_rad_s=4*sign,body_command_rule='vx=2Vcos(heading-direction),vy=0; original cap1.5m/s',no_live_position_correction_or_teacher=True))
 recipe=dict(id='E2_CLOSED109_SIGNED4_WORLD_V0P5_FROZEN_RECIPE_CPU_V1',source=dict(path=str(source),bytes=source.stat().st_size,SHA=expected,all17Adam653820=True,updates109=True),num_envs88_pergroup8=True,groups=groups,steps1500_dt0p01_callbacks6000=True,native120_before_full1500_required=True,seed20260928=True,profile='white_v3',normal35_mode_onehot=[1,0,0,0,0,0,0],policy_inputs35_previous_actual_clipped6_selectedreset_only=True,source35_actor9_only_on_GPU_no_optimizer_critic20kDRrestore=True,route_duration15s_ideal_goal7p5m_not_actual_performance=True,actual_route_boundary_ground_query_truncation_resource_SDK_native_not_yet_audited=True,original_ordinary_truncations_valid_failedprefixes_retained=True,no_old_1or2yaw_results_relabelled4=True,not_matched_old_S5_devseed_scope=True,not_GPU_dispatched_or_skill_pass=True)
 f=V/'E2_CLOSED109_SIGNED4_WORLD_V0P5_FROZEN_RECIPE_CPU_V1.json';assert not f.exists();f.write_text(json.dumps(recipe,indent=2),encoding='utf8');assert len(groups)==11 and len([g for g in groups if g.get('signed_yaw_rad_s')==4])==4 and len([g for g in groups if g.get('signed_yaw_rad_s')==-4])==4
 theta=torch.linspace(-8*math.pi,8*math.pi,8193,dtype=torch.float64);maxerror=0.
 for g in groups[3:]:
  v=2*.5*torch.cos(theta-g['world_direction_rad']);assert float(v.abs().max())<=1. and torch.isfinite(v).all();assert float((v.clamp(-1.5,1.5)-v).abs().max())==0
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();template=W/'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015/payload/frozen_shared/runtime/isaac/mod4/frozen_history_policy.py';entry=V/'payload/e2/job0/runtime/isaac/mod4/train_E2_full_resume_v1.py';assert 'activation="elu"' in entry.read_text('utf8');out=dict(epoch=time.time(),passed_source_recipe_CPU_only=True,source_guard=good,all9_badsource_rejected=neg,adapter=dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)),recipe=dict(path=str(f),bytes=f.stat().st_size,SHA=H(f)),original_A0_frozen_template=dict(path=str(template),bytes=template.stat().st_size,SHA=H(template)),actual_source_actor_architecture=[256,128,64],actual_source_ELU_entry_SHA=H(entry),new_recipe88env11groups8each_signed4_both_signs_4directions=True,ideal_command_peak1p0_no_clipping_not_a_physics_pass=True,original_reference_heading_transform_not_position_feedback=True,future_requires_target_sourcefreeze_whole_native_physical_query_contact_COM_hardware_all_saved_CPUmeans=True,old_low_yaw_template_only_source_not_new4qualification=True,not_GPU_SDK_or_native_or_fullroute_pass=True,CPU_RNG_unchanged0CUDA0optimizer=True,remaining=['Freeze/package exact source adapter into original3060 observed loader with SDK/resource/MSVCRT and own unused native/full lease.','Actually audit15s route/termination/ground/query and preserve all failedprefixes; do not silently change or disable bounds.','Run own native120/full1500-6000callbacks and independent whole35/action/query/contactCOMhardware CPU review.','Retain current newtraining separate from frozenqualification, oldsource and S5matchedfairseeds.']);q=R/'E2_CLOSED109_NEW_FROZEN_SOURCE_ADAPTER_SIGNED4_RECIPE_CPU_PREPARED_ACTUAL.json';assert not q.exists();q.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(source_SHA=expected,CPU_badsource_rejected=len(neg),recipe_groups11_envs88=True,frozen_GPU_not_dispatched=True)),flush=True)
if __name__=='__main__':main()
