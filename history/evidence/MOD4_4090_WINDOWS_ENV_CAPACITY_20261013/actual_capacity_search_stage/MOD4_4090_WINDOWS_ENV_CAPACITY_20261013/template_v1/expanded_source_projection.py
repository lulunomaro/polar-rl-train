"""CPU-only own128 -> expanded capacity branch. Never reinitialize policy.

The fixed99 path schema excludes neural hidden128 dimensions. Parent-slot copies
are explicit dimension migration, not independent resampling or same128 resume.
The consumer must restore all12 contracts, then one new physical episode. No
CUDA, installed SDK modification, launch, canonical budget write or new RNG.
"""
from pathlib import Path
import copy,hashlib,json,os,time
import numpy as np
import torch

PARENT_N=128
ALLOWED_TARGETS=(256,512,1024)
PROFILE='windows4090_own128_expanded_capacity_state_v1'
PARENT_PROFILE='windows4090_temporary128_memory20GB_selected_source_v9'
DONOR_SHA='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
INITIAL35_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
GEOMETRY_SHA='32e0a753c886244c4bfcf24d5523d800e06e0bb1035a78ddc494d6144e2dc4bd'
PARTITION_SHA='c2317e380d49eea6f4647aecfdc46cfbab70b40ddaf059e9e75f2585950aca78'
ASSIGNMENT_SHA='4c9a7f3b596bc055e8501a91a69bc9ffd1c8c58516b955f0003ba1b5031fe73d'
STATES=('E1_terrain_state','E1_WAVE50_entry_reset_identity','E1_WAVE50_episode_direction_state','E1_WAVE50_route_lifecycle_state','E1_WAVE50_episode_lifetime_state')
EXCLUDED_ROOTS={'actor_state_dict','critic_state_dict','optimizer_state_dict'}
COUNT_PATHS=(('sensor_DR_state','n'),('feedback_delay_state','n'),('physical_action_delay_state','n'),('spring_pressure_state','n'),('gas_damping_state','n'),('chassis_PD_state','COM','num_envs'),('chassis_PD_state','PD','num_envs'),*((k,'num_envs') for k in STATES),('E1_retained_flat_command_state','num_envs'))
CODE_BIND_FIELDS={'E1_terrain_state':{'entry_runtime_sha256','entry_full_pose_sha256'},'E1_WAVE50_entry_reset_identity':{'entry_runtime_sha256','entry_full_pose_sha256'},'E1_WAVE50_episode_direction_state':set(),'E1_WAVE50_route_lifecycle_state':{'parent_boundary_source_sha256'},'E1_WAVE50_episode_lifetime_state':set()}

