"""Real original MOD4 environment -> SuperMimic (model-based BPTT) data bridge.
No SDK physics differentiation claim; no task/reward/DR/threshold changes.
Terminal physical s1 is captured at original termination computation before reset.
Terminal xi1 actor-observation is unavailable without new sensor sampling: masked,
never silently substitute post-reset observation into a terminal target.
"""
from pathlib import Path
from dataclasses import dataclass
import io,json,hashlib,copy,time
import torch
from supermimic_vendor_v2.geometry import invariant_features,unflatten_state
from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY,SUPERMIMIC_TRANSITION_KEY

@dataclass
class BridgeState:
 info:dict
 reward:torch.Tensor
 terminated:torch.Tensor
 truncated:torch.Tensor
 obs:dict

class PinnedTeacher:
 def __init__(self,task):
  p=Path(task['teacher_path']);raw=p.read_bytes();assert len(raw)==task['teacher_bytes']and hashlib.sha256(raw).hexdigest()==task['teacher_SHA'];self.raw=raw;self.root=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);self.task=task;self.freeze=self._freeze(self.root);self.actor=None
 def _freeze(self,x):
  if torch.is_tensor(x):return('tensor',x,x._version,tuple(x.shape),x.dtype)
  if isinstance(x,dict):return('dict',x,[(k,self._freeze(v))for k,v in x.items()])
  if isinstance(x,(tuple,list)):return(type(x).__name__,x,[self._freeze(v)for v in x])
  return('value',x,copy.deepcopy(x))
 def _same(self,x,f):
  kind=f[0]
  if kind=='tensor':assert x is f[1]and x._version==f[2]and tuple(x.shape)==f[3]and x.dtype==f[4];return
  if kind=='dict':
   assert x is f[1]and list(x)==[k for k,_ in f[2]]
   for k,v in f[2]:self._same(x[k],v)
  elif kind in('tuple','list'):
   assert x is f[1]and len(x)==len(f[2])
   for v,z in zip(x,f[2]):self._same(v,z)
  else:
   if hasattr(x,'shape'):assert x is f[1]
   else:assert x==f[2]
 def assert_frozen(self):self._same(self.root,self.freeze)
 def build_actor(self,device):
  from tensordict import TensorDict
  from rsl_rl.models import MLPModel
  obs=TensorDict(dict(policy=torch.zeros(2,35),critic=torch.zeros(2,38)),batch_size=[2]);distribution=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar')
  with torch.random.fork_rng(devices=[]):a=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=distribution);a.load_state_dict(self.root['actor_state_dict'],strict=True)
  a.to(device).eval().requires_grad_(False);self.actor=a;self.assert_frozen();return a
 def receipt(self):return dict(source_path=self.task['teacher_path'],source_SHA=self.task['teacher_SHA'],source_bytes=len(self.raw),physical_byte_opens=1,SHA_calculations=1,decodes=1,whole_bootstrap_checkpoint_retained=True,original_PPO_optimizer_preserved_not_restored_to_new_BPTT=True,teacher_frozen=True)

class OriginalTaskMdp:
 num_joints=30;action_dim=6;goal_frame_dim=3;max_step_reward=1.
 def __init__(self,context_dim,physical_sample):
  self.context_dim=context_dim;self.invariant_dim=int(invariant_features(unflatten_state(physical_sample[:1])).shape[-1]);self.actor_context_offset=self.invariant_dim+6;self.obs_dim=self.actor_context_offset+context_dim
 def to(self,device):return self
 def normalize_context(self,context):return context
 def add_noise(self,obs):return obs
 def obs(self,state,previous_action,context,frames):return torch.cat((invariant_features(state),previous_action,context),-1)
 def goal_with_context(self,frames,num_frames,context):return context[...,:3].repeat(*([1]*(context.ndim-1)),num_frames)
 def goal(self,*a,**k):raise RuntimeError('Original task requires current context; no H1/LQR analytic goal substitution')
 def reward(self,*a,**k):raise RuntimeError('Use context-aware learned original environment reward head')
 def soft_termination(self,*a,**k):raise RuntimeError('Use learned original masked termination head, not new orientation threshold')
 def critic_features(self,state,frames,normalized_context):return torch.cat((invariant_features(state),normalized_context,frames.float()[...,None]/1000.),-1)
 def project_predicted_context(self,context,state1,action,frames):
  # Exact original observation slots, not a new observation or action semantics.
  out=context.clone();out[...,14:16]=0.;out[...,22:28]=action;return out
 def valid_imagination_start_with_context(self,frames,horizon,context):return torch.ones_like(frames,dtype=torch.bool)
 def valid_imagination_start(self,frames,horizon):return torch.ones_like(frames,dtype=torch.bool)

