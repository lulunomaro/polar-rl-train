"""Full D1-D7/optimizer restore, terrain metadata restore, then one new episode."""
from pathlib import Path
import os,time,json,hashlib,torch
from e1_terrain_state import validate
from chassis_pd_checkpoint import install_chassis_pd_save_contract,resume_chassis_pd_new_episode
from spring_pressure_checkpoint import exact
def current_state(env):
 from e1_full_pose_reset import query,A
 mesh=query(env).geometry;part=env.scene.terrain.exact_partition_receipt
 state=dict(version=1,num_envs=env.num_envs,profile='mod4_intro_gentle_v1',seed=env.cfg.seed,layout=[40,40],command_vx_range=[-.3,.3],command_vy_yaw=[0.,0.],
  geometry_triangles_sha256=mesh.receipt()['triangles_sha256'],ordered_partition_triangles_sha256=part['triangle_world_f32_order_sha256'],triangles=len(mesh.faces),
  partition_exact=part['pass_'] and part['all_faces_and_winding_retained'] and not part['geometry_simplified'],no_ground_fallback=True,no_privileged_terrain_actor_input=True,
  reset_bank_sha256=hashlib.sha256((A/'MOD4_RESET_COLLISION_BANK.npz').read_bytes()).hexdigest(),spawn_xy=env._rough_spawn_xy.clone(),reset_expected_q=env._rough_probe_expected_q.clone(),episode=env._e1_episode.clone())
 validate(state,env.num_envs);return state
def identity(state):
 return {k:v for k,v in state.items() if k not in ('spawn_xy','reset_expected_q','episode')}
def restore(env,state):
 validate(state,env.num_envs);assert identity(state)==identity(current_state(env)),'Terrain recipe/mesh identity differs'
 env._rough_spawn_xy.copy_(state['spawn_xy'].to(env.device));env._rough_probe_expected_q.copy_(state['reset_expected_q'].to(env.device));env._e1_episode.copy_(state['episode'].to(env.device))
 assert exact(current_state(env),state)
def install_e1_save_contract(runner,env):
 install_chassis_pd_save_contract(runner,env);original=runner.save
 def save(path,*a,**k):
  original(path,*a,**k);ck=torch.load(path,map_location='cpu',weights_only=False);state=current_state(env)
  ck['E1_terrain_state']=state;ck['E1_terrain_resume_contract']='Exact full DR/actor/critic/std/optimizer/globalnamed and terrain identity/bookkeeping restore, then one new physical episode. Static ray BVH reused, same-tick query cache cleared; not PhysX exactresume.'
  torch.save(ck,path)
 runner.save=save
def resume_e1_new_episode(runner,env,path,log_dir):
 ck=torch.load(path,map_location='cpu',weights_only=False);has='E1_terrain_state' in ck
 if has:restore(env,ck['E1_terrain_state'])
 else:assert os.environ.get('RM_E1_INITIAL_ADMISSION')=='E0_to_E1' and 'chassis_PD_state' in ck
 before=current_state(env);tmp=Path(log_dir)/'E1_TERRAIN_ACTUAL_CUDA_ROUNDTRIP.pt';torch.save(before,tmp);restored=torch.load(tmp,map_location='cpu',weights_only=False);restore(env,restored)
 episode=env._e1_episode.clone();row=resume_chassis_pd_new_episode(runner,env,path,log_dir)
 assert torch.equal(env._e1_episode,episode+1) and env._rough_query_tick is None
 assert identity(current_state(env))==identity(before)
 proof=dict(epoch=time.time(),pid=os.getpid(),source_sha256=row['source_sha256'],predecessor_had_E1_terrain_state=has,terrain_state_restored_exact=has,explicitly_new_E1_terrain=not has,
  actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact=True,complete_D1_D7_optimizer_global_named_streams_verified=True,E1_episode_incremented_once=True,new_physical_episode=True,
  static_geometry_identity_preserved=True,same_tick_ground_query_cache_cleared=True,PhysX_exact_resume_claimed=False,terrain_identity=identity(current_state(env)))
 Path(log_dir,'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2));return proof
