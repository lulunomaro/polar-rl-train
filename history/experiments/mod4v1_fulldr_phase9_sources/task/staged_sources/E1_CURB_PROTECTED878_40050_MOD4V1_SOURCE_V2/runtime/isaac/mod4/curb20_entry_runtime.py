"""Same CURB plant/commands; independently admitted reset-entry placement only."""
import numpy as np,torch
from curb20_retention_runtime import configure_retention as old_configure
from curb20_entry_math import entry_map,PROFILE

def reset_entry_xy(env,ids):
 from e1_full_pose_reset import A
 if not hasattr(env,'_curb_entry_xy'):
  bank=np.load(A/'MOD4_RESET_COLLISION_BANK.npz');pick=int(np.argmin(abs(bank['root_height']-.25)))
  xy,receipt=entry_map(env.scene.env_origins.detach().cpu().numpy(),env.scene.terrain.retention_assignment,bank['points_root'][pick])
  env._curb_entry_xy=torch.as_tensor(xy,device=env.device,dtype=torch.float32)
  env._curb_entry_map_receipt=receipt
  assert env.scene.terrain.retention_assignment_sha and len(env._curb_entry_xy)==env.num_envs
 return env._curb_entry_xy[ids].clone()

def configure_retention(cfg):
 from curb20_entry_full_pose_reset import full_reset
 r=old_configure(cfg);cfg.events.consistent_start.func=full_reset
 r['independent_CURB_reset_entry']=dict(profile=PROFILE,only_actual_CURB_assignment=True,original_world_heading_and_commands_unchanged=True,full_sampled_collision_footprint_front_support_m=.4,lower_upper_lanes_abs_x_m=[.8,1.65],not_evaluation_route_shortening=True,no_new_rng=True)
 return r
