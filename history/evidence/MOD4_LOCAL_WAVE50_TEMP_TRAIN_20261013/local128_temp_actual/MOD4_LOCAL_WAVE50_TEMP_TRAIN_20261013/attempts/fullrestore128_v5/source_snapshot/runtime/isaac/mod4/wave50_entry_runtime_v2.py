"""Only reset XY changes; cache binds actual origins, assignment, bank and profile."""
from pathlib import Path
import hashlib,json,numpy as np,torch
from wave50_entry_v1_math import entry_map,PROFILE
A=Path(__file__).resolve().parent
PROFILE_SHA='995115310ad96d92a77865c04c736896c112b4b89c7d674ac7a6d4d19f249a5d'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reset_entry_xy(env,ids):
 if hasattr(env,'_local_projection_reset_xy'):
  from local_state_projection import selected_entry
  return selected_entry(env,ids)
 origins=env.scene.env_origins[:,:2];rows=env.scene.terrain.retention_assignment
 assignment=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert assignment==env.scene.terrain.retention_assignment_sha
 profile=A/'g4_cad_profile.json';assert h(profile)==PROFILE_SHA
 bank=A/'MOD4_RESET_COLLISION_BANK.npz'
 static=(assignment,h(bank),h(A/'wave50_entry_v1_math.py'),h(A/'wave50_entry_full_pose_reset_v2.py'),h(profile))
 if not hasattr(env,'_wave50_entry_xy') or static!=env._wave50_entry_static_identity or not torch.equal(origins,env._wave50_entry_origin_snapshot):
  with np.load(bank) as z:
   pick=int(np.argmin(abs(z['root_height']-.25)));points=z['points_root'][pick].copy()
  xy,receipt=initialization_safe_map(origins.detach().cpu().numpy(),rows,points,json.loads(profile.read_bytes())['span_m'],env.num_envs)
  origin_sha=hashlib.sha256(origins.detach().cpu().numpy().astype('<f4').tobytes()).hexdigest()
  key=hashlib.sha256((origin_sha+json.dumps(static)).encode()).hexdigest()
  env._wave50_entry_xy=torch.as_tensor(xy,device=env.device,dtype=torch.float32)
  env._wave50_entry_origin_snapshot=origins.clone();env._wave50_entry_static_identity=static
  env._wave50_entry_cache_builds=getattr(env,'_wave50_entry_cache_builds',0)+1
  env._wave50_entry_map_receipt=dict(receipt,actual_origin_sha256=origin_sha,actual_assignment_sha256=assignment,
   complete_bank_sha256=static[1],math_sha256=static[2],full_pose_reset_sha256=static[3],geometry_profile_sha256=static[4],
   actual_input_identity_sha256=key,cache_builds=env._wave50_entry_cache_builds,actual_origin_bound=True)
 return env._wave50_entry_xy[ids].clone()
def initialization_safe_map(origins,rows,points,span,n):
 origins=np.asarray(origins,dtype='<f4');mask=np.zeros(n,dtype=bool);covered=np.zeros(n,dtype=bool)
 for a in rows:
  b=np.asarray(a['bounds']);inside=((origins>=b[0,:2])&(origins<b[1,:2])).all(1)
  covered|=inside
  if a['family']=='random_uniform_for_rm':mask|=inside
 if mask.any():return entry_map(origins,rows,points,span)
 assert n<20000 and covered.all() and np.isfinite(origins).all() and len(np.unique(origins,axis=0))==n
 extent=np.max(abs(points[:,:2]),axis=0);assert extent[0]<.30 and extent[1]<.30 and 2.<span<3.
 receipt=dict(profile=PROFILE,map_sha256=hashlib.sha256(origins.tobytes()).hexdigest(),changed_environments=0,Wave_environments=0,other_environments_unchanged=n,
  actual_Wave_groups=[],collision_sample_extent_xy=extent.tolist(),minimum_full_flat_front_support_m=float(.8-extent[0]),minimum_same_side_lane_gap_m=.85,
  ten_wave_span_m=float(span),commands_and_RNG_consumption_unchanged=True,no_new_random_stream=True,reset_position_only_axis=True,
  no_actor_gate_truth_input=True,original2m_route_truncation_unchanged=True,not_whole_ten_wave_training_episode_certificate=True,
  CPU_map_not_physical_contact_nonpenetration_or_causal_certificate=True,explicit_small_initialization_has_no_Wave_origins=True)
 return origins.copy(),receipt
def configure_retention(cfg):
 from g4_retention_runtime import configure_retention as old_configure
 from wave50_entry_full_pose_reset_v2 import full_reset
 r=old_configure(cfg);cfg.events.consistent_start.func=full_reset
 r['independent_WAVE50_reset_entry']=dict(profile=PROFILE,reset_XY_only=True,unchanged_command_RNG_reward_DR_geometry=True,
  full_sampled_footprint_front_support_min_m=.4,no_new_random_stream=True,original2m_training_route_unchanged=True)
 return r
