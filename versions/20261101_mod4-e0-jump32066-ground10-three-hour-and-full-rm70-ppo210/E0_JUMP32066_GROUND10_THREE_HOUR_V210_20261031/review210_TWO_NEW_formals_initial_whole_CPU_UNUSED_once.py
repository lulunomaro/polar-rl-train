"""Future NEW complete outputs only, one CPU byte pass/decode each; no old PT."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,io,json,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
def read(p):return json.loads(p.read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 c=read(R/'ROOT210_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');specs=read(N/'SCHEDULE_V2_PUBLIC.json')['experts']
 assert c['passed_collection'] and c['owner_closed']['canonical_None'] and c['owner_closed']['shared_locks_free']
 assert c['formals'],'No complete formal to qualify; no premature model read'
 for key,x in c['formals'].items():assert x['transfers']==1 and x['two_host_SHA_equal'] and c['roles'][key]['qualified_formal'] and c['roles'][key]['private_EX_free']
 put('ROOT210_NEW_FORMALS_CPU_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),roles=list(c['formals']),maximum_NEW_formal_byte_read_and_decode_each=1,
  old_E0_W35_main_native_witness_PT_reads=0,CUDA_allowed=False))
 import torch
 assert not torch.cuda.is_initialized();reports={}
 for key,f in c['formals'].items():
  p=Path(f['path']);assert p.stat().st_size==f['bytes']
  with p.open('rb') as stream:raw=stream.read()
  assert hashlib.sha256(raw).hexdigest()==f['SHA']
  ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
  count=0;bad=[]
  def finite(v,path='root'):
   nonlocal count
   if torch.is_tensor(v):
    count+=1
    if (v.is_floating_point() or v.is_complex()) and not torch.isfinite(v).all():bad.append(path)
   elif isinstance(v,dict):
    for k,x in v.items():finite(x,path+'.'+str(k))
   elif isinstance(v,(list,tuple)):
    for i,x in enumerate(v):finite(x,path+'.'+str(i))
  finite(ck);assert not bad
  sp=specs[key];updates=ck['actual_new_PPO_updates'];steps=[float(x['step']) for x in ck['optimizer_state_dict']['state'].values()]
  assert updates>0 and len(steps)==17 and min(steps)==max(steps)==sp['source_Adamstep']+20*updates
  assert ck['iter']==sp['source_iteration']+updates
  actor=ck['actor_state_dict'];critic=ck['critic_state_dict']
  assert len(actor)==9 and len(critic)==8
  assert tuple(actor['mlp.0.weight'].shape)==(256,35) and tuple(actor['mlp.6.weight'].shape)==(6,64)
  assert tuple(critic['mlp.0.weight'].shape)==(256,38) and tuple(critic['mlp.6.weight'].shape)==(1,64)
  assert tuple(actor['distribution.std_param'].shape)==(6,)
  if key=='e0_72':
   assert ck['source_parent_branch_SHA']==sp['source_SHA']
   t=ck['typed_MIX210_task'];assert t['source_SHA']==sp['source_SHA'] and t['learning_seconds']==10800 and t['ground_envs']==2000 and t['jump_envs']==18000
   assert {'sensor','feedback','physical_action','spring','damping','COM','PD','mild','global_CPU_rng','global_CUDA_rng','command_rngs'}<=set(ck['target_DR_state'])
   assert {'base_air_time','last_contacts','contact_filt','was_in_flight','last_actions','last_root','episode_sums'}<=set(ck['original_jump_reward_memory'])
   mix=ck['mixed_ground_JUMP_state'];mask=mix['flat_mask'];mode=mix['mode']
   assert mask.shape==(20000,) and mask.dtype==torch.bool and int(mask.sum())==2000 and torch.equal(mode,(~mask).long())
   assert {'command','height','ground_reward_episode_sums','stateful_ground_rewards'}<=set(mix)
  else:
   t=ck['typed_W35_RM70_task'];assert t['source_SHA']==sp['source_SHA'] and t['policy_hz']==50 and t['nominal_gas_N_each']==400 and t['root_quaternion_order']=='xyzw'
   for name in ('sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','feedback_delay_state','physical_action_delay_state',
    'spring_pressure_state','gas_damping_state','chassis_PD_state','E1_terrain_state','E1_retained_flat_command_state'):assert name in ck,name
   terrain=ck['E1_terrain_state'];assert terrain['num_envs']==20000 and terrain['collision_SHA']=='9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b'
   assert terrain['profile']=='W35_to_original_full_RM70_arena208_v1'
   command=ck['E1_retained_flat_command_state'];assert command['num_envs']==20000 and command['profile']==terrain['profile'] and command['assignment_sha256']==terrain['collision_SHA']
  go=c['owner_closed']['cohort_final']['go'][key];saved=c['roles'][key]['formal']['epoch']
  reports[key]=dict(passed=True,path=str(p),bytes=f['bytes'],SHA=f['SHA'],finite_tensors=count,new_PPO_updates=updates,saved_iteration=ck['iter'],Adam17_step=steps[0],
   actor35_critic38_STD6=True,complete_task_and_DR_state_present=True,actual_GO=go,actual_saved_epoch=saved,
   save_at_or_after_requested_deadline=saved>=go['save_deadline'],not_skill_or_supermimic_graduation=True)
 put('ROOT210_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,roles=reports,NEW_formal_reads=len(reports),old_model_reads=0,
  CUDA_initialized=torch.cuda.is_initialized(),no_270_or_full_RM70_skill_inferred=True))
 print(json.dumps(dict(passed=True,roles={k:dict(iteration=v['saved_iteration'],Adam=v['Adam17_step'],updates=v['new_PPO_updates']) for k,v in reports.items()})))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT210_NEW_FORMAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_promotion=True));raise