class TeacherResidualPolicy(torch.nn.Module):
 def __init__(self,residual,teacher,offset,scale=.05):
  super().__init__();self.residual=residual;self.teacher=teacher;self.offset=offset;self.scale=scale;teacher.eval().requires_grad_(False)
  assert isinstance(residual.dec[-1],torch.nn.Linear)
  with torch.no_grad():residual.dec[-1].weight.zero_();residual.dec[-1].bias.zero_()
 @property
 def obs_norm(self):return self.residual.obs_norm
 @property
 def goal_norm(self):return self.residual.goal_norm
 def forward(self,history,goal):
  from tensordict import TensorDict
  obs=history[...,-1,self.offset:self.offset+35];td=TensorDict(dict(policy=obs),batch_size=list(obs.shape[:-1]));base=self.teacher(td,stochastic_output=False);delta=self.residual(history,goal)
  return(base+self.scale*delta).clamp(-6.,6.)

class NativeTaskBridge:
 def __init__(self,env,task,out,tensor,teacher,initial_obs=None):
  self.initial_obs=initial_obs;self.real=env;self.num_envs=env.num_envs;self.device=torch.device(env.device);self.task=task;self.out=Path(out);self.tensor=tensor;self.teacher=teacher;self.controls=0;self.physics_start=int(env._integrated_contact.tick);self.feedback_start=int(env._feedback_100hz_tick);self.ep_step=torch.zeros(self.num_envs,dtype=torch.int32,device=self.device);self.last_action=torch.zeros(self.num_envs,6,device=self.device);self.state=None;self.pre=None;self.learner=None;self.observed_context_layout=None;self.metrics_terms={k:0 for k in env.termination_manager.active_terms};self.explicit_resets=0;self.initialized=False;self._oldterm=env.termination_manager.compute;env.termination_manager.compute=self._termination_capture
 def _t(self,x):return self.tensor(x).detach().clone()
 @torch.no_grad()
 def pack(self):
  r=self.real.scene['robot'];root=self._t(r.data.root_state_w);root[:,:3]-=self.real.scene.env_origins;root[:,3:7]=root[:,[6,3,4,5]]
  return torch.cat((root,self._t(r.data.joint_pos),self._t(r.data.joint_vel)),-1)
 @torch.no_grad()
 def _termination_capture(self,*a,**k):
  value=self._oldterm(*a,**k);tm=self.real.termination_manager;self.pre=dict(s1=self.pack(),term=tm.terminated.clone(),trunc=tm.time_outs.clone())
  for name in self.metrics_terms:self.metrics_terms[name]+=int(tm.get_term(name).sum())
  return value
 @torch.no_grad()
 def context(self,obs):
  e=self.real;r=e.scene['robot'];values=[('actor35_original',self._t(obs['policy']))]
  def add(name,x,scale=1.):
   if x is None:return
   if isinstance(x,dict):
    for key,value in x.items():add(name+'_'+str(key),value,scale)
    return
   if not(torch.is_tensor(x)or hasattr(x,'torch')):return
   x=self._t(x)
   if x.ndim<1 or x.shape[0]!=self.num_envs:return
   x=x.reshape(self.num_envs,-1)
   if x.shape[1]>128:return
   values.append((name,x.float()*scale))
  add('contact_history',getattr(e._integrated_contact,'history',None),.01);add('applied_torque',r.data.applied_torque,.02)
  for name in('factor','mass_factor','inertia_factor','gain_factor'):add('mild_'+name,getattr(e._mild_dr,name,None))
  for name in('legs','wheels'):
   g=e._physics_action_delay.queue.groups[name]
   for key in('lag_steps','pending','applied'):add('delay_'+name+'_'+key,g.get(key),.5 if key=='lag_steps'else 1.)
  add('feedback_delay',getattr(e._feedback_delay_mild,'delay',None))
  for obj,key in((e._spring_pressure.component,'factor'),(e._gas_damping.component,'factor'),(e._chassis_com.component,'delta_m')):add(type(obj).__name__+'_'+key,getattr(obj,key,None),200. if key=='delta_m'else 1.)
  pd=getattr(e._explicit_pd.component,'factor',{})
  if isinstance(pd,dict):
   for k,v in pd.items():add('PD_'+k,v)
  else:add('PD_factor',pd)
  cmd=e.command_manager.get_term('twist')
  for key in('direction','sign','heading','_command_heading','time_left','age','mode','key'):add('command_'+key,getattr(cmd,key,None),.01 if key in('time_left','age')else 1.)
  recovery=getattr(e,'recovery',None)
  if recovery is not None:
   for key in('age','recipe','request','credited','stable'):add('recovery_'+key,getattr(recovery,key,None),.01 if key in('age','stable')else 1.)
  layout=[(n,int(v.shape[1]))for n,v in values]
  if self.observed_context_layout is None:self.observed_context_layout=layout
  assert layout==self.observed_context_layout,'Context must keep named dimensional identity across episodes'
  out=torch.cat([v for _,v in values],-1);assert out.shape[1]>=35 and torch.isfinite(out).all();return out
 @torch.no_grad()
 def init_state(self):
  assert not self.initialized;self.initialized=True;obs=self.initial_obs if self.initial_obs is not None else self.real.observation_manager.compute();s=self.pack();xi=self.context(obs);self.mdp=OriginalTaskMdp(xi.shape[-1],s);z=torch.zeros(self.num_envs,device=self.device);self.state=BridgeState(info={SUPERMIMIC_STATE_KEY:dict(s=s,xi=xi,f=self.ep_step.long(),a_prev=self.last_action.clone(),ep_step=self.ep_step.clone())},reward=z,terminated=z.bool(),truncated=z.bool(),obs=obs)
  # SDK layout evidence: actual projected gravity vs quaternion rotation.
  state=unflatten_state(s);gravity=self._t(self.real.scene['robot'].data.projected_gravity_b);err=float(((-state[1][:,2,:])-gravity).abs().max());assert err<1e-3,('SDK quaternion convention',err);self.quaternion_gravity_max_error=err;return self.state
 @property
 def supermimic_mdp(self):
  if not self.initialized:self.init_state()
  return self.mdp
 @torch.no_grad()
 def step(self,actions):
  old=self.state.info[SUPERMIMIC_STATE_KEY];self.pre=None;applied=actions.detach().clamp(-6.,6.);obs,reward,term,trunc,extra=self.real.step(applied);self.controls+=1;assert self.pre is not None,'Original pre-reset capture required';done=term.bool()|trunc.bool();assert torch.equal(done,self.pre['term']|self.pre['trunc']);s=self.pack();xi1=self.context(obs);xi1_masked=xi1.clone();xi1_masked[done]=0
  transition=dict(s=old['s'],s1=self.pre['s1'],a=applied.clone(),a_prev=old['a_prev'],xi=old['xi'],xi1=xi1_masked,xi1_valid=~done,r=reward.detach().clone(),f=old['f'],ep_step=old['ep_step'],done=done.clone(),term=self.pre['term'],trunc=self.pre['trunc']);self.ep_step=torch.where(done,0,self.ep_step+1).to(torch.int32);previous=applied.clone();previous[done]=0;self.last_action=previous
  self.state=BridgeState(info={SUPERMIMIC_STATE_KEY:dict(s=s,xi=xi1,f=self.ep_step.long(),a_prev=previous,ep_step=self.ep_step.clone()),SUPERMIMIC_TRANSITION_KEY:transition},reward=reward.detach(),terminated=term.bool(),truncated=trunc.bool(),obs=obs);return self.state
 def metrics(self):return dict(actual_controls=self.controls,real_environment_transitions=self.controls*self.num_envs,physics_callbacks=int(self.real._integrated_contact.tick)-self.physics_start,feedback_samples=int(self.real._feedback_100hz_tick)-self.feedback_start,actual_termination_events=self.metrics_terms,num_envs=self.num_envs,task_reward_unchanged=True,BPTT_is_worldmodel_not_differentiable_PhysX=True,original_skill_pass_rate='PENDING_INDEPENDENT_FROZEN_EVALUATION_NOT_TRAINING_LOSS')
 def state_dict(self):
  return dict(ep_step=self.ep_step.clone(),last_action=self.last_action.clone(),state=self.state,controls=self.controls,metrics=self.metrics(),context_layout=self.observed_context_layout,physical_root_q_dq=self.pack(),resume_environment_contract='New bounded episode with original fresh DR; persistent replay/learner RNG/optimizers restored separately, not bitwise PhysX contact warmstart',teacher=self.teacher.receipt())
 def export_supermimic_resume(self):
  def safe(x):
   if torch.is_tensor(x):return x.detach().cpu().clone()
   if isinstance(x,dict):return {str(k):safe(v)for k,v in x.items()}
   if isinstance(x,(list,tuple)):return [safe(v)for v in x]
   if x is None or isinstance(x,(str,bool,int,float)):return x
   return {'unserialized_type':type(x).__name__}
  components={}
  for name in('_mild_dr','_sensor_mild','_feedback_delay_mild','_spring_pressure','_gas_damping','_chassis_com','_explicit_pd'):
   obj=getattr(self.real,name,None);getter=getattr(obj,'state_dict',None)
   if callable(getter):components[name]=safe(getter())
  q=self.real._physics_action_delay.queue;components['physics_action_groups']=safe(q.groups)
  return dict(exact=False,environment_resume='Explicit original fresh episode; not bitwise PhysX/contact solver resume',physical_root_q_dq=safe(self.pack()),bridge_state={k:safe(v)for k,v in vars(self.state).items()},ep_step=safe(self.ep_step),last_action=safe(self.last_action),original_DR_queue_snapshot=components,controls=self.controls,context_layout=self.observed_context_layout,metrics=self.metrics())
 def close(self):self.real.termination_manager.compute=self._oldterm
