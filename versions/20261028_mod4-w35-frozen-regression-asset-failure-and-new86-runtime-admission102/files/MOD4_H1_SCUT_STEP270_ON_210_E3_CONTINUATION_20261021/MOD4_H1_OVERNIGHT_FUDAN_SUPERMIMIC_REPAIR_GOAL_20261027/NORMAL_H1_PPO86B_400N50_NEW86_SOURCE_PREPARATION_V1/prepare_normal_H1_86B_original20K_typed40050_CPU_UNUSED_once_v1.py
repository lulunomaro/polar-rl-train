"""One declared normal-H1 fullstate migration; no native models, policy calls or GPU."""
from pathlib import Path
import copy,hashlib,json,os,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent
SOURCE=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/current_baseline_closed_models/h1/model_update138.pt'
SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'

def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def exact(a,b,torch):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k],torch) for k in a)
 if isinstance(a,(list,tuple)):return type(a)is type(b) and len(a)==len(b) and all(exact(x,y,torch) for x,y in zip(a,b))
 if type(a).__module__.startswith('numpy') and hasattr(a,'shape'):
  import numpy as np
  return type(a)is type(b) and a.dtype==b.dtype and a.shape==b.shape and bool(np.array_equal(a,b))
 return type(a)is type(b) and a==b

def leaves(v,p=''):
 import torch
 if torch.is_tensor(v):yield p,v
 elif isinstance(v,dict):
  for k,x in v.items():yield from leaves(x,p+'/'+str(k))
 elif isinstance(v,(tuple,list)):
  for i,x in enumerate(v):yield from leaves(x,p+'/'+str(i))

def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')=='';R.mkdir(exist_ok=True);assert not (B/'typed_source').exists();put('NORMAL_H1_DECLARED_CPU_MIGRATION_STARTED_ACTUAL.json',dict(epoch=time.time(),purpose='ordinary normal-H1 PPO86B fullstate qualification plus exactly four400N50Hz recipe fields; not nativeH1 or frozenRSL witness editing',source_path=str(SOURCE),source_SHA=SHA,one_original_source_CPU_load_planned=True,no_policy_forward_optimizer_remote_or_GPU=True))
 import torch
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();assert SOURCE.stat().st_size==16868635 and H(SOURCE)==SHA;ck=torch.load(SOURCE,map_location='cpu',weights_only=False)
 assert 'PPO50_gas400_adaptation' not in ck
 assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and ck['actor_state_dict']['distribution.std_param'].shape==(6,) and ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
 assert len(ck['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={832460}
 assert ck['spring_pressure_state']['n']==20000 and ck['physical_action_delay_state']['control_us']==ck['physical_action_delay_recipe']['control_period_us']==10000
 assert ck['spring_pressure_recipe']['nominal_stiffness_N_m']==3500 and ck['spring_pressure_recipe']['actual_stiffness_bounds_N_m']==[3150,3850]
 assert ck['H1_step270_task_state']['version']==270;phase=ck['H1_step270_task_state']['phase'];assert phase['version']==270 and phase['num_envs']==20000 and phase['geometry']==dict(height=.270,edge_x=.35,depth=.8,width=1.2) and phase['tensors']['age_control'].shape==(20000,)
 tensors=list(leaves(ck));assert all(t.device.type=='cpu' and (not t.is_floating_point() or bool(torch.isfinite(t).all())) for _,t in tensors)
 value=copy.deepcopy(ck);before={key:copy.deepcopy(ck[key]) for key in ['physical_action_delay_state','physical_action_delay_recipe','spring_pressure_recipe']};value['physical_action_delay_state']['control_us']=20000;value['physical_action_delay_recipe']['control_period_us']=20000;value['spring_pressure_recipe']['nominal_stiffness_N_m']=2000;value['spring_pressure_recipe']['actual_stiffness_bounds_N_m']=[1800,2200]
 inverse=copy.deepcopy(value)
 for key,item in before.items():inverse[key]=item
 assert exact(inverse,ck,torch)
 meta=dict(schema='mod4.normal_H1_PPO86B.original20K.PPO50_gas400.v1',role='normal_H1_PPO',logical_slot_candidate='h1_ppo40050_86',original_source_path=str(SOURCE),original_source_SHA=SHA,original_complete_update_count=138,original_stored_RSL_iteration=int(ck['iter']),original_Adam_step=832460,original_population=20000,target_population=20000,actor35_critic38_STD6_and17Adam_literal_original=True,original_optimizer_LR=ck['optimizer_state_dict']['param_groups'][0]['lr'],four_recipe_fields_only=True,policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,public_phase_tick_hz=100,required_public_phase_tick_increment_per_policy=2,public_request_seconds=[1.0,1.8],original_phase_tensors_and_history_and_command_RNG_retained=True,original_queue_history_not_rescaled=True,source_restore_then_one_new_actual_episode_required=True,landing_physics_callbacks=12,recovery_physics_callbacks=200,original_true270_goal_geometry_unchanged=True,original_reward_task_and_mean_overflow_loss_retained=True,gas_force_N_each=400,gas_nominal_k_N_m=2000,gas_damping_Ns_m=3,gas_upper_q_m=.020639440248416612,gas_lower_q_m=-.0267046843609,hardware_force_curve_calibrated=False,not_native101_or103_method=True,no_new_Fudan_reward_injected_into_frozen_PPO_fork=True,original_frozen_model_and_RSL_witness_bytes_unchanged=True,new_skill_qualification=False,target86_fullrestore_native24_PPO_and_sole72_admission_pending=True,producer_path=str(Path(__file__).resolve()),producer_SHA=H(__file__))
 value['PPO50_gas400_adaptation']=meta;(B/'typed_source').mkdir();target=B/'typed_source/NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt';torch.save(value,target);roundtrip=torch.load(target,map_location='cpu',weights_only=False);assert exact(value,roundtrip,torch);assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('NORMAL_H1_TYPED40050_ORIGINAL_FULLSTATE_CPU_ACTUAL_V1.json',dict(passed=True,epoch=time.time(),source=meta,new_source=dict(path=str(target),bytes=target.stat().st_size,SHA=H(target)),original_source_loaded_once=True,new_typed_roundtrip_loaded_once=True,all_original_fullstate_tensors_finite=True,original_tensor_leaf_count=len(tensors),full_original_inverse_recipe_proof=True,all_other_source_fields_literal_preserved=True,original_optimizer_param_groups=ck['optimizer_state_dict']['param_groups'],required_constructor_LR=ck['optimizer_state_dict']['param_groups'][0]['lr'],runtime_phase_clock_overlay_not_yet_executed=True,no_actor_call_or_optimizer_or_WM_data_or_GPU=True,original_top_level_keys=list(ck)))
 print(json.dumps(dict(passed=True,source_SHA=SHA,new_source_SHA=H(target),new_source_path=str(target),original_RSL_iteration=int(ck['iter']),original_Adam=832460,required_constructor_LR=ck['optimizer_state_dict']['param_groups'][0]['lr'],CPU_only_not_GPU_admitted=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);put('NORMAL_H1_TYPED_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_reload_or_model_source_promotion=True));raise
