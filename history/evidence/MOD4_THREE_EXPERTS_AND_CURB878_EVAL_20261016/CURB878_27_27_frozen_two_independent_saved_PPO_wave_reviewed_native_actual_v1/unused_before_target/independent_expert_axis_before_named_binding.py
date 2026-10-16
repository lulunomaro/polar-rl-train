"""Explicit task axes; no inference truth, physical setters, reward or RNG changes."""
import hashlib,json
import numpy as np
def layout(origins,family_grid):
 xy=np.asarray(origins,dtype=np.float64)[:,:2];rc=np.floor(xy/9.+20).astype(np.int64)
 if not ((rc>=0)&(rc<40)).all():raise ValueError('Origin outside pinned40x40 layout')
 if np.asarray(family_grid).shape!=(40,40):raise ValueError('Family grid shape')
 centers=(rc.astype(np.float64)+.5-20)*9.;mask=np.asarray(family_grid)[rc[:,0],rc[:,1]]==4
 return centers.astype(np.float32),mask
def cache(env):
 import torch
 if not hasattr(env,'_independent_expert_axis_cache'):
  centers,mask=layout(env.scene.env_origins.detach().cpu().numpy(),env.scene.terrain.retention_family.detach().cpu().numpy())
  env._independent_expert_axis_cache=dict(centers=torch.as_tensor(centers,device=env.device),target=torch.as_tensor(mask,device=env.device),origin=env.scene.env_origins[:,:2].clone())
 return env._independent_expert_axis_cache
def configure_route(cfg,original,kind):
 recipe=original(cfg);old=cfg.terminations.rough_route_boundary.func
 def boundary(env):
  import torch
  v=old(env);x=cache(env);root=env.scene['robot'].data.root_pos_w;root=root.torch if hasattr(root,'torch') else root;delta=root[:,:2]-x['centers'];new=(delta[:,0].abs()>3.5)|(delta[:,1].abs()>3.)
  return torch.where(x['target'],new,v)
 assert cfg.terminations.rough_route_boundary.time_out is True;cfg.terminations.rough_route_boundary.func=boundary
 recipe['independent_expert_new_axis']=dict(kind=kind,target_family_only='random_uniform_for_rm',original_geometry_unchanged=True,original_other_family_boundary_unchanged=True,target_boundary_tile_center_abs_xy_m=[3.5,3.],physical_episode_limit_seconds=20,normal_commands_reward_DR_RNG_unchanged=True,no_live_heading_position_correction=True)
 return recipe
def configure_slope(cfg):
 from slope5_retention_runtime import configure_retention
 return configure_route(cfg,configure_retention,'SLOPE5_full_ramp_and_both_flat_supports')
def configure_wave(cfg):
 from retention_flat_runtime_sdk_reviewed import configure_retention
 return configure_route(cfg,configure_retention,'WAVE35_whole_wave_and_both_flat_supports')
def bind_after_restore(env,kind):
 import torch
 x=cache(env);x['kind']=kind
 if kind=='CURB20':
  term=env.command_manager.get_term('twist');side=torch.sign(env._rough_spawn_xy[:,0]-x['centers'][:,0]);assert (side[x['target']]!=0).all();x['reset_direction']=-side;old=term._write_dynamic
  def write(ids):
   old(ids)
   if term.manual_evaluation_mode:return
   ids=torch.as_tensor(ids,device=env.device,dtype=torch.long);selected=ids[x['target'][ids]&~term.is_standing_env[ids]]
   term.vel_command_b[selected,0]=.3*x['reset_direction'][selected];term.vel_command_b[selected,1:]=0.;term.linear_vx[selected]=term.vel_command_b[selected,0]
  term._write_dynamic=write;write(torch.arange(env.num_envs,device=env.device))
 x['original_private_RNG_draws_unchanged']=True
 return x
