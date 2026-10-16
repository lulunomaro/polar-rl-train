"""Change only Wave episode inward route truncation, retain original other axes."""
from pathlib import Path
import torch,hashlib,json
from wave50_entry_runtime_v2 import reset_entry_xy
from wave50_route_state import PROFILE,KEY,FIELDS,validate,identity,evaluate_timeout
A=Path(__file__).resolve().parent
def tensor(v):return v.torch if hasattr(v,'torch') else v
def metadata(env):
 receipt=env._wave50_entry_map_receipt
 return dict(version=1,profile=PROFILE,num_envs=env.num_envs,no_new_rng=True,Wave_inward_limit_m=4.,outward_limit_m=2.,lateral_limit_m=2.,other_environment_limit_m=2.,assignment_sha256=env.scene.terrain.retention_assignment_sha,entry_map_sha256=receipt['map_sha256'],entry_origin_sha256=receipt['actual_origin_sha256'],parent_boundary_source_sha256=hashlib.sha256((A/'e1_terrain_runtime.py').read_bytes()).hexdigest())
def bind(env):
 n=env.num_envs;ids=torch.arange(n,device=env.device);xy=reset_entry_xy(env,ids);m=metadata(env);old=getattr(env,'_wave50_route_state',None)
 if old is None or identity(old)!=identity(m):
  old=dict(m,wave_mask=torch.zeros(n,device=env.device,dtype=torch.bool),toward_sign=torch.zeros(n,device=env.device),bound_episode=torch.full((n,),-1,device=env.device,dtype=torch.long),spawn_xy=torch.zeros((n,2),device=env.device),inward_limit_m=torch.full((n,),2.,device=env.device),evaluations=torch.zeros(n,device=env.device,dtype=torch.long));env._wave50_route_state=old
 changed=ids[old['bound_episode']!=env._e1_episode]
 if len(changed):
  t=env.scene.terrain;size=torch.tensor(t.retention_size,device=env.device);rc=torch.floor(xy[changed]/size+20).long();assert ((rc>=0)&(rc<40)).all()
  bounds=t.retention_bounds[rc[:,0],rc[:,1]];mask=t.retention_family[rc[:,0],rc[:,1]]==4;d=xy[changed,0]-(bounds[:,0,0]+bounds[:,1,0])*.5
  ex=torch.tensor(env._wave50_entry_map_receipt['collision_sample_extent_xy'],device=env.device);span=env._wave50_entry_map_receipt['ten_wave_span_m']
  assert (d[mask].abs()-ex[0]-span*.5>=.4-1e-6).all()
  assert torch.equal(tensor(env._rough_spawn_xy)[changed],xy[changed]),'Route must bind actual reset spawn, not current moving pose'
  old['wave_mask'][changed]=mask;old['toward_sign'][changed]=torch.where(mask,-torch.sign(d),0.)
  old['bound_episode'][changed]=env._e1_episode[changed];old['spawn_xy'][changed]=tensor(env._rough_spawn_xy)[changed];old['inward_limit_m'][changed]=torch.where(mask,4.,2.)
 validate(old,n);assert torch.equal(old['spawn_xy'],tensor(env._rough_spawn_xy));return old
def state_dict(env,refresh=False):
 s=bind(env) if refresh or not hasattr(env,'_wave50_route_state') else env._wave50_route_state
 validate(s,env.num_envs);return {k:(v.clone() if torch.is_tensor(v) else v) for k,v in s.items()}
def load_state(env,s):
 validate(s,env.num_envs);reset_entry_xy(env,torch.arange(env.num_envs,device=env.device));assert identity(s)==identity(metadata(env))
 env._wave50_route_state={k:(v.to(env.device).clone() if torch.is_tensor(v) else v) for k,v in s.items()}
def audit(env):
 s=bind(env);term=env.command_manager.get_term('twist')
 assert torch.equal(s['wave_mask'],term.wave_mask) and torch.equal(s['toward_sign'],term.entry_sign) and torch.equal(s['bound_episode'],term.bound_episode)
 return dict(profile=PROFILE,Wave_episodes=int(s['wave_mask'].sum()),nonWave_episodes=int((~s['wave_mask']).sum()),Wave_inward_limit_m=4.,outward_and_lateral_and_nonWave_limit_m=2.,actual_reset_spawn_exact=True,episode_identity_exact=True,entry_assignment_origin_identity=identity(s),no_new_rng=True,no_live_heading_position_command_correction=True,no_actor_gate_input=True,evaluations=int(s['evaluations'].sum()))
def boundary_timeout(env):
 from e1_terrain_runtime import boundary_timeout as original
 s=bind(env);out=evaluate_timeout(tensor(env.scene['robot'].data.root_pos_w)[:,:2],tensor(env._rough_spawn_xy),s,original(env));s['evaluations'].add_(1);return out
def configure_retention(cfg):
 from wave50_direction_runtime import configure_retention as original
 recipe=original(cfg);cfg.terminations.rough_route_boundary.func=boundary_timeout
 assert cfg.terminations.rough_route_boundary.time_out
 recipe['independent_WAVE50_route_lifecycle']=dict(profile=PROFILE,Wave_inward_limit_m=4.,old_outward_lateral_nonWave2m_exact=True,only_route_truncation_axis=True,no_reward_geometry_command_DR_clock_change=True,no_actor_gate_truth_input=True)
 return recipe
def verify_GPU_boundary_fixture(env):
 """Actual bound GPU tensors and pure boundary evaluation, zero physical teleport."""
 from e1_terrain_runtime import boundary_timeout as original
 import types
 s=state_dict(env,refresh=True);anchor=s['spawn_xy'];mask=s['wave_mask'];sign=s['toward_sign'];rows=[]
 for x,y in ((2.5,0.),(4.,0.),(4.001,0.),(-2.001,0.),(0.,2.001)):
  xy=anchor.clone();xy[:,0]+=torch.where(mask,sign,torch.ones_like(sign))*x;xy[:,1]+=y
  fixture=types.SimpleNamespace(scene={'robot':types.SimpleNamespace(data=types.SimpleNamespace(root_pos_w=xy))},_rough_spawn_xy=anchor)
  old=original(fixture);new=evaluate_timeout(xy,anchor,s,old);assert torch.equal(new[~mask],old[~mask])
  expect=x>4 or x < -2 or abs(y)>2;assert torch.equal(new[mask],torch.full_like(new[mask],expect))
  rows.append(dict(inward_fixture_m=x,lateral_fixture_m=y,old_truncated_Wave=int(old[mask].sum()),new_truncated_Wave=int(new[mask].sum()),nonWave_exact=True))
 return dict(passed=True,actual_bound_CUDA_state=anchor.is_cuda,rows=rows,no_physics_step_reset_teleport_or_progress_credit=True,not_physical_fullroute_or_contact_certificate=True)
