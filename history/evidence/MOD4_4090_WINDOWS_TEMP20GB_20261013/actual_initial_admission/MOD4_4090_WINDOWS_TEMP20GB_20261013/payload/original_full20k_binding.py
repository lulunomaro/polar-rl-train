"""Complete coherent20k donor binding, with explicit Windows ABI metadata only.

No environment projection, actor splicing, RNG draw or physics-equivalence claim.
The runtime must restore the complete bound donor before the separate initializer.
"""
from pathlib import Path
import copy, hashlib, json, os, time
import numpy as np
import torch

DONOR_SHA='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
INITIAL35_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
PROFILE='windows4090_coherent_full20k_ABI_metadata_binding_v1'
GEOMETRY_SHA='32e0a753c886244c4bfcf24d5523d800e06e0bb1035a78ddc494d6144e2dc4bd'
PARTITION_SHA='c2317e380d49eea6f4647aecfdc46cfbab70b40ddaf059e9e75f2585950aca78'
ASSIGNMENT_SHA='4c9a7f3b596bc055e8501a91a69bc9ffd1c8c58516b955f0003ba1b5031fe73d'
IDENTITY_STATES=('E1_terrain_state','E1_WAVE50_entry_reset_identity','E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state')
# Only hashes of explicitly adapted ABI code and their derived input hash may bind.
# Physical geometry/profile/bank/math/assignment/origin/map are deliberately absent.
ALLOWED_METADATA={
 'E1_terrain_state':{'entry_full_pose_sha256','entry_input_sha256'},
 'E1_WAVE50_entry_reset_identity':{'entry_full_pose_sha256','entry_input_sha256'},
 'E1_WAVE50_episode_direction_state':set(),
 'E1_WAVE50_route_lifecycle_state':{'parent_boundary_source_sha256'},
 'E1_WAVE50_episode_lifetime_state':set(),
}
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def same(a,b):
 if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.detach().cpu(),b.detach().cpu())
 if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and a.dtype==b.dtype and a.shape==b.shape and np.array_equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if isinstance(a,(list,tuple)):return type(a) is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return type(a) is type(b) and a==b
def floating_count(v):
 if isinstance(v,torch.Tensor):
  if v.is_floating_point() or v.is_complex():assert torch.isfinite(v).all();return 1
  return 0
 if isinstance(v,dict):return sum(floating_count(x) for x in v.values())
 if isinstance(v,(list,tuple)):return sum(floating_count(x) for x in v)
 return 0
def perenv_inventory(v,path=''):
 out=[]
 if torch.is_tensor(v) and 20000 in v.shape:out.append((path,tuple(v.shape),str(v.dtype)))
 elif isinstance(v,dict):
  for k,x in v.items():out.extend(perenv_inventory(x,path+'/'+str(k)))
 elif isinstance(v,(tuple,list)):
  for i,x in enumerate(v):out.extend(perenv_inventory(x,path+'/'+str(i)))
 return out
def validate(ck,source_sha):
 assert ck['independent_terrain_expert']=='E1_WAVE50' and ck['E1_WAVE50_initial_source_sha256']==INITIAL35_SHA,'expert/ancestor identity'
 assert 'LOCAL_TEMPORARY_BRANCH' not in ck,'local128 projection is not complete20k'
 t=ck['E1_terrain_state'];assert t['num_envs']==20000 and t['seed']==20260928 and t['layout']==[40,40]
 assert t['geometry_triangles_sha256']==GEOMETRY_SHA and t['ordered_partition_triangles_sha256']==PARTITION_SHA
 assert t['entry_assignment_sha256']==ASSIGNMENT_SHA and t['triangles']==10306304
 assert t['G4_height_peak_to_trough_m']==.05 and t['command_vx_range']==[-.3,.3] and t['command_vy_yaw']==[0.,0.]
 assert len(perenv_inventory(ck))==99,'complete original99perenv tensor schema'
 assert floating_count(ck)==107,'full107 floating tensor schema'
 a=ck['actor_state_dict'];assert list(a)==['distribution.std_param','mlp.0.weight','mlp.0.bias','mlp.2.weight','mlp.2.bias','mlp.4.weight','mlp.4.bias','mlp.6.weight','mlp.6.bias']
 assert a['mlp.0.weight'].shape==(256,35) and a['mlp.6.weight'].shape==(6,64) and a['distribution.std_param'].shape==(6,) and (a['distribution.std_param']>0).all()
 assert ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
 o=ck['optimizer_state_dict'];assert len(o['param_groups'])==1 and o['param_groups'][0]['params']==list(range(17))
 for pid,shape in ((0,(6,)),(7,(6,64)),(8,(6,))):
  assert set(o['state'][pid])=={'step','exp_avg','exp_avg_sq'}
  assert o['state'][pid]['step'].shape==torch.Size([])
  assert all(o['state'][pid][field].shape==shape for field in ('exp_avg','exp_avg_sq'))
 for k in IDENTITY_STATES:assert ck[k]['num_envs']==20000
 if source_sha!=DONOR_SHA:
  b=ck['WINDOWS4090_FULL20K_BACKEND_BINDING'];r=ck['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL']
  assert b['profile']==PROFILE and b['complete_original20k_donor_SHA']==DONOR_SHA and b['num_envs']==20000
  assert r['applied_once_after_complete_source_restore'] and r['original_complete20k_donor_SHA']==DONOR_SHA and not r['CPU_prepared_only']
 return ck
