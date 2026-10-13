"""Explicit original20k -> selected2048 transition; strict subsequent identity."""
from pathlib import Path
import torch,numpy as np,copy,json,hashlib,os,time
import original_full20k_binding as old
from original_full20k_binding import same,H,floating_count,DONOR_SHA,GEOMETRY_SHA,PARTITION_SHA,ASSIGNMENT_SHA
from selected_source_projection import select,project_tree,bind_selected_entry
N=2048
PROFILE='windows4090_temporary2048_memory20GB_selected_source_v1'
FIELDS={'num_envs','entry_map_sha256','entry_origin_sha256','entry_input_sha256','entry_runtime_sha256','entry_full_pose_sha256','parent_boundary_source_sha256'}
STATES=old.IDENTITY_STATES
def perenv_inventory(v,path='',n=N):
 out=[]
 if torch.is_tensor(v) and n in v.shape:out.append((path,tuple(v.shape),str(v.dtype)))
 elif isinstance(v,dict):
  for k,x in v.items():out.extend(perenv_inventory(x,path+'/'+str(k),n))
 elif isinstance(v,(list,tuple)):
  for i,x in enumerate(v):out.extend(perenv_inventory(x,path+'/'+str(i),n))
 return out
def validate(ck,source_sha):
 if 'WINDOWS4090_TEMPORARY_BRANCH' not in ck:return old.validate(ck,source_sha)
 b=ck['WINDOWS4090_TEMPORARY_BRANCH'];assert b['profile']==PROFILE and b['original20k_donor_SHA']==DONOR_SHA and b['num_envs']==N
 assert len(b['source_original_ids'])==N and len(set(b['source_original_ids']))==N and all(0<=i<20000 for i in b['source_original_ids'])
 assert ck['independent_terrain_expert']=='E1_WAVE50' and ck['E1_WAVE50_initial_source_sha256']==old.INITIAL35_SHA
 t=ck['E1_terrain_state'];assert t['num_envs']==N and t['geometry_triangles_sha256']==GEOMETRY_SHA and t['ordered_partition_triangles_sha256']==PARTITION_SHA
 assert t['entry_assignment_sha256']==ASSIGNMENT_SHA and t['triangles']==10306304 and t['G4_height_peak_to_trough_m']==.05
 assert len(perenv_inventory(ck))==99 and floating_count(ck)==107
 assert t['seed']==20260928 and t['layout']==[40,40] and t['command_vx_range']==[-.3,.3] and t['command_vy_yaw']==[0.,0.]
 assert (ck['actor_state_dict']['distribution.std_param']>0).all()
 assert len(b['family_counts'])==5 and sum(b['family_counts'])==N and all(type(x) is int and x>0 for x in b['family_counts'])
 for key in STATES:assert ck[key]['num_envs']==N
 assert hashlib.sha256(t['spawn_xy'].cpu().numpy().astype('<f4').tobytes()).hexdigest()==t['entry_map_sha256']
 assert t['entry_origin_sha256']==t['entry_map_sha256']
 for key in ('E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state'):
  st=ck[key];assert st['assignment_sha256']==ASSIGNMENT_SHA and st['entry_map_sha256']==t['entry_map_sha256'] and st['entry_origin_sha256']==t['entry_origin_sha256']
  assert same(st['bound_episode'],t['episode'])
 assert same(ck['E1_WAVE50_route_lifecycle_state']['spawn_xy'],t['spawn_xy'])
 assert same(ck['E1_WAVE50_episode_direction_state']['reset_xy'],t['spawn_xy'])
 if source_sha!=DONOR_SHA:
  m=ck['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL'];assert m['applied_once_after_complete_source_restore'] and not m['CPU_prepared_only']
 return ck
def initialize_selected_env(env,args):
 assert env.num_envs==N and H(args.source_checkpoint)==args.source_sha
 ck=validate(torch.load(args.source_checkpoint,map_location='cpu',weights_only=False),args.source_sha)
 if 'WINDOWS4090_TEMPORARY_BRANCH' in ck:
  ids=torch.arange(N);quota=ck['WINDOWS4090_TEMPORARY_BRANCH']['family_counts']
  bind_selected_entry(env,ids,ck)
  env._local_projection_original_ids=torch.tensor(ck['WINDOWS4090_TEMPORARY_BRANCH']['source_original_ids'])
 else:
  ids,quota=select(env,ck);bind_selected_entry(env,ids,ck)
 env._temporary_source_ids=ids;env._temporary_family_quota=quota
 env.reset();env.command_manager.get_term('twist')._write_dynamic(torch.arange(N,device=env.device))
 return ck
