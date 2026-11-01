"""Only NEW240 complete formal CPU once. Input2050/E0/native PT0."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import argparse,hashlib,io,json,math,time,traceback
from normal240_common import *
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--caller-index-SHA',required=True);a=parser.parse_args()
 verify_index(N/INDEX,a.caller_index_SHA)
 c=read(R/'ROOT240V2_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
 assert c['passed_collection'] and c['owner_closed']['canonical_None'] and c['owner_closed']['shared_locks_free']
 assert set(c['formals'])=={'jump_72'} and c['roles']['jump_72']['qualified_formal']
 f=c['formals']['jump_72'];r=c['roles']['jump_72'];p=Path(f['path'])
 assert f['transfers']==1 and f['two_host_SHA_equal'] and r['private_EX_free'] and r['actual_material_limit_error_count']==0
 assert p.resolve().is_relative_to((N/'current_closed240_models/jump_72/formal').resolve()) and p.name=='model_final.pt' and f['SHA']!=SHA
 put('ROOT240V2_NEW_FORMAL_CPU_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),NEW_formal_byte_hash_decode_max=1,input2050_E0_native_normal86_PT_reads=0,CUDA_allowed=False))
 import torch
 assert not torch.cuda.is_initialized()
 with p.open('rb')as stream:b=stream.read()
 assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['SHA']
 ck=torch.load(io.BytesIO(b),map_location='cpu',weights_only=False);del b
 count=0;bad=[]
 def finite(v,path='root'):
  nonlocal count
  if torch.is_tensor(v):
   count+=1
   if(v.is_floating_point()or v.is_complex())and not torch.isfinite(v).all():bad.append(path)
  elif isinstance(v,(float,complex)):
   assert math.isfinite(v.real)and math.isfinite(v.imag),path
  elif isinstance(v,dict):
   for k,x in v.items():finite(x,path+'.'+str(k))
  elif isinstance(v,(list,tuple)):
   for i,x in enumerate(v):finite(x,path+'.'+str(i))
 finite(ck);assert not bad
 updates=ck['actual_new_PPO_updates'];steps=[float(x['step'])for x in ck['optimizer_state_dict']['state'].values()]
 assert updates>0 and len(steps)==17 and min(steps)==max(steps)==ADAM+20*updates and ck['iter']==ITER+updates
 actor=ck['actor_state_dict'];critic=ck['critic_state_dict']
 assert len(actor)==9 and len(critic)==8 and actor['mlp.0.weight'].shape==(128,35) and actor['mlp.6.weight'].shape==(6,32)
 assert critic['mlp.0.weight'].shape==(128,38)and critic['mlp.6.weight'].shape==(1,32)
 assert actor['distribution.std_param'].shape==(6,)and(actor['distribution.std_param']>0).all()
 task=ck['typed_MODEL2050_MIX240_task']
 assert task['kind']=='MODEL2050_ORIGINAL_FUDAN_JUMP90_E0_GROUND10_400N50_FULLSTATE_V240'
 assert task['source_SHA']==SHA and task['source_bytes']==BYTES and task['source_iteration']==ITER and task['source_Adam_step']==ADAM and task['source_LR']==LR
 assert task['source_ONNX_actor_identity_passed']and task['source_hidden']==[128,64,32]and task['literal_original_reward_bytes_unchanged']
 assert task['physics_dt']==.0025 and task['TGS']==[32,4]and task['policy_hz']==50 and task['feedback_hz']==100 and task['gas_nominal_k']==2000
 assert task['closure_m']==.002 and task['mimic_rad']==.01 and task['D0white_v3_D1_D7'] and task['source_physics_and_DR_not_restored']
 assert task['ground_envs']==2000 and task['jump_envs']==18000 and task['num_envs']==20000 and task['ground_reward_original_E0_separate']
 assert ck['source_parent_branch_SHA']==SHA
 dr=ck['target_DR_state']
 assert set(dr)=={'sensor','feedback','physical_action','spring','damping','COM','PD','mild','global_CPU_rng','global_CUDA_rng','command_rngs'}
 assert torch.is_tensor(dr['global_CPU_rng'])and dr['global_CPU_rng'].dtype==torch.uint8 and len(dr['global_CUDA_rng'])>0
 assert all(k in dr['mild']for k in ('factor','nominal','mu','reset_count','private_GPU_rng','private_CPU_rng','motor_output'))
 mixed=ck['mixed_ground_JUMP_state'];flat=mixed['flat_mask'];mode=mixed['mode']
 assert flat.shape==(20000,)and flat.dtype==torch.bool and int(flat.sum())==2000
 assert mode.shape==(20000,)and torch.equal(mode,(~flat).long())and mixed['height'].shape==(20000,1)
 assert mixed['frozen_E0_reference_immutable'] and 'private_E0_mode_rng'in mixed['command']
 memory=ck['original_jump_reward_memory']
 assert set(memory)=={'episode_sums','base_air_time','last_contacts','contact_filt','was_in_flight','last_actions','last_root'}
 assert memory['base_air_time'].shape==(20000,)and memory['last_contacts'].shape==(20000,2)
 assert memory['last_actions'].shape==(20000,6,2)and memory['last_root'].shape==(20000,3)
 assert updates==r['final']['actual_new_PPO_updates']==r['formal']['actual_new_PPO_updates']
 assert ck['iter']==r['formal']['saved_iteration']and steps[0]==r['formal']['Adam_min']==r['formal']['Adam_max']
 go=c['owner_closed']['cohort_final']['go']['jump_72'];validate_original_go(go,c['run_id'])
 saved=r['formal']['epoch'];assert saved>=go['save_deadline']
 assert r['source_readcounts_before_Appclose']['source_physical_byte_opens']==r['source_readcounts_before_Appclose']['source_decodes']==1
 assert r['original_node_terminal']['row']['returncode']==0 and r['original_node_exit']['all_own_children_waited']and r['original_node_exit']['private_EX_released']
 row=dict(passed=True,path=str(p),bytes=f['bytes'],SHA=f['SHA'],finite_tensors=count,new_PPO_updates=updates,new_own_transitions=updates*480000,
  saved_iteration=ck['iter'],Adam17_step=steps[0],actor35_critic38_STD6=True,hidden=[128,64,32],complete_task_DR_and_persistent_ground_JUMP_state=True,
  actual_saved_optimizer_LR=[x['lr']for x in ck['optimizer_state_dict']['param_groups']],actual_saved_epoch=saved,save_at_or_after_requested_deadline=True,
  actual_GO=go,not_stable_jump270_or_full_SuperMimic_graduation=True)
 put('ROOT240V2_NEW_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,roles=dict(jump_72=row),NEW_formal_reads=1,old_model_reads=0,CUDA_initialized=torch.cuda.is_initialized()))
 print(json.dumps(dict(passed=True,iteration=ck['iter'],updates=updates,Adam17=steps[0],finite_tensors=count)))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT240V2_NEW_FORMAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_promotion=True));raise
