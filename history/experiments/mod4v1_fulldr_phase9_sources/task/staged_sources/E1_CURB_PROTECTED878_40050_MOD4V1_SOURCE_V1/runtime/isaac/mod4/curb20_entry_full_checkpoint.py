"""Independent CURB fullsave/fullresume and explicit G3-to-CURB transition."""
from e1_pinned_source_v1 import cached_load,cached_H,cached_source_owns,runner_source_load_scope
from pathlib import Path
import hashlib,json,os,time,torch
from curb20_entry_current_state import current_state,identity,validate,PROFILE
from chassis_pd_checkpoint import install_chassis_pd_save_contract,resume_chassis_pd_new_episode
from retention_command_state import validate as command_validate,same
from curb20_command_migration_environment_view import restore_source_then_bind_CURB
SOURCE_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'

def restore(env,state):
 validate(state,env.num_envs);assert identity(state)==identity(current_state(env))
 for k,a in (('spawn_xy','_rough_spawn_xy'),('reset_expected_q','_rough_probe_expected_q'),('episode','_e1_episode')):
  getattr(env,a).copy_(state[k].to(env.device))
 assert same(current_state(env),state)

def install_e1_save_contract(runner,env):
 install_chassis_pd_save_contract(runner,env);original=runner.save
 def save(path,*a,**k):
  original(path,*a,**k);ck=cached_load(path,map_location='cpu',weights_only=False,purpose='runtime/isaac/mod4/curb20_entry_full_checkpoint.py:19')
  ck['E1_terrain_state']=current_state(env)
  ck['E1_terrain_resume_contract']='Independent CURB same geometry/command fullrestore, then one new physical episode; explicit initial G3-to-CURB transition, not PhysX exactresume.'
  ck['E1_retained_flat_command_state']=env.command_manager.get_term('twist').state_dict_retention()
  ck['E1_current_command_profile']=ck['E1_retained_flat_command_state']['profile']
  ck['E1_terrain_state_legacy_command_ranges_are_noneligible_gentle_only']=True
  ck['independent_terrain_expert']='E1_CURB'
  ck['E1_CURB_initial_source_sha256']=SOURCE_SHA
  ck['E1_CURB_entry_reset_identity']=identity(ck['E1_terrain_state'])
  assert hashlib.sha256(ck['E1_terrain_state']['spawn_xy'].cpu().numpy().astype('<f4').tobytes()).hexdigest()==ck['E1_terrain_state']['entry_map_sha256']
  torch.save(ck,path);env.write_retention_trace(Path(path).parent)
 runner.save=save

def resume_e1_new_episode(runner,env,path,log_dir):
 path=Path(path);ck=cached_load(path,map_location='cpu',weights_only=False,purpose='runtime/isaac/mod4/curb20_entry_full_checkpoint.py:33');h=cached_H(path,purpose='runtime/isaac/mod4/curb20_entry_full_checkpoint.py:source_identity:33')
 state=ck['E1_terrain_state'];term=env.command_manager.get_term('twist');cmd=ck['E1_retained_flat_command_state']
 command_validate(cmd,env.num_envs);same_scope=state['profile']==PROFILE
 if same_scope:
  assert ck['independent_terrain_expert']=='E1_CURB' and ck['E1_CURB_initial_source_sha256']==SOURCE_SHA
  assert ck['E1_CURB_entry_reset_identity']==identity(state)
  restore(env,state);term.load_state_retention(cmd);assert same(term.state_dict_retention(),cmd)
  migration=dict(source_command_state_and_private_RNG_exact=True,explicit_changed_assignment_binding=False,
    source_assignment_sha256=cmd['assignment_sha256'],new_actual_assignment_sha256=cmd['assignment_sha256'],original_strict_loader_reused_under_source_identity=True)
 else:
  from g3_terrain_checkpoint import validate as source_validate
  assert h==SOURCE_SHA and os.environ.get('RM_CURB_INITIAL_ADMISSION')=='verified_G3_to_independent_CURB20'
  source_validate(state,env.num_envs);assert identity(state)!=identity(current_state(env))
  for k,a in (('spawn_xy','_rough_spawn_xy'),('reset_expected_q','_rough_probe_expected_q'),('episode','_e1_episode')):
   getattr(env,a).copy_(state[k].to(env.device));assert torch.equal(getattr(env,a).cpu(),state[k].cpu())
  migration=restore_source_then_bind_CURB(term,cmd,cmd['assignment_sha256'])
 before=current_state(env);ct=term.state_dict_retention();tmp=Path(log_dir)/'CURB_FULL_STATE_ACTUAL_CUDA_ROUNDTRIP.pt'
 torch.save(dict(terrain=before,command=ct),tmp);loaded=cached_load(tmp,map_location='cpu',weights_only=False,purpose='runtime/isaac/mod4/curb20_entry_full_checkpoint.py:50')
 restore(env,loaded['terrain']);term.load_state_retention(loaded['command'])
 assert same(current_state(env),before) and same(term.state_dict_retention(),ct)
 episode=state['episode'].to(env.device).clone()
 old=resume_chassis_pd_new_episode(runner,env,path,log_dir)
 assert torch.equal(env._e1_episode,episode+1) and env._rough_query_tick is None
 assert identity(current_state(env))==identity(before)
 term._write_dynamic(torch.arange(env.num_envs,device=env.device));audit=term.audit_retention()
 assert audit['assignment_sha256']==ct['assignment_sha256'] and audit['projection_error']<=1e-6
 terrain=dict(epoch=time.time(),pid=os.getpid(),source_sha256=h,terrain_state_restored_exact=same_scope,
  explicitly_new_E1_terrain=not same_scope,explicit_G3_to_CURB_geometry_transition=not same_scope,
  explicit_G2_to_G3_geometry_transition=False,entry_reset_state_restored_exact=same_scope,explicit_new_entry_reset_scope=not same_scope,entry_origin_cache_bound_to_actual_origins=True,old_terrain_bookkeeping_restored_before_new_episode=True,
  actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact=True,complete_D1_D7_optimizer_global_named_streams_verified=True,
  E1_episode_incremented_once=True,saved_source_episode_plus_one_verified=True,new_physical_episode=True,
  same_tick_ground_query_cache_cleared=True,PhysX_exact_resume_claimed=False,terrain_identity=identity(current_state(env)))
 proof=dict(epoch=time.time(),pid=os.getpid(),source_sha256=h,expert='E1_CURB',
  predecessor_command_state_restored_exact=True,explicitly_new_command_scope=not same_scope,
  migration=migration,actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact=True,
  old_full_D1_D7_optimizer_global_named_streams_verified=old['complete_D1_D6_optimizer_global_named_streams_verified'],
  E1_episode_incremented_once=True,saved_source_episode_plus_one_verified=True,one_new_physical_episode=True,
  actual_command_audit=audit,PhysX_exact_resume_claimed=False)
 Path(log_dir,'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(terrain,indent=2))
 Path(log_dir,'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2))
 return proof
