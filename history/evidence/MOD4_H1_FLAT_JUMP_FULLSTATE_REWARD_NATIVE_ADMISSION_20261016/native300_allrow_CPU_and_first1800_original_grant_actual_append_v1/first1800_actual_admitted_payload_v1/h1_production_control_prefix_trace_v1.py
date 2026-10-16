"""Read-only sampling/control evidence and immutable pre-update full checkpoints.

Never recomputes observations, samples actions, advances RNG, changes forces or inputs.
Control-rate training records are not full physical-callback replay evidence.
"""
from pathlib import Path
import time,json,hashlib,traceback
import torch,numpy as np
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
class H1ControlPrefixTrace:
 def __init__(self,runner,folder):
  self.runner=runner;self.vec=runner.env;self.env=self.vec.unwrapped;self.folder=Path(folder);self.folder.mkdir();self.rows=[];self.index=[];self.source_models=[];self.observed=None;self.frame=None;self.terms=list(self.env.reward_manager._term_names);self.total=0
 def install(self):
  old_act=self.runner.alg.act;old_step=self.vec.step;old_term=self.env.termination_manager.compute;old_reward=self.env.reward_manager.compute
  def act(obs,*args,**kwargs):
   if not self.rows:
    p=self.folder/('preupdate_fullsource_'+str(len(self.source_models))+'.pt');tmp=p.with_suffix('.pt.partial');self.runner.save(str(tmp));tmp.replace(p);self.source_models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p),before_control=self.total,no_optimizer_call=True))
   self.observed=dict(policy35=obs['policy'].detach().clone(),critic38=obs['critic'].detach().clone());return old_act(obs,*args,**kwargs)
  def term(*args,**kwargs):
   value=old_term(*args,**kwargs)
   import mod4_task as task
   e=self.env;r=e.scene['robot'];p=e.h1_phase;self.frame=dict(root13=r.data.root_state_w.detach().clone(),q30=r.data.joint_pos.detach().clone(),joint_velocity=r.data.joint_vel.detach().clone(),applied_torque=r.data.applied_torque.detach().clone(),executed6=e.action_manager.action.detach().clone(),history5ms=e._integrated_contact.history.detach().clone(),impulse=e._integrated_contact.impulse.detach().clone(),closure=torch.stack(list(task.closure_errors(e).values())).amax(0),mimic=torch.stack(list(task.mimic_errors(e).values())).amax(0),public_request=p.request_for_action.detach().clone(),event_expected=p.event_control.detach().clone(),takeoff_count=p.takeoff_count.detach().clone(),landing_count=p.landing_count.detach().clone(),recovery_count=p.recovery_count.detach().clone(),episode=e._sensor_mild.episode.detach().clone());return value
  def reward(dt,*args,**kwargs):
   result=old_reward(dt,*args,**kwargs)
   if self.frame is not None:self.frame['reward_term_contribution']=self.env.reward_manager._step_reward.detach().clone()*self.env.h1_reward_readout_scale
   return result
  def step(actions):
   raw=actions.detach().clone();self.frame=None
   try:
    output=old_step(actions);obs,reward,done,info=output;assert self.frame is not None and self.observed is not None;row={**self.observed,**self.frame,'raw_sampled6':raw,'total_reward':reward.detach().clone(),'done':done.detach().clone()};self.rows.append({k:v.detach().cpu().numpy().copy() for k,v in row.items()});self.total+=1
    if len(self.rows)==24:self.persist()
    return output
   except BaseException:
    put(self.folder/'ACTUAL_STEP_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),completed_control_rows=self.total,failed_current_control_not_claimed_complete=True));self.persist();raise
  self.runner.alg.act=act;self.vec.step=step;self.env.termination_manager.compute=term;self.env.reward_manager.compute=reward
 def persist(self):
  if self.rows:
   p=self.folder/('control_prefix_'+str(len(self.index))+'.npz');tmp=p.with_suffix('.npz.partial')
   with tmp.open('xb') as f:np.savez_compressed(f,**{k:np.stack([x[k] for x in self.rows]) for k in self.rows[0]})
   tmp.replace(p);self.index.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p),controls=len(self.rows),preupdate_source=self.source_models[len(self.index)]));self.rows.clear()
  put(self.folder/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json',dict(epoch=time.time(),controls=self.total,index=self.index,preupdate_full_sources=self.source_models,reward_terms=self.terms,physical_callback_replay=False,no_extra_actor_forward_or_RNG_draw=True,raw_sampled_action_and_actualclip_execution_separate=True,all_success_and_failed_control_prefixes_retained=True))
