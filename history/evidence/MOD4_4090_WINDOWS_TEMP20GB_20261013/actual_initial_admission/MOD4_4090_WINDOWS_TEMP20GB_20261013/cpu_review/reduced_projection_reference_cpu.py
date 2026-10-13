"""CPU reference for a separate reduced-env branch; never a GPU dispatcher.

Validate the coherent complete20k donor first. Select exactly the original99
per-environment tensor paths. Actor/critic/std/Adam and all named/private RNG
bytes remain exact; generic future same-reduced resume must not project again.
The selected entry/ABI metadata needs separate actual runtime binding and GPU
validation. This helper does not fabricate those later markers or a lease.
"""
from pathlib import Path
import copy,hashlib,sys
import numpy as np
import torch

W=Path(__file__).resolve().parents[2]
V=W/'MOD4_4090_WINDOWS_REPAIR_20261013/repair_payload/v6a_audited_cpu_payload'
sys.path.insert(0,str(V))
from windows20k_fullstate_binding import validate,floating_count,same,DONOR_SHA,perenv_inventory
PROFILE='windows4090_temp20GB_reduced_projection_CPU_reference_v1'

def project_complete_original(source,source_sha,ids):
 assert source_sha==DONOR_SHA;validate(source,source_sha)
 assert torch.is_tensor(ids) and ids.device.type=='cpu' and ids.dtype==torch.long and ids.ndim==1
 n=len(ids);assert 0<n<20000 and len(torch.unique(ids))==n and int(ids.min())>=0 and int(ids.max())<20000
 changes=[];metadata=[]
 def walk(value,path=''):
  if torch.is_tensor(value):
   axes=[i for i,x in enumerate(value.shape) if x==20000];assert len(axes)<=1
   if axes:
    out=value.index_select(axes[0],ids).clone();changes.append(dict(path=path,axis=axes[0],from_shape=list(value.shape),to_shape=list(out.shape),dtype=str(value.dtype)));return out
   return value.clone()
  if isinstance(value,np.ndarray):
   assert 20000 not in value.shape,'Unexpected perenv NumPy schema requires reviewed selection'
   return value.copy()
  if isinstance(value,dict):
   out={}
   for k,x in value.items():
    if k in ('n','num_envs') and type(x) is int and x==20000:out[k]=n;metadata.append(dict(path=path+'/'+str(k),old=20000,new=n))
    else:out[k]=walk(x,path+'/'+str(k))
   return out
  if isinstance(value,(list,tuple)):
   assert len(value)!=20000,'Unexpected perenv list schema requires reviewed selection'
   return type(value)(walk(x,path+'/'+str(i)) for i,x in enumerate(value))
  return copy.deepcopy(value)
 out=walk(source);assert len(changes)==len(perenv_inventory(source))==99 and floating_count(out)==107
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):assert same(source[key],out[key]),key
 # Selected physical tensors are retained, not replaced by a small-N lane rerank.
 for key in ('spawn_xy','reset_expected_q','episode'):assert same(out['E1_terrain_state'][key],source['E1_terrain_state'][key].index_select(0,ids))
 out['WINDOWS4090_REDUCED_TEMPORARY_BRANCH_CPU_ONLY']=dict(profile=PROFILE,source_complete20k_SHA=source_sha,source_num_envs=20000,temporary_num_envs=n,source_original_ids=ids.tolist(),selected_tensor_paths_exact=True,metadata_runtime_binding_GPU_still_pending=True,CPU_reference_only_not_training_source_admission=True,not_PhysX_exact_resume=True)
 return out,dict(profile=PROFILE,num_envs=n,source_sha=source_sha,exact99_selected_paths=changes,environment_count_metadata_changes=metadata,all107_floating_fields_preserved=True,all_actorcritic_std_Adam_and_globalnamed_private_RNG_exact=True,selected_spawn_expected30q_episode_exact=True,no_CUDA_or_newRNGdraw=True,actual_runtime_geometry_command_entry_direction_route_lifetime_binding_pending=True)