def bound_tree(env,args):
 from wave50_entry_current_state_v2 import current_state,identity,KEY
 from wave50_route_runtime import state_dict as route
 from wave50_lifetime_runtime import state_dict as lifetime
 ck=initialize_selected_env(env,args);is_small='WINDOWS4090_TEMPORARY_BRANCH' in ck
 changes=[];projected=copy.deepcopy(ck) if is_small else project_tree(ck,env._temporary_source_ids,changes=changes)
 assert len(perenv_inventory(projected))==99 and floating_count(projected)==107
 for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):assert same(ck[k],projected[k]),k
 actual=current_state(env);term=env.command_manager.get_term('twist')
 states={'E1_terrain_state':actual,KEY:identity(actual),'E1_WAVE50_episode_direction_state':term.state_dict_direction(),'E1_WAVE50_route_lifecycle_state':route(env,refresh=True),'E1_WAVE50_episode_lifetime_state':lifetime(env,refresh=True)}
 bindings=[]
 for k,st in states.items():
  prior=projected[k];a={f:v for f,v in prior.items() if not torch.is_tensor(v)};b={f:v for f,v in st.items() if not torch.is_tensor(v)}
  assert set(a)==set(b),(k,'metadata schema')
  for f,v in b.items():
   if same(a[f],v):continue
   assert not is_small and f in FIELDS,(k,f,'unapproved or repeated identity migration')
   bindings.append(dict(state=k,field=f,old=a[f],new=v));prior[f]=copy.deepcopy(v)
  # Every projected tensor retains its saved value; no real new episode yet.
 assert same(projected['E1_terrain_state']['spawn_xy'],ck['E1_terrain_state']['spawn_xy'] if is_small else ck['E1_terrain_state']['spawn_xy'][env._temporary_source_ids])
 assert same(projected['E1_terrain_state']['reset_expected_q'],actual['reset_expected_q'])
 if not is_small:
  projected['WINDOWS4090_TEMPORARY_BRANCH']=dict(profile=PROFILE,original20k_donor_SHA=DONOR_SHA,num_envs=N,source_num_envs=20000,source_original_ids=env._temporary_source_ids.tolist(),family_counts=env._temporary_family_quota,selected_all99perenv_exact=True,all_actorcritic_std_Adam_globalnamed_privateRNG_initially_exact=True,source_original_unchanged=True,not_PhysX_exact_resume=True)
  projected['WINDOWS4090_TEMPORARY_BACKEND_BINDING']=dict(profile=PROFILE,num_envs=N,complete_original20k_donor_SHA=DONOR_SHA,explicit_environment_selection_and_Windows_ABI_metadata_migration=True,changes=bindings,backend_equivalence_not_claimed=True,PhysX_exact_resume=False)
 validate(projected,DONOR_SHA)
 return projected,dict(changes=changes,metadata_bindings=bindings,same_temporary_identity=is_small,source_original_ids=projected['WINDOWS4090_TEMPORARY_BRANCH']['source_original_ids'])
def probe_source(env,args):
 if env.num_envs==10:return old.validate(torch.load(args.source_checkpoint,map_location='cpu',weights_only=False),args.source_sha)
 return bound_tree(env,args)[0]
def materialize(env,output,args,write):
 projected,receipt=bound_tree(env,args);q=Path(output)/'WINDOWS4090_BOUND_FULLSTATE_SOURCE.pt';assert not q.exists()
 torch.save(projected,q)
 with q.open('r+b') as f:f.flush();os.fsync(f.fileno())
 assert same(projected,torch.load(q,map_location='cpu',weights_only=False))
 receipt.update(epoch=time.time(),pid=os.getpid(),passed=True,source_sha256=args.source_sha,bound_source_sha256=H(q),original20k_donor_SHA=DONOR_SHA,num_envs=N,explicit_environment_projection=True,all99selected_perenv_exact=True,floating107=True,no_source_splice=True,no_RNG_in_projection=True,not_PhysX_exact_resume=True)
 write('WINDOWS4090_FULLSTATE_CPU_BINDING_ACTUAL.json',receipt);return q,receipt
