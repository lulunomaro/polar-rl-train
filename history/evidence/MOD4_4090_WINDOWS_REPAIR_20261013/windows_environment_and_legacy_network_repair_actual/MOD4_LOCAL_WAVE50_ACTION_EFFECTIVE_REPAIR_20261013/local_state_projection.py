"""Explicit small-environment branch from the exact immutable20k source checkpoint."""
from pathlib import Path
import torch,json,hashlib,copy,numpy as np
D=Path(__file__).resolve().parent
SOURCE=json.loads((D/'reports/SOURCE_FULL_STATE_CPU_ACTUAL.json').read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def same(a,b):
 if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and torch.equal(a.cpu(),b.cpu())
 if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and np.array_equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return a==b

def select(env,ck):
 n=env.num_envs;xy=ck['E1_terrain_state']['spawn_xy'];rc=torch.floor(xy/9+20).long();assert ((rc>=0)&(rc<40)).all()
 family=env.scene.terrain.retention_family.cpu()[rc[:,0],rc[:,1]]
 quota=[round(n*.30),round(n*.20),round(n*.20),round(n*.15)];quota.append(n-sum(quota));ids=[]
 for f,k in enumerate(quota):
  candidates=torch.nonzero(family==f).flatten();assert len(candidates)>=k
  # Spread deterministic selected environments over the source cohort without newRNG.
  index=torch.linspace(0,len(candidates)-1,k).round().long();ids.append(candidates[index])
 ids=torch.cat(ids);assert len(torch.unique(ids))==n
 return ids,quota

def project_tree(value,ids,path='',changes=None):
 if changes is None:changes=[]
 if isinstance(value,torch.Tensor):
  axes=[i for i,n in enumerate(value.shape) if n==20000]
  assert len(axes)<=1
  if axes:
   out=value.index_select(axes[0],ids).clone();changes.append(dict(path=path,axis=axes[0],from_shape=list(value.shape),to_shape=list(out.shape)));return out
  return value.clone()
 if isinstance(value,dict):
  return {k:len(ids) if k in ('n','num_envs') and v==20000 and isinstance(v,int) else project_tree(v,ids,path+'/'+str(k),changes) for k,v in value.items()}
 if isinstance(value,tuple):return tuple(project_tree(v,ids,path+'/'+str(i),changes) for i,v in enumerate(value))
 if isinstance(value,list):return [project_tree(v,ids,path+'/'+str(i),changes) for i,v in enumerate(value)]
 return copy.deepcopy(value)

def bind_selected_entry(env,ids,ck):
 xy=ck['E1_terrain_state']['spawn_xy'][ids].clone().to(env.device)
 env.scene.env_origins[:,:2]=xy;env.scene.terrain.env_origins[:,:2]=xy
 env._local_projection_reset_xy=xy;env._local_projection_original_ids=ids.clone()
 # Own isolated worker uses this frozen selected entrymap rather than reranking its lanes.
 env._local_projection_source_SHA=SOURCE['sha256']

def selected_entry(env,ids):
 from wave50_entry_runtime_v2 import A,h
 from wave50_entry_v1_math import PROFILE
 xy=env._local_projection_reset_xy;origins=env.scene.env_origins[:,:2]
 assert env._local_projection_source_SHA==SOURCE['sha256'] and torch.equal(xy,origins)
 rows=env.scene.terrain.retention_assignment;assignment=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert assignment==env.scene.terrain.retention_assignment_sha
 bank=A/'MOD4_RESET_COLLISION_BANK.npz';profile=A/'g4_cad_profile.json'
 with np.load(bank) as z:points=z['points_root'][int(np.argmin(abs(z['root_height']-.25)))].copy()
 extent=np.max(abs(points[:,:2]),axis=0);span=json.loads(profile.read_bytes())['span_m'];rc=torch.floor(xy/9+20).long()
 assert ((rc>=0)&(rc<40)).all();bounds=env.scene.terrain.retention_bounds[rc[:,0],rc[:,1]];mask=env.scene.terrain.retention_family[rc[:,0],rc[:,1]]==4
 ex=torch.tensor(extent,device=env.device);center=(bounds[:,0,0]+bounds[:,1,0])*.5
 assert (torch.abs(xy[mask,0]-center[mask])-ex[0]-span*.5>=.4-1e-6).all()
 assert ((xy[mask]-ex>=bounds[mask,0,:2]+.004-1e-6)&(xy[mask]+ex<=bounds[mask,1,:2]-.004+1e-6)).all()
 sha=hashlib.sha256(xy.cpu().numpy().astype('<f4').tobytes()).hexdigest()
 env._wave50_entry_xy=xy.clone();env._wave50_entry_origin_snapshot=origins.clone()
 env._wave50_entry_map_receipt=dict(profile=PROFILE,map_sha256=sha,actual_origin_sha256=sha,actual_assignment_sha256=assignment,complete_bank_sha256=h(bank),math_sha256=h(A/'wave50_entry_v1_math.py'),full_pose_reset_sha256=h(A/'wave50_entry_full_pose_reset_v2.py'),geometry_profile_sha256=h(profile),actual_input_identity_sha256=hashlib.sha256((sha+assignment+SOURCE['sha256']).encode()).hexdigest(),cache_builds=1,actual_origin_bound=True,collision_sample_extent_xy=extent.tolist(),ten_wave_span_m=span,Wave_environments=int(mask.sum()),other_environments_unchanged=int((~mask).sum()),changed_environments=int(mask.sum()),minimum_full_flat_front_support_m=float((torch.abs(xy[mask,0]-center[mask])-ex[0]-span*.5).min()) if mask.any() else .517,local_explicit_selected_source_entry_projection=True,source_original_ids=env._local_projection_original_ids.tolist(),source_SHA=SOURCE['sha256'],no_new_random_stream=True)
 return xy[ids].clone()

def materialize(env,output,local_checkpoint=None):
 from wave50_entry_current_state_v2 import current_state,identity,KEY as EK
 from wave50_route_runtime import state_dict as route_state
 from wave50_lifetime_runtime import state_dict as lifetime_state
 path=Path(SOURCE['path']);assert H(path)==SOURCE['sha256'];ck=torch.load(path,map_location='cpu',weights_only=False)
 same_local=local_checkpoint is not None
 if same_local:
  proof=json.loads(Path(__import__('os').environ['MOD4_LOCAL_REPAIR_SOURCE_PROOF']).read_bytes());assert proof['passed']
  path=Path(local_checkpoint);assert str(path.resolve())==str(Path(proof['checkpoint']['path']).resolve()) and H(path)==proof['checkpoint']['sha256']
  ck=torch.load(path,map_location='cpu',weights_only=False);assert ck['LOCAL_TEMPORARY_BRANCH']['source_SHA']==SOURCE['sha256'] and ck['LOCAL_TEMPORARY_BRANCH']['local_num_envs']==env.num_envs
 assert env.scene.terrain.retention_assignment_sha==ck['E1_terrain_state']['entry_assignment_sha256']
 if same_local:
  ids=torch.arange(env.num_envs);quota=None;bind_selected_entry(env,ids,ck);env._local_projection_original_ids=torch.tensor(ck['LOCAL_TEMPORARY_BRANCH']['source_original_ids'])
 else:ids,quota=select(env,ck);bind_selected_entry(env,ids,ck)
 env.reset();term=env.command_manager.get_term('twist');term._write_dynamic(torch.arange(env.num_envs,device=env.device))
 changes=[];projected=copy.deepcopy(ck) if same_local else project_tree(ck,ids,changes=changes)
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):assert same(ck[key],projected[key]),key
 actual=current_state(env)
 # Original actualworld triangles and allterrain limits must match before newbranch metadata binding.
 for key in ('geometry_triangles_sha256','ordered_partition_triangles_sha256','triangles','G4_profile_sha256','reset_bank_sha256'):assert ck['E1_terrain_state'][key]==actual[key],key
 before=copy.deepcopy(projected['E1_terrain_state']);projected['E1_terrain_state'].update(identity(actual));projected[EK]=identity(projected['E1_terrain_state'])
 assert same(projected['E1_terrain_state']['spawn_xy'],before['spawn_xy']) and same(projected['E1_terrain_state']['reset_expected_q'],before['reset_expected_q']) and same(projected['E1_terrain_state']['episode'],before['episode'])
 projected['E1_retained_flat_command_state']['assignment_sha256']=env.scene.terrain.retention_assignment_sha
 actualstates={'E1_WAVE50_episode_direction_state':term.state_dict_direction(),'E1_WAVE50_route_lifecycle_state':route_state(env,refresh=True),'E1_WAVE50_episode_lifetime_state':lifetime_state(env,refresh=True)}
 for key,st in actualstates.items():
  for k,v in st.items():
   if not isinstance(v,torch.Tensor):projected[key][k]=copy.deepcopy(v)
 if same_local:
  
  for key in ('E1_terrain_state','E1_WAVE50_entry_reset_identity','E1_retained_flat_command_state','E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state'):assert same(ck[key],projected[key]),key
  projected['LOCAL_TEMPORARY_BRANCH']['continued_local_checkpoint_SHA']=H(path)
 else:projected['LOCAL_TEMPORARY_BRANCH']=dict(source_SHA=SOURCE['sha256'],source_num_envs=20000,local_num_envs=env.num_envs,source_original_ids=ids.tolist(),backend='Windows-IsaacSim5.1-PhysX2API',exact_selected_per_environment_values_before_new_episode=True,explicit_identity_migration=True,physical_engine_equivalence_claimed=False)
 q=Path(output)/'LOCAL_PROJECTED_FULLSTATE_SOURCE.pt';assert not q.exists();torch.save(projected,q);roundtrip=torch.load(q,map_location='cpu',weights_only=False);assert same(roundtrip,projected)
 receipt=dict(epoch=__import__('time').time(),passed=True,original_source=dict(path=str(path),sha256=H(path)),projection=dict(path=str(q),sha256=H(q),num_envs=env.num_envs,ids=ids.tolist(),family_counts=quota),all_actor_critic_std_optimizer_global_named_private_RNG_preserved=True,exact_selected_tensor_projection=changes,geometry_identity_exact=True,same_local_identity_resume=same_local,identity_only_changes={k:[n for n in v if not isinstance(v[n],torch.Tensor)] for k,v in actualstates.items()},selected_entry_receipt=env._wave50_entry_map_receipt,source_original_intact=True,not_PhysX_exact_resume=True)
 Path(output,'LOCAL_PROJECTED_STATE_CPU_ADMISSION.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
 return q,receipt