def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def same(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.shape==b.shape and a.dtype==b.dtype and torch.equal(a.cpu(),b.cpu())
 if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and a.shape==b.shape and a.dtype==b.dtype and np.array_equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return type(a)is type(b) and a==b
def floating_count(v):
 if torch.is_tensor(v):
  assert v.device.type=='cpu','CPU source only'
  if v.is_floating_point() or v.is_complex():assert torch.isfinite(v).all();return 1
  return 0
 if isinstance(v,dict):return sum(floating_count(x) for x in v.values())
 if isinstance(v,(tuple,list)):return sum(floating_count(x) for x in v)
 return 0
def at(tree,tokens):
 for token in tokens:tree=tree[token]
 return tree
def put(tree,tokens,value):
 parent=at(tree,tokens[:-1]);assert not isinstance(parent,tuple),'tensor tuple replacement occurs in recursive copier only';parent[tokens[-1]]=value
def inventory(v,n,path=()):
 if torch.is_tensor(v):
  if path and path[0] not in EXCLUDED_ROOTS and n in v.shape:return [dict(tokens=list(path),shape=list(v.shape),dtype=str(v.dtype),axis=next(i for i,k in enumerate(v.shape) if k==n))]
  return []
 if isinstance(v,dict):return [row for k,x in v.items() for row in inventory(x,n,path+(k,))]
 if isinstance(v,(tuple,list)):return [row for i,x in enumerate(v) for row in inventory(x,n,path+(i,))]
 return []
def schema(path=None):
 p=Path(path) if path else Path(__file__).with_name('PERENV128_SCHEMA_V1.json');x=json.loads(p.read_bytes())
 assert x['parent_n']==PARENT_N and len(x['fields'])==99 and len({tuple(r['tokens']) for r in x['fields']})==99
 return x['fields'],H(p)
def network_validate(ck):
 a=ck['actor_state_dict'];c=ck['critic_state_dict'];o=ck['optimizer_state_dict']
 keys=['distribution.std_param','mlp.0.weight','mlp.0.bias','mlp.2.weight','mlp.2.bias','mlp.4.weight','mlp.4.bias','mlp.6.weight','mlp.6.bias']
 assert list(a)==keys and list(c)==keys[1:]
 sizes={'mlp.0.weight':(256,35),'mlp.0.bias':(256,),'mlp.2.weight':(128,256),'mlp.2.bias':(128,),'mlp.4.weight':(64,128),'mlp.4.bias':(64,),'mlp.6.weight':(6,64),'mlp.6.bias':(6,),'distribution.std_param':(6,)}
 for k,shape in sizes.items():assert a[k].shape==shape
 for k in keys[1:]:assert c[k].shape==((256,38) if k=='mlp.0.weight' else ((1,64) if k=='mlp.6.weight' else ((1,) if k=='mlp.6.bias' else sizes[k])))
 assert (a['distribution.std_param']>0).all() and len(o['param_groups'])==1 and o['param_groups'][0]['params']==list(range(17))
 params=list(a.values())+list(c.values());assert set(o['state'])==set(range(17))
 for i,p in enumerate(params):
  st=o['state'][i];assert set(st)=={'step','exp_avg','exp_avg_sq'} and st['step'].shape==torch.Size([])
  assert st['exp_avg'].shape==st['exp_avg_sq'].shape==p.shape
def _common(ck,n):
 network_validate(ck);assert floating_count(ck)==107
 assert ck['independent_terrain_expert']=='E1_WAVE50' and ck['E1_WAVE50_initial_source_sha256']==INITIAL35_SHA
 t=ck['E1_terrain_state'];assert t['num_envs']==n and t['seed']==20260928 and t['layout']==[40,40]
 assert t['geometry_triangles_sha256']==GEOMETRY_SHA and t['ordered_partition_triangles_sha256']==PARTITION_SHA
 assert t['entry_assignment_sha256']==ASSIGNMENT_SHA and t['triangles']==10306304 and t['G4_height_peak_to_trough_m']==.05
 assert t['command_vx_range']==[-.3,.3] and t['command_vy_yaw']==[0.,0.]
 m=hashlib.sha256(t['spawn_xy'].numpy().astype('<f4').tobytes()).hexdigest()
 assert t['entry_map_sha256']==t['entry_origin_sha256']==m
 assert ck['E1_WAVE50_entry_reset_identity']=={k:v for k,v in t.items() if not torch.is_tensor(v)}
 for k in STATES:assert ck[k]['num_envs']==n
 for k in STATES[2:]:
  assert ck[k]['assignment_sha256']==ASSIGNMENT_SHA and ck[k]['entry_map_sha256']==ck[k]['entry_origin_sha256']==m
  assert same(ck[k]['bound_episode'],t['episode'])
 assert same(ck['E1_WAVE50_route_lifecycle_state']['spawn_xy'],t['spawn_xy']) and same(ck['E1_WAVE50_episode_direction_state']['reset_xy'],t['spawn_xy'])
 r=ck['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL'];assert r['original_complete20k_donor_SHA']==DONOR_SHA and r['applied_once_after_complete_source_restore'] and not r['CPU_prepared_only']
 assert r.get('initializer_repeated_on_this_resume',False)is False
def validate_parent128(ck):
 _common(ck,PARENT_N);b=ck['WINDOWS4090_TEMPORARY_BRANCH'];assert b['profile']==PARENT_PROFILE and b['num_envs']==128 and b['original20k_donor_SHA']==DONOR_SHA
 ids=b['source_original_ids'];assert len(ids)==len(set(ids))==128 and all(type(i)is int and 0<=i<20000 for i in ids)
 assert b['family_counts']==[38,26,26,19,19] and 'WINDOWS4090_EXPANDED_ENV_BRANCH' not in ck
 fields,_=schema();assert inventory(ck,128)==fields
 return ck
def repeat_index(target_n):
 assert type(target_n)is int and target_n in ALLOWED_TARGETS
 return torch.arange(target_n,dtype=torch.long)%PARENT_N
def expand_tree(source,*,source_sha,target_n):
 assert len(source_sha)==64 and source_sha!=DONOR_SHA,'Own repaired128 source required, not old20k donor'
 validate_parent128(source);fields,schema_sha=schema();mapping=repeat_index(target_n);by_path={tuple(x['tokens']):x for x in fields};changes=[]
 def visit(v,path=()):
  if torch.is_tensor(v):
   if path in by_path:
    row=by_path[path];assert list(v.shape)==row['shape'] and str(v.dtype)==row['dtype']
    assert row['shape'].count(128)==1 and row['axis']==0
    out=v.index_select(row['axis'],mapping).clone();assert v.data_ptr()!=out.data_ptr()
    changes.append(dict(tokens=list(path),axis=row['axis'],parent_shape=list(v.shape),child_shape=list(out.shape),dtype=str(v.dtype)))
    return out
   return v.clone()
  if isinstance(v,dict):return {k:visit(x,path+(k,)) for k,x in v.items()}
  if isinstance(v,list):return [visit(x,path+(i,)) for i,x in enumerate(v)]
  if isinstance(v,tuple):return tuple(visit(x,path+(i,)) for i,x in enumerate(v))
  return copy.deepcopy(v)
 out=visit(source);assert len(changes)==99
 count_changes=[]
 for path in COUNT_PATHS:
  assert at(out,path)==128;put(out,path,target_n);count_changes.append(dict(tokens=list(path),old=128,new=target_n))
 m=hashlib.sha256(out['E1_terrain_state']['spawn_xy'].numpy().astype('<f4').tobytes()).hexdigest();inputsha=hashlib.sha256((m+ASSIGNMENT_SHA+DONOR_SHA).encode()).hexdigest();identity_changes=[]
 for state in STATES:
  for field,value in (('entry_map_sha256',m),('entry_origin_sha256',m),('entry_input_sha256',inputsha)):
   if field in out[state]:identity_changes.append(dict(state=state,field=field,old=out[state][field],new=value));out[state][field]=value
 parent_ids=source['WINDOWS4090_TEMPORARY_BRANCH']['source_original_ids'];mult=target_n//128
 b=out['WINDOWS4090_TEMPORARY_BRANCH'];b.update(profile=PROFILE,num_envs=target_n,source_original_ids=[parent_ids[i] for i in mapping.tolist()],family_counts=[x*mult for x in b['family_counts']])
 out['WINDOWS4090_EXPANDED_ENV_BRANCH']=dict(profile=PROFILE,num_envs=target_n,parent_num_envs=128,parent_checkpoint_SHA=source_sha,parent_branch_profile=PARENT_PROFILE,original20k_donor_SHA=DONOR_SHA,child_slot_ids=list(range(target_n)),parent_slot_ids=mapping.tolist(),parent_original20k_source_ids=list(parent_ids),ancestor20k_source_ids=[parent_ids[i] for i in mapping.tolist()],fixed99_schema_SHA=schema_sha,CPU_prepared_only=True,actual_runtime_metadata_bound=False,original99_perenv_parent_slot_repeat_exact=True,actor_critic_std_Adam_globalnamed_private_CPUCUDA_exact=True,all_saved_parent_generators_retained_not_duplicated_or_newly_drawn=True,global_command_histograms_retained_not_multiplied=True,duplicate_ancestor_ids_not_duplicate_child_ids=True,left_initializer_repeated=False,not_same128_or_complete20k_or_PhysX_exact_resume=True,new_physical_episode_source_parent_slot_plus_one_required=True,all12_own_CPUCUDA_restore_disk_roundtrip_and_API_offsets_pending=True)
 # Historical backend and128 initialization receipts remain byte-exact; they
 # must not be falsely relabelled as256/512/1024 actualGPU evidence.
 assert same(out['WINDOWS4090_TEMPORARY_BACKEND_BINDING'],source['WINDOWS4090_TEMPORARY_BACKEND_BINDING'])
 assert same(out['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL'],source['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL'])
 validate_expanded(out,target_n=target_n)
 return out,dict(profile=PROFILE,parent_SHA=source_sha,target_num_envs=target_n,parent_slot_mapping=mapping.tolist(),schema_SHA=schema_sha,exact99_tensor_paths=changes,count_metadata_changes=count_changes,explicit_identity_hash_changes=identity_changes,CPU_prepared_only=True,actual_runtime_binding_and_GPU_admission_pending=True,no_new_RNG=True,no_initializer_called=True)
def validate_expanded(ck,*,target_n):
 assert target_n in ALLOWED_TARGETS;_common(ck,target_n);b=ck['WINDOWS4090_EXPANDED_ENV_BRANCH'];t=ck['WINDOWS4090_TEMPORARY_BRANCH']
 assert b['profile']==t['profile']==PROFILE and b['num_envs']==t['num_envs']==target_n and b['parent_num_envs']==128
 assert b['original20k_donor_SHA']==t['original20k_donor_SHA']==DONOR_SHA and len(b['parent_checkpoint_SHA'])==64 and b['parent_checkpoint_SHA']!=DONOR_SHA
 assert b['child_slot_ids']==list(range(target_n)) and len(set(b['child_slot_ids']))==target_n
 assert b['parent_slot_ids']==repeat_index(target_n).tolist() and len(set(b['parent_original20k_source_ids']))==128
 ancestors=[b['parent_original20k_source_ids'][i] for i in b['parent_slot_ids']]
 assert b['ancestor20k_source_ids']==t['source_original_ids']==ancestors
 assert all(type(i)is int and 0<=i<20000 for i in ancestors)
 assert t['family_counts']==[x*(target_n//128) for x in (38,26,26,19,19)]
 assert not b['left_initializer_repeated'];fields,sh=schema();assert b['fixed99_schema_SHA']==sh
 expected=[dict(row,shape=[target_n if i==row['axis'] else k for i,k in enumerate(row['shape'])]) for row in fields]
 assert inventory(ck,target_n)==expected,'exact99 perenv paths/axis/dtype required, neural dimensions excluded'
 return ck
def bind_runtime_metadata_once(ck,*,target_n,actual_states,approved_code_changes):
 """Only frozen code hash migration. Computed map/origin/physical values exact.

 actual_states must come from current physical birth and original state getters.
 This helper never updates tensors or obtains/chooses expected from actualoutput.
 Subsequent same-expanded resumes use require_same_runtime_metadata instead.
 """
 validate_expanded(ck,target_n=target_n);b=ck['WINDOWS4090_EXPANDED_ENV_BRANCH'];assert b['CPU_prepared_only'] and not b['actual_runtime_metadata_bound']
 for field in ('spawn_xy','reset_expected_q'):assert same(ck['E1_terrain_state'][field],actual_states['E1_terrain_state'][field]),(field,'actual birth must preserve parent-slot physical reset')
 out=copy.deepcopy(ck);changes=[]
 for state in STATES:
  a={k:v for k,v in ck[state].items() if not torch.is_tensor(v)};actual={k:v for k,v in actual_states[state].items() if not torch.is_tensor(v)};assert set(a)==set(actual)
  for field,v in actual.items():
   if same(a[field],v):continue
   assert field in CODE_BIND_FIELDS[state],(state,field,'physical/map/profile identity cannot migrate again')
   plan=approved_code_changes[state][field];assert plan==dict(old=a[field],new=v,explicit_frozen_code_binding_only=True)
   out[state][field]=copy.deepcopy(v);changes.append(dict(state=state,field=field,old=a[field],new=v))
 out['WINDOWS4090_EXPANDED_ENV_BRANCH'].update(CPU_prepared_only=False,actual_runtime_metadata_bound=True,approved_code_binding_changes=changes)
 validate_expanded(out,target_n=target_n);return out,changes
def require_same_runtime_metadata(ck,*,target_n,actual_states):
 validate_expanded(ck,target_n=target_n);b=ck['WINDOWS4090_EXPANDED_ENV_BRANCH'];assert b['actual_runtime_metadata_bound'] and not b['CPU_prepared_only']
 for state in STATES:
  a={k:v for k,v in ck[state].items() if not torch.is_tensor(v)};actual={k:v for k,v in actual_states[state].items() if not torch.is_tensor(v)}
  assert same(a,actual),(state,'same expanded scope forbids all metadata rebinding')
 return True
def materialize(source_path,*,expected_source_sha,target_n,output_dir):
 """Fresh CPU candidate and fsynced proof only. Never invokes GPU/worker."""
 path=Path(source_path);assert H(path)==expected_source_sha;assert not torch.cuda.is_initialized()
 rng=torch.get_rng_state().clone();source=torch.load(path,map_location='cpu',weights_only=False)
 candidate,proof=expand_tree(source,source_sha=expected_source_sha,target_n=target_n)
 out=Path(output_dir);assert not out.exists();out.mkdir(parents=True)
 p=out/('EXPANDED_OWN128_TO_'+str(target_n)+'_CPU_CANDIDATE.pt');torch.save(candidate,p)
 with p.open('r+b') as f:f.flush();os.fsync(f.fileno())
 reread=torch.load(p,map_location='cpu',weights_only=False);assert same(candidate,reread);validate_expanded(reread,target_n=target_n)
 assert H(path)==expected_source_sha and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 proof.update(epoch=time.time(),passed_CPU_math_and_disk_only=True,source=dict(path=str(path),bytes=path.stat().st_size,sha256=expected_source_sha),candidate=dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)),floating107=True,source_unmodified=True,actual_CUDA_12restore_and_capacity_not_claimed=True)
 q=out/'CPU_EXPANSION_ACTUAL.json'
 with q.open('xb') as f:f.write(json.dumps(proof,indent=2).encode());f.flush();os.fsync(f.fileno())
 return p,proof