def bind_metadata(ck,actual_states,approved_changes,same_windows=False):
 """Actual-state physical hashes exact; replacement is restricted to review plan."""
 out=copy.deepcopy(ck);changes=[]
 for key in IDENTITY_STATES:
  old=ck[key];actual=actual_states[key]
  old_meta={k:v for k,v in old.items() if not torch.is_tensor(v)}
  actual_meta={k:v for k,v in actual.items() if not torch.is_tensor(v)}
  assert set(old_meta)==set(actual_meta),(key,'metadata schema mismatch')
  for field,value in actual_meta.items():
   if same(old_meta[field],value):continue
   assert not same_windows,'same Windows scope cannot rebind metadata'
   assert field in ALLOWED_METADATA[key],(key,field,'physical identity changed')
   plan=approved_changes[key][field]
   assert plan['old']==old_meta[field] and plan['new']==value and plan['ABI_code_or_derived_hash_only'],(key,field,'unapproved ABI binding')
   out[key][field]=copy.deepcopy(value);changes.append(dict(state=key,field=field,old=old_meta[field],new=value))
 # All99 environment tensors and every nonidentity state tree remain exact.
 assert perenv_inventory(out)==perenv_inventory(ck) and len(perenv_inventory(out))==99
 def tensors(a,b):
  if torch.is_tensor(a):assert same(a,b)
  elif isinstance(a,dict):
   for k,v in a.items():tensors(v,b[k])
  elif isinstance(a,(tuple,list)):
   for v,x in zip(a,b):tensors(v,x)
 tensors(ck,out)
 for key in ck:
  if key not in IDENTITY_STATES:assert same(out[key],ck[key]),key
 assert floating_count(out)==107
 return out,changes
def validate_physical_reset(source,actual):
 for field in ('spawn_xy','reset_expected_q'):assert same(source['E1_terrain_state'][field],actual[field]),field
def materialize(env,output,args,write):
 from wave50_entry_current_state_v2 import current_state,identity,KEY as EK
 from wave50_route_runtime import state_dict as route_state
 from wave50_lifetime_runtime import state_dict as lifetime_state
 assert env.num_envs==20000 and not hasattr(env,'_local_projection_reset_xy')
 path=Path(args.source_checkpoint);assert H(path)==args.source_sha
 ck=validate(torch.load(path,map_location='cpu',weights_only=False),args.source_sha)
 term=env.command_manager.get_term('twist');term._write_dynamic(torch.arange(env.num_envs,device=env.device))
 actual=current_state(env)
 # Actual reset30q and origin/entry coordinates must match original20k source.
 validate_physical_reset(ck,actual)
 assert env.scene.terrain.retention_assignment_sha==ASSIGNMENT_SHA
 states={'E1_terrain_state':actual,EK:identity(actual),'E1_WAVE50_episode_direction_state':term.state_dict_direction(),'E1_WAVE50_route_lifecycle_state':route_state(env,refresh=True),'E1_WAVE50_episode_lifetime_state':lifetime_state(env,refresh=True)}
 plan=json.loads(Path(args.manifest).read_bytes())['approved_ABI_metadata_bindings']
 bound,changes=bind_metadata(ck,states,plan,same_windows=args.source_sha!=DONOR_SHA)
 if args.source_sha==DONOR_SHA:
  bound['WINDOWS4090_FULL20K_BACKEND_BINDING']=dict(profile=PROFILE,complete_original20k_donor_SHA=DONOR_SHA,num_envs=20000,explicit_Linux_to_Windows_ABI_identity_migration=True,all99perenv_tensors_exact_not_projected=True,all_physical_geometry_fullpose_command_entry_direction_route_lifetime_values_exact=True,backend_equivalence_not_claimed=True,PhysX_exact_resume=False,changes=changes)
 q=Path(output)/'WINDOWS4090_BOUND_FULLSTATE_SOURCE.pt';assert not q.exists();torch.save(bound,q)
 with q.open('r+b') as f:f.flush();os.fsync(f.fileno())
 assert same(torch.load(q,map_location='cpu',weights_only=False),bound)
 receipt=dict(epoch=time.time(),pid=os.getpid(),passed=True,source_path=str(path),source_sha256=args.source_sha,bound_source_path=str(q),bound_source_sha256=H(q),original_donor_SHA=DONOR_SHA,num_envs=20000,all99perenv_tensors_exact=True,floating107=True,no_environment_projection_or_source_splice=True,explicit_ABI_metadata_changes=changes,source_original_SHA_unchanged=H(path)==args.source_sha,no_RNG_draw=True,not_PhysX_exact_resume=True)
 write('WINDOWS4090_FULLSTATE_CPU_BINDING_ACTUAL.json',receipt)
 return q,receipt
