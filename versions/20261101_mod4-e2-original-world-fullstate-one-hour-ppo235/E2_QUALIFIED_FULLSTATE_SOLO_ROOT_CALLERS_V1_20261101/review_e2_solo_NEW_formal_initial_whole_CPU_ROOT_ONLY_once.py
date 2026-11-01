"""ROOT-only NEW E2 complete formal CPU;one byte/decode,old model0."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import argparse,hashlib,io,json,time,traceback
from caller_common import *
import math


def read(p):return json.loads(p.read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--caller-index-SHA',required=True);args=parser.parse_args()
 from caller_common import verify_index,INDEX,validate_original_go
 verify_index(N/INDEX,args.caller_index_SHA)
 c=read(R/'ROOT_E2_SOLO_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
 assert c['passed_collection'] and c['owner_closed']['canonical_None'] and c['owner_closed']['shared_locks_free']
 assert set(c['formals'])=={'e2'} and c['roles']['e2']['qualified_formal']
 f=c['formals']['e2'];r=c['roles']['e2']
 assert f['transfers']==1 and f['two_host_SHA_equal'] and r['private_EX_free'] and r['actual_material_limit_error_count']==0
 p=Path(f['path']);assert p.resolve().is_relative_to((N/'current_closed_e2_models/e2/formal').resolve())
 assert p.name=='model_final.pt' and f['SHA']!='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
 put('ROOT_E2_SOLO_NEW_E2_FORMAL_CPU_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),roles=['e2'],
  maximum_NEW_formal_byte_read_and_decode=1,old_E2_or_other_PT_reads=0,CUDA_allowed=False))
 import torch
 assert not torch.cuda.is_initialized() and p.stat().st_size==f['bytes']
 with p.open('rb') as stream:raw=stream.read()
 assert hashlib.sha256(raw).hexdigest()==f['SHA']
 ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
 count=0;bad=[]
 def finite(value,path='root'):
  nonlocal count
  if torch.is_tensor(value):
   count+=1
   if (value.is_floating_point() or value.is_complex()) and not torch.isfinite(value).all():bad.append(path)
  elif isinstance(value,(float,complex)):
   assert math.isfinite(value.real) and math.isfinite(value.imag),'Nonfinite scalar: '+path
  elif isinstance(value,dict):
   for k,x in value.items():finite(x,path+'.'+str(k))
  elif isinstance(value,(list,tuple)):
   for i,x in enumerate(value):finite(x,path+'.'+str(i))
 finite(ck);assert not bad
 updates=ck['actual_new_PPO_updates'];steps=[float(x['step']) for x in ck['optimizer_state_dict']['state'].values()]
 assert updates>0 and len(steps)==17 and min(steps)==max(steps)==859300+20*updates
 assert ck['iter']==42822+updates
 actor=ck['actor_state_dict'];critic=ck['critic_state_dict']
 assert len(actor)==9 and len(critic)==8
 assert tuple(actor['mlp.0.weight'].shape)==(256,35) and tuple(actor['mlp.6.weight'].shape)==(6,64)
 assert tuple(critic['mlp.0.weight'].shape)==(256,38) and tuple(critic['mlp.6.weight'].shape)==(1,64)
 assert tuple(actor['distribution.std_param'].shape)==(6,)
 t=ck['typed_E2_original_world_PPO_task'];assert t['source_SHA']==SHA and t['source_bytes']==BYTES
 assert t['kind']==WORKER_KIND and t['source_iteration']==ITER and t['source_Adam_step']==ADAM and t['source_LR']==LR
 assert t['actor_obs']==35 and t['critic_obs']==38 and t['action_dim']==6 and t['num_envs']==20000
 assert t['policy_hz']==50 and t['feedback_hz']==100 and t['nominal_gas_N_each']==400 and t['physics_dt']==.0025 and t['TGS']==[32,4]
 assert t['domain_kind']=='E2_WORLD_MOVING_SIGNED4' and t['sampler_stage']=='world_directional_v1'
 for key in ('source_command_state_and_named_global_RNG_restored_before_one_new_physical_episode',
  'original_world_goal_point5_and_body_pure_transition_stand_mix_retained','source_STD_17Adam_and_LR_retained'):assert t[key] is True,key
 assert t['PhysX_exact_resume_claimed'] is False and t['full_E2_skill'] is False and t['full_SuperMimic'] is False
 assert updates==r['final']['actual_new_PPO_updates']==r['formal']['actual_new_PPO_updates']
 assert ck['iter']==r['formal']['saved_iteration'] and min(steps)==r['formal']['Adam_min']==r['formal']['Adam_max']
 assert r['formal']['all_saved_tensor_and_scalar_numbers_finite'] and r['formal']['original_E2_command_state_and_private_RNG_saved']
 for name in ('sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state',
  'feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state',
  'E2_moving4_command_state'):assert name in ck,name
 cmd=ck['E2_moving4_command_state'];assert cmd['version']==1 and cmd['kind']=='E2_WORLD_MOVING_SIGNED4' and cmd['moving_yaw_cap']==4.
 fields={'is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin','world_direction','signed_yaw','phase_elapsed','vel_command_b'}
 assert set(cmd['tensors'])==fields and all(torch.is_tensor(v) and v.shape[0]==20000 for v in cmd['tensors'].values())
 assert torch.is_tensor(cmd['private_mode_rng']) and cmd['private_mode_rng'].dtype==torch.uint8 and cmd['private_mode_rng'].numel()>0
 assert r['source_readcounts_before_Appclose']['source_physical_byte_opens']==r['source_readcounts_before_Appclose']['source_decodes']==1
 assert r['original_node_terminal']['row']['returncode']==0 and r['original_node_exit']['all_own_children_waited'] and r['original_node_exit']['private_EX_released']
 go=c['owner_closed']['cohort_final']['go']['e2'];validate_original_go(go,c['run_id']);saved=r['formal']['epoch'];assert saved>=go['save_deadline']
 row=dict(passed=True,path=str(p),bytes=f['bytes'],SHA=f['SHA'],finite_tensors=count,new_PPO_updates=updates,
  saved_iteration=ck['iter'],Adam17_step=steps[0],actor35_critic38_STD6=True,complete_task_and_DR_state_present=True,
  source_initial_LR=.00022500000000000002,actual_saved_optimizer_LR=[g['lr'] for g in ck['optimizer_state_dict']['param_groups']],
  actual_GO=go,actual_saved_epoch=saved,save_at_or_after_requested_deadline=saved>=go['save_deadline'],
  not_skill_or_supermimic_graduation=True)
 put('ROOT_E2_SOLO_NEW_E2_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,roles=dict(e2=row),
  NEW_formal_reads=1,old_model_reads=0,CUDA_initialized=torch.cuda.is_initialized(),no_E2_skill_inferred=True))
 print(json.dumps(dict(passed=True,iteration=ck['iter'],Adam=steps[0],updates=updates)))


if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT_E2_SOLO_NEW_FORMAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_promotion=True));raise
