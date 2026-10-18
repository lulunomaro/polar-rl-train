"""Read actual reward configuration and post-step fields; never compute extra rewards."""
from pathlib import Path
import inspect,hashlib,json,time
def install(module,context):
 import torch,numpy as np
 original_create=module.create_observed_env;original_finish=module.finalize_observer
 def cpu(x):return x.detach().cpu().numpy().copy() if torch.is_tensor(x) else np.asarray(x).copy()
 def safe(x):
  if torch.is_tensor(x):return x.detach().cpu().tolist()
  if isinstance(x,(str,int,float,bool,type(None))):return x
  if isinstance(x,dict):return {str(k):safe(v) for k,v in x.items()}
  if isinstance(x,(list,tuple)):return [safe(v) for v in x]
  return repr(x)
 def create(*a,**k):
  e=original_create(*a,**k);manager=e.reward_manager;terms=[]
  for name,cfg in zip(manager._term_names,manager._term_cfgs):
   source=inspect.getsourcefile(cfg.func);p=Path(source) if source else None
   terms.append(dict(name=name,weight=cfg.weight,params=safe(cfg.params),function_module=cfg.func.__module__,function_name=getattr(cfg.func,'__qualname__',repr(cfg.func)),actual_source_path=str(p) if p else None,actual_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest() if p and p.is_file() else None))
  context['save']('ACTUAL_LOADED_REWARD_TERMS_WEIGHTS_PARAMS_SOURCE.json',dict(epoch=time.time(),manager_class=type(manager).__module__+'.'+type(manager).__qualname__,terms=terms,no_term_recomputed_or_configuration_changed=True,source_not_loaded_binary_bitexact=True))
  rows=[];context['actual_reward_frame_observation']=dict(rows=rows,env=e);step=e.step
  def observed_step(action):
   value=step(action);r=e.scene['robot'].data;entry=dict(root_state_w=cpu(r.root_state_w),root_lin_vel_b=cpu(r.root_lin_vel_b),root_ang_vel_b=cpu(r.root_ang_vel_b),projected_gravity_b=cpu(r.projected_gravity_b),command=cpu(e.command_manager.get_command('twist')),step_reward=cpu(manager._step_reward))
   for attr in ('_mod4_jump','_mod4_spin','_mod4_recovery'):
    obj=getattr(e,attr,None);active=getattr(obj,'active',None);entry[attr+'_active_present']=np.asarray(torch.is_tensor(active),dtype=np.bool_)
    if torch.is_tensor(active):entry[attr+'_active']=cpu(active)
   rows.append(entry);return value
  e.step=observed_step;return e
 def finish(env,result):
  item=context['actual_reward_frame_observation'];rows=item['rows'];assert rows
  arrays={key:np.stack([r[key] for r in rows]) for key in rows[0]};assert len(rows)==env._retention_native_witness.args.steps
  for key,value in arrays.items():
   if value.dtype.kind in 'fc':assert np.isfinite(value).all(),key
  p=Path(context['output_dir'])/'actual_reward_frame_legacy_readouts.npz';assert not p.exists();np.savez_compressed(p,**arrays)
  context['save']('ACTUAL_REWARD_FRAME_LEGACY_READOUT_COMPLETE.json',dict(epoch=time.time(),controls=len(rows),path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),shapes={k:list(v.shape) for k,v in arrays.items()},absent_legacy_state_kept_absent_not_fabricated_zero=True,no_extra_reward_compute_actor_forward_optimizer_or_RNG=True,not_unique_failure_cause_or_skill_graduation=True));return original_finish(env,result)
 module.create_observed_env=create;module.finalize_observer=finish
