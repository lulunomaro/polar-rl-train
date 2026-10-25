"""Explicit G2->G3 geometry transition; keep all D1-D7 and optimizer streams."""
from pathlib import Path
import os,time,json,hashlib,torch
import e1_terrain_checkpoint as old
from chassis_pd_checkpoint import install_chassis_pd_save_contract,resume_chassis_pd_new_episode
from spring_pressure_checkpoint import exact
PROFILE='mod4_G3_CAD_derived_35mm_v1'
def validate(state,n):
 assert state['profile']==PROFILE and state['G3_height_peak_to_trough_m']==.035
 assert len(state['G3_profile_sha256'])==64 and state['G3_is_derived_not_real_RM70mm']
 copy=dict(state,profile='mod4_intro_gentle_v1')
 return old.validate(copy,n)
def current_state(env):
 from g3_cad_wave_geometry import PROFILE as path
 state=old.current_state(env)
 state.update(profile=PROFILE,G3_height_peak_to_trough_m=.035,G3_profile_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),G3_is_derived_not_real_RM70mm=True)
 validate(state,env.num_envs);return state
def identity(state):return old.identity(state)
def restore(env,state):
 validate(state,env.num_envs);assert identity(state)==identity(current_state(env))
 for name,attribute in (('spawn_xy','_rough_spawn_xy'),('reset_expected_q','_rough_probe_expected_q'),('episode','_e1_episode')):
  getattr(env,attribute).copy_(state[name].to(env.device))
 assert exact(current_state(env),state)
def install_e1_save_contract(runner,env):
 install_chassis_pd_save_contract(runner,env);original=runner.save
 def save(path,*a,**k):
  original(path,*a,**k);ck=torch.load(path,map_location='cpu',weights_only=False)
  ck['E1_terrain_state']=current_state(env)
  ck['E1_terrain_resume_contract']='Full same-G3 state restoration, then new physical episode; G2->G3 is an explicitly authorized geometric transition, never an exact mesh resume.'
  torch.save(ck,path)
 runner.save=save
def resume_e1_new_episode(runner,env,path,log_dir):
 ck=torch.load(path,map_location='cpu',weights_only=False);state=ck['E1_terrain_state'];same=state['profile']==PROFILE
 if same:restore(env,state)
 else:
  from g2_terrain_checkpoint import validate as validate_previous_G2
  validate_previous_G2(state,env.num_envs)
  assert os.environ.get('RM_E1_G3_INITIAL_ADMISSION')=='G2_to_G3_35mm'
  assert state['profile']=='mod4_G2_CAD_derived_20mm_v1' and identity(state)!=identity(current_state(env))
  # Restore existing bookkeeping before one fresh full-pose reset on the new mesh.
  for name,attribute in (('spawn_xy','_rough_spawn_xy'),('reset_expected_q','_rough_probe_expected_q'),('episode','_e1_episode')):
   getattr(env,attribute).copy_(state[name].to(env.device));assert torch.equal(getattr(env,attribute).cpu(),state[name].cpu())
 before=current_state(env);tmp=Path(log_dir)/'E1_G3_ACTUAL_CUDA_ROUNDTRIP.pt'
 torch.save(before,tmp);restore(env,torch.load(tmp,map_location='cpu',weights_only=False))
 episode=env._e1_episode.clone();row=resume_chassis_pd_new_episode(runner,env,path,log_dir)
 assert torch.equal(env._e1_episode,episode+1) and env._rough_query_tick is None
 assert identity(current_state(env))==identity(before)
 proof=dict(epoch=time.time(),pid=os.getpid(),source_sha256=row['source_sha256'],predecessor_had_E1_terrain_state=True,terrain_state_restored_exact=same,explicitly_new_E1_terrain=not same,explicit_G2_to_G3_geometry_transition=not same,old_terrain_bookkeeping_restored_before_new_episode=True,old_mesh_not_claimed_restored_on_new_geometry=True,actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact=True,complete_D1_D7_optimizer_global_named_streams_verified=True,E1_episode_incremented_once=True,new_physical_episode=True,static_geometry_identity_preserved=same,same_tick_ground_query_cache_cleared=True,PhysX_exact_resume_claimed=False,terrain_identity=identity(current_state(env)))
 Path(log_dir,'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2));return proof
