"""Explicit frozen variant extra-state owner, no model-I/O on import.
Future helper restores complete saved extras BEFORE lower original E1helper's
ONEfreshreset, audits source extras after; never regenerates saved axis/metadata.
No RNGdraw/reseed/NCCL/physics/optimizer or physical qualification gate here.
"""
import copy
PROTECTED='CURB_PROTECTED878'
INDEPENDENT=('CURB_INDEPENDENT113','SLOPE_INDEPENDENT50')

def required_extra_keys(variant):
 if variant==PROTECTED:return ('distributed_rank_contract',)
 if variant in INDEPENDENT:return ('independent_expert_scope_state','independent_expert_task_contract')
 raise ValueError('Explicit frozen variant only')

def tree_to_device(value,device,torch_module):
 if torch_module.is_tensor(value):return value.detach().clone().to(device=device)
 if isinstance(value,dict):return type(value)((k,tree_to_device(v,device,torch_module)) for k,v in value.items())
 if isinstance(value,list):return [tree_to_device(v,device,torch_module) for v in value]
 if isinstance(value,tuple):return tuple(tree_to_device(v,device,torch_module) for v in value)
 return copy.deepcopy(value)

def install_saved_curb_axis_writer(env,torch_module):
 # Exact original producer bind_after_restore.write body; no recompute of
 # source saved reset_direction from freshly reset terrain/randomstate.
 torch=torch_module;x=env._independent_expert_axis_cache;term=env.command_manager.get_term('twist');old=term._write_dynamic
 def write(ids):
  old(ids)
  if term.manual_evaluation_mode:return
  ids=torch.as_tensor(ids,device=env.device,dtype=torch.long);selected=ids[x['target'][ids]&~term.is_standing_env[ids]]
  term.vel_command_b[selected,0]=.3*x['reset_direction'][selected];term.vel_command_b[selected,1:]=0.;term.linear_vx[selected]=term.vel_command_b[selected,0]
 term._write_dynamic=write
 return write

def restore_extra_before_original_reset(env,source,*,variant,torch_module,writer_installer=None):
 keys=required_extra_keys(variant)
 if any(k not in source for k in keys):raise ValueError('Full selectedvariant extra state required; never silently drop/assume none')
 if variant==PROTECTED:
  saved=source['distributed_rank_contract']
  if not isinstance(saved,dict) or saved.get('rank')!=0 or saved.get('world_size')!=3 or saved.get('per_rank_envs')!=20000:raise ValueError('Protectedrank0/oneactor/threerankhistory contract required')
  env._frozen_distributed_rank_contract=copy.deepcopy(saved)
  return dict(variant=variant,keys=keys,rank0_only_future_single_envscene=True,historical_world_size_preserved=3,future_NCCL_spawn_or_rank_RNGfork=False)
 saved=source['independent_expert_scope_state'];contract=source['independent_expert_task_contract']
 if not isinstance(saved,dict) or not isinstance(contract,dict):raise ValueError('Complete independent scope+task dict required')
 fields={'centers','target','origin','kind','original_private_RNG_draws_unchanged'}
 if variant=='CURB_INDEPENDENT113':fields.add('reset_direction')
 if not fields<=set(saved):raise ValueError('Known saved independent axis fields required; unknown extras retained')
 expected='CURB20' if variant=='CURB_INDEPENDENT113' else 'SLOPE5'
 if saved['kind']!=expected or contract.get('kind')!=expected:raise ValueError('OwnCURB/SLOPE task semantics required')
 for k,shape in [('centers',(20000,2)),('origin',(20000,2)),('target',(20000,))]+([('reset_direction',(20000,))] if variant=='CURB_INDEPENDENT113' else []):
  if tuple(saved[k].shape)!=shape:raise ValueError('Complete original20k extra tensor shape required:'+k)
 env._independent_expert_axis_cache=tree_to_device(saved,env.device,torch_module);env._frozen_independent_expert_task_contract=copy.deepcopy(contract)
 if variant=='CURB_INDEPENDENT113':
  install=writer_installer or install_saved_curb_axis_writer;env._frozen_independent_axis_write=install(env,torch_module)
 return dict(variant=variant,keys=keys,complete_axis_keys=list(saved),unknown_axis_keys_preserved=sorted(set(saved)-fields),axis_not_rebuilt_from_new_reset=True,private_RNG_draws_or_reseed=0)

def extra_state(env,*,variant):
 if variant==PROTECTED:return dict(distributed_rank_contract=copy.deepcopy(env._frozen_distributed_rank_contract))
 if variant in INDEPENDENT:return dict(independent_expert_scope_state=env._independent_expert_axis_cache,independent_expert_task_contract=copy.deepcopy(env._frozen_independent_expert_task_contract))
 raise ValueError('Explicit frozen variant only')

def finish_extra_after_original_reset(env,source,*,variant,torch_module,exact):
 # Same deterministic writeALL performed by original producer bind_after_restore;
 # no reset/resampling/RNG/physicalstep. Stored direction remains saved, not rebuilt.
 if variant=='CURB_INDEPENDENT113':env._frozen_independent_axis_write(torch_module.arange(env.num_envs,device=env.device))
 current=extra_state(env,variant=variant)
 if not exact(current,{k:source[k] for k in required_extra_keys(variant)}):raise ValueError('Original complete savedextras must remain exact across ONElowerreset')
 return dict(variant=variant,all_saved_extra_fields_before_after_exact=True,source_fieldkeys=list(current),physical_reset_or_step_calls_added=0,RNG_draw_or_reseed_calls_added=0,original_axis_writer_semantics_preserved=variant=='CURB_INDEPENDENT113')

def merge_extra_into_own_save(complete_state,env,*,variant):
 # New root, extras only as original producer wrote; no newcheckpointclock/kind
 # and no unknown-root/unknown-axis dropping. Caller retains original savechain.
 merged=dict(complete_state)
 for k,v in extra_state(env,variant=variant).items():merged[k]=v
 return merged
