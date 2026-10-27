"""Declared source qualification/migration: one original E2 CPU read, no policy call."""
from pathlib import Path
import copy,hashlib,json,os,time,traceback
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
SOURCE=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/current_three_closed_models/e2/model_update90.pt'
SHA='72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,v):
 with (B/'reports'/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def exact(a,b,torch):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.shape==b.shape and a.dtype==b.dtype and torch.equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k],torch) for k in a)
 if isinstance(a,(list,tuple)):return type(a)is type(b) and len(a)==len(b) and all(exact(x,y,torch) for x,y in zip(a,b))
 return type(a)is type(b) and a==b
def tensors(v,p=''):
 import torch
 if torch.is_tensor(v):yield p,v
 elif isinstance(v,dict):
  for k,x in v.items():yield from tensors(x,p+'/'+str(k))
 elif isinstance(v,(tuple,list)):
  for k,x in enumerate(v):yield from tensors(x,p+'/'+str(k))
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 assert not (B/'typed_source').exists();put('E2_DECLARED_ORIGINAL_SOURCE_CPU_MIGRATION_STARTED.json',dict(epoch=time.time(),purpose='Original E2 fullstate source qualification and exact old700 to400 recipe migration, one original PT load',source_path=str(SOURCE),source_SHA=SHA,no_GPU_remote_account_or_policy=True))
 import torch
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();assert H(SOURCE)==SHA
 ck=torch.load(SOURCE,map_location='cpu',weights_only=False)
 assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
 assert len(ck['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={857460}
 assert ck['spring_pressure_state']['n']==20000 and ck['physical_action_delay_state']['control_us']==ck['physical_action_delay_recipe']['control_period_us']==20000
 assert ck['spring_pressure_recipe']['nominal_stiffness_N_m']==3500 and ck['spring_pressure_recipe']['actual_stiffness_bounds_N_m']==[3150,3850]
 assert ck['E2_moving4_command_state']['kind']=='E2_WORLD_MOVING_SIGNED4' and ck['E2_moving4_command_state']['moving_yaw_cap']==4.
 leaves=list(tensors(ck));assert all(x.device.type=='cpu' and (not x.is_floating_point() or bool(torch.isfinite(x).all())) for _,x in leaves)
 value=copy.deepcopy(ck);value['spring_pressure_recipe']['nominal_stiffness_N_m']=2000;value['spring_pressure_recipe']['actual_stiffness_bounds_N_m']=[1800,2200]
 inverse=copy.deepcopy(value);inverse['spring_pressure_recipe']=copy.deepcopy(ck['spring_pressure_recipe']);assert exact(inverse,ck,torch)
 meta=dict(schema='mod4.E2.originalN20K.PPO50_gas400.v1',role='E2',original_source_path=str(SOURCE),original_source_SHA=SHA,original_iteration=ck['iter'],original_Adam_step=857460,original_population=20000,target_population=20000,actor35_critic38_original=True,two_pressure_recipe_fields_changed_only=True,original50Hz_clock_queue_history_not_rescaled=True,core_STD_optimizer_LR_D1_D7_private_global_E2_command_RNG_literal_original=True,policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,solver='TGS32/4',gas_force_N_each=400,gas_nominal_k_N_m=2000,gas_upper_q_m=.020639440248416612,gas_lower_q_m=-.0267046843609,gas_damping_Ns_m=3,hardware_force_curve_calibrated=False,same_PhysX_resume=False,new_adaptation_skill_qualified=False,original_frozen_label_unchanged=True,target_CUDA_restore_and_GPU_training_admitted=False,producer_path=str(Path(__file__).resolve()),producer_SHA=H(__file__))
 value['PPO50_gas400_adaptation']=meta;(B/'typed_source').mkdir();target=B/'typed_source/E2_83B90_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt';torch.save(value,target)
 roundtrip=torch.load(target,map_location='cpu',weights_only=False);assert exact(value,roundtrip,torch)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('E2_TYPED400_SOURCE_ORIGINAL_CLOCK_FULLSTATE_CPU_ACTUAL_V1.json',dict(passed=True,epoch=time.time(),source=meta,new_source=dict(path=str(target),bytes=target.stat().st_size,SHA=H(target)),original_optimizer_param_groups=ck['optimizer_state_dict']['param_groups'],original_constructor_learning_rate=ck['optimizer_state_dict']['param_groups'][0]['lr'],source_tensor_count=len(leaves),all_fullstate_finite=True,inverse_entire_original_state_equal=True,one_original_source_CPU_load=True,one_NEW_typed_roundtrip_CPU_load=True,target_SDK_CUDA_restore_native24_and_PPO_pending=True,WM_transition_collection_executed=False))
 print(json.dumps(dict(passed=True,new_source=str(target),SHA=H(target),iteration=ck['iter'],Adam=857460,LR=ck['optimizer_state_dict']['param_groups'][0]['lr'])))
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_TYPED_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_reload_or_promotion=True));raise
