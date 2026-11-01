"""One NEW WM-warm formal CPU decode. All old models/raw remain unread."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import argparse,hashlib,io,json,math,time,traceback
from reader281_common import *
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--caller-index-SHA',required=True);a=p.parse_args();verify_index(D/INDEX,a.caller_index_SHA)
 j=read(R/'ROOT276_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
 assert j['passed_collection']and j['owner_closed']['canonical_None']and j['owner_closed']['shared_locks_free']and set(j['formals'])=={'jump_72'}
 role=j['roles']['jump_72'];f=j['formals']['jump_72'];path=Path(f['path'])
 assert role['qualified_formal']and role['private_EX_free']and role['actual_material_limit_error_count']==0 and f['transfers']==1 and f['two_host_SHA_equal']
 assert path.resolve().is_relative_to((N/'current_closed276_models/jump_72/formal').resolve())and path.name=='model_final.pt'
 put('ROOT281_NEW_FORMAL_CPU_PURPOSE_CONSUMED_BEFORE_READ.json',dict(epoch=time.time(),NEW_WM_formal_byte_hash_decode_max=1,old_teacher_E0_native_raw_reads=0,CUDA_allowed=False))
 import torch
 assert not torch.cuda.is_initialized()
 with path.open('rb')as stream:b=stream.read()
 assert len(b)==f['bytes']and hashlib.sha256(b).hexdigest()==f['SHA'];ck=torch.load(io.BytesIO(b),map_location='cpu',weights_only=False);del b
 count=0
 def finite(v):
  nonlocal count
  if torch.is_tensor(v):
   count+=1
   if v.is_floating_point()or v.is_complex():assert torch.isfinite(v).all()
  elif isinstance(v,(float,complex)):assert math.isfinite(v.real)and math.isfinite(v.imag)
  elif isinstance(v,dict):
   for x in v.values():finite(x)
  elif isinstance(v,(list,tuple)):
   for x in v:finite(x)
 finite(ck)
 from wm_task275 import validate_task,validate_final,SOURCE_SHA
 task=ck['typed_WM_WARM276_task'];validate_task(task);go=ck['original_finite_owner_GO'];validate_original_go(go,j['run_id']);validate_final(role['final'],task,go)
 u=ck['actual_new_WM_updates'];assert u>0 and u==role['formal']['saved_WM_updates']and ck['actual_new_PPO_updates']==ck['actual_Pi_Critic_STD_updates']==0
 assert ck['kind']=='OWN_DEPTH_WM_ONLY_WARM276_COMPLETE'and ck['teacher_source_SHA']==SOURCE_SHA and ck['teacher_saved_iteration']==2135 and ck['teacher_Adam17_step']==42940
 teacher=ck['teacher_full_PPO_state'];assert teacher['iter']==2135
 actor=teacher['actor_state_dict'];critic=teacher['critic_state_dict'];steps=[float(v['step'])for v in teacher['optimizer_state_dict']['state'].values()]
 assert len(steps)==17 and min(steps)==max(steps)==42940 and teacher['optimizer_state_dict']['param_groups'][0]['lr']==.0019461950683593758
 assert len(actor)==9 and actor['mlp.0.weight'].shape==(128,35)and actor['mlp.6.weight'].shape==(6,32)and actor['distribution.std_param'].shape==(6,)and(actor['distribution.std_param']>0).all()
 assert len(critic)==8 and critic['mlp.0.weight'].shape==(128,38)and critic['mlp.6.weight'].shape==(1,32)
 wm=ck['world_model'];ws=[int(v['step'])for v in wm['world_optimizer']['state'].values()];assert ws and min(ws)==max(ws)==u and wm['world_updates']==u
 assert wm['world_model']['net.0.weight'].shape==(512,273)and wm['world_model']['net.9.weight'].shape==(223,512)
 assert wm['future_safe_WM_warm_schema']=='V273_FIRST_CURRENT_ANCHOR_ONLY'and wm['teacher_contract']['checkpoint_SHA']==SOURCE_SHA
 assert wm['teacher_and_Pi_updates']==0 and wm['complete_three_optimizer_conversion']is False and wm['actual_Pi_runtime_qualified']is False and wm['replay_saved']is False
 assert ck['complete_three_optimizer_conversion']is False and ck['actual_Pi_runtime_qualified']is False and ck['full_physics_resume_claimed']is False
 dr=ck['target_DR_state'];assert set(dr['components'])=={'sensor','feedback','physics_action_queue','spring','damping','COM','PD'}
 assert set(dr['mild'])=={'factor','nominal','mu','reset_count','private_GPU_rng','private_CPU_rng','motor_output'}and dr['global_CPU_rng'].dtype==torch.uint8 and len(dr['global_CUDA_rng'])>0
 mixed=ck['mixed_ground_JUMP_state'];flat=mixed['flat_mask'];assert flat.shape==(80,)and flat.dtype==torch.bool and int(flat.sum())==8 and torch.equal(mixed['mode'],(~flat).long())
 assert 'stateful_ground_rewards'in mixed and 'generators'in mixed
 memory=ck['original_jump_reward_memory'];assert set(memory)=={'episode_sums','base_air_time','last_contacts','contact_filt','was_in_flight','last_actions','last_root'}
 assert memory['base_air_time'].shape==(80,)and memory['last_contacts'].shape==(80,2)and memory['last_actions'].shape==(80,6,2)
 assert ck['current_measured_state224'].shape==(80,224)and ck['current_static31'].shape==(80,31)and ck['previous_clipped_action'].shape==(80,6)
 controls=ck['controls'];assert controls*80==ck['own_transitions']and controls*8==ck['physics_callbacks']and controls*2==ck['feedback_samples']and role['formal']['save_epoch']>=go['save_deadline']
 row=dict(passed=True,epoch=time.time(),path=str(path),bytes=f['bytes'],SHA=f['SHA'],finite_tensors=count,actual_new_WM_updates=u,controls=controls,new_own_transitions=controls*80,frozen_teacher_iteration=2135,frozen_teacher_Adam17=42940,NEW_formal_reads=1,old_model_raw_reads=0,CUDA_initialized=torch.cuda.is_initialized(),actual_Pi_Critic_STD_updates=0,complete_three_optimizer_conversion=False,not_navigation_jump270_or_full_SuperMimic=True)
 put('ROOT281_NEW_WM_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json',row);print(json.dumps(row))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT281_NEW_FORMAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_promotion=True));raise
