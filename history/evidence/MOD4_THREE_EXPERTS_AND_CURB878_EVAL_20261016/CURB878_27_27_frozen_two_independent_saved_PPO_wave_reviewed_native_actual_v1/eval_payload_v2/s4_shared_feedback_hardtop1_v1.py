"""Source-bound pair router. Training saves z and raw a, not a blended Gaussian.

The original35 observation uses last processed control action at22:28 and
constant normal mode at28:35. Motor delay/torque history remains in the plant.
"""
from pathlib import Path
import copy, hashlib, math, sys
import torch
from torch import nn
from torch.nn import functional as F
W=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014'))
from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35,Gate35CPU
EXPERT_IDS=('E0','E1_WAVE35')
SHA=('b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8','b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clone_tree(x):
 if torch.is_tensor(x):return x.detach().clone()
 if isinstance(x,dict):return {k:clone_tree(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return type(x)(clone_tree(v) for v in x)
 return copy.deepcopy(x)
class Critic38(nn.Module):
 def __init__(self,state):
  super().__init__();self.keys=[f'mlp.{i}.{k}' for i in (0,2,4,6) for k in ('weight','bias')];assert set(state)==set(self.keys)
  for j,key in enumerate(self.keys):self.register_parameter('p'+str(j),nn.Parameter(state[key].detach().clone()))
  for i,(a,b) in zip((0,2,4,6),zip((38,256,128,64),(256,128,64,1))):assert state[f'mlp.{i}.weight'].shape==(b,a) and state[f'mlp.{i}.bias'].shape==(b,)
 def forward(self,x):
  assert x.ndim==2 and x.shape[1]==38 and torch.isfinite(x).all()
  for j in range(0,8,2):
   x=F.linear(x,getattr(self,'p'+str(j)),getattr(self,'p'+str(j+1)))
   if j!=6:x=F.elu(x)
  return x
class PairRouter:
 def __init__(self,refs,n,device='cpu'):
  assert isinstance(n,int) and n>0 and [x['expert'] for x in refs]==list(EXPERT_IDS)
  self.refs=copy.deepcopy(refs);self.n=n;self.device=torch.device(device);self.experts=[];source=[]
  for row,digest in zip(refs,SHA):
   assert row['sha256']==digest and sha(row['local_path'])==digest
   ck=torch.load(row['local_path'],map_location='cpu',weights_only=False);assert ck.get('history_architecture',{}).get('variant','A0')=='A0'
   source.append(ck);self.experts.append(FrozenMean35(ck['actor_state_dict']).to(self.device))
  self.std=torch.stack([s['actor_state_dict']['distribution.std_param'] for s in source]).detach().clone().to(self.device)
  assert self.std.shape==(2,6) and torch.isfinite(self.std).all() and (self.std>0).all()
  self.gate=Gate35CPU().to(self.device);self.critic=Critic38(source[0]['critic_state_dict']).to(self.device)
  self.optimizer=torch.optim.Adam(list(self.gate.parameters())+list(self.critic.parameters()),lr=1e-4)
  self.last_action=torch.zeros(n,6,device=self.device);self.previous=torch.full((n,),-1,dtype=torch.int64,device=self.device)
  self.last_switch=torch.full((n,),-1000000,dtype=torch.int64,device=self.device)
  self.last_tick=-1;self.pending=None;self.observation_calls=0;self.completed_controls=0;self.switch_count=0
 def _valid_view(self,obs):
  assert obs.shape==(self.n,35) and obs.dtype==torch.float32 and obs.device==self.device and torch.isfinite(obs).all()
  assert torch.equal(obs[:,22:28],self.last_action),'Not the original previous executed clipped control action'
  expected=torch.zeros_like(obs[:,28:35]);expected[:,0]=1
  assert torch.equal(obs[:,28:35],expected),'First pair cannot infer from hidden terrain/task mode bits'
 def distributions(self,obs):
  self._valid_view(obs);means=torch.stack([e(obs) for e in self.experts],1);logits=self.gate(obs)
  assert means.shape==(self.n,2,6) and logits.shape==(self.n,2) and torch.isfinite(logits).all()
  return means,logits
 def joint_log_prob(self,obs,z,raw):
  means,logits=self.distributions(obs);assert z.shape==(self.n,) and z.dtype==torch.int64 and ((z>=0)&(z<2)).all()
  assert raw.shape==(self.n,6) and torch.isfinite(raw).all()
  rows=torch.arange(self.n,device=self.device);m=means[rows,z];s=self.std[z]
  gaussian=(-.5*((raw-m)/s).square()-s.log()-.5*math.log(2*math.pi)).sum(-1)
  return logits.log_softmax(-1)[rows,z]+gaussian
 def latent_joint_entropy(self,obs):
  _,logits=self.distributions(obs);logp=logits.log_softmax(-1);p=logp.exp()
  conditional=(self.std.log()+.5*math.log(2*math.pi*math.e)).sum(-1)
  return -(p*logp).sum(-1)+(p*conditional).sum(-1)
 @staticmethod
 def frozen_expert_joint_KL(old_logits,new_logits):
  assert old_logits.shape==new_logits.shape and torch.isfinite(old_logits).all() and torch.isfinite(new_logits).all()
  old=old_logits.log_softmax(-1);new=new_logits.log_softmax(-1)
  return (old.exp()*(old-new)).sum(-1)
 def decide(self,tick,provider,mode='gate_eval',generator=None,dwell_ticks=0,advantage=0.):
  assert isinstance(tick,int) and tick>=0 and mode in ('gate_eval','rule_eval','train_joint')
  if self.pending is not None:
   assert tick==self.last_tick,'Previous physical control is not committed'
   assert self.pending['configuration']==(mode,dwell_ticks,float(advantage)),'Routing mode/configuration changed inside a physical control'
   return clone_tree(self.pending)
  assert self.last_tick<0 or tick==self.last_tick+1,'Duplicate, skipped or stale decision tick'
  assert isinstance(dwell_ticks,int) and dwell_ticks>=0 and 0<=advantage<=1
  if mode=='train_joint':assert generator is not None and dwell_ticks==0 and advantage==0,'Stateful deterministic hysteresis is not the categorical training distribution'
  obs=provider();self._valid_view(obs);self.observation_calls+=1
  means,logits=self.distributions(obs);p=logits.softmax(-1);rows=torch.arange(self.n,device=self.device)
  if mode=='rule_eval':
   low_linear=(obs[:,0].abs()>0)&(obs[:,0].abs()<=.300001)&(obs[:,1:3].abs().amax(-1)<=1e-6)
   p=torch.stack((~low_linear,low_linear),-1).to(torch.float32);choice=low_linear.long()
  elif mode=='train_joint':choice=torch.multinomial(p,1,generator=generator).squeeze(-1)
  else:choice=p.argmax(-1)
  if mode!='train_joint' and (dwell_ticks or advantage):
   previous=self.previous.clamp_min(0);delta=p[rows,choice]-p[rows,previous]
   keep=(self.previous>=0)&((tick-self.last_switch<dwell_ticks)|(delta<=advantage));choice=torch.where(keep,previous,choice)
  if mode=='train_joint':
   noise=torch.randn((self.n,6),device=self.device,dtype=torch.float32,generator=generator);raw=means[rows,choice]+self.std[choice]*noise
   logprob=self.joint_log_prob(obs,choice,raw)
  else:raw=means[rows,choice];logprob=None
  clipped=raw.clamp(-6,6);self.last_tick=tick
  self.pending=dict(tick=tick,mode=mode,configuration=(mode,dwell_ticks,float(advantage)),shared_obs=obs.detach().clone(),expert_means=means.detach().clone(),logits=logits.detach().clone(),probabilities=p.detach().clone(),z=choice.detach().clone(),raw_action=raw.detach().clone(),clipped_action=clipped.detach().clone(),joint_log_prob=logprob.detach().clone() if logprob is not None else None)
  return clone_tree(self.pending)
 def finish(self,tick,actual_action_manager_before_reset,ended):
  assert self.pending is not None and tick==self.last_tick
  assert ended.shape==(self.n,) and ended.dtype==torch.bool
  assert torch.equal(actual_action_manager_before_reset,self.pending['clipped_action']),'Actual vector wrapper action differs from routed whole action'
  choice=self.pending['z'];changed=(self.previous>=0)&(choice!=self.previous);self.switch_count+=int(changed.sum())
  self.last_switch=torch.where((self.previous<0)|changed,torch.full_like(self.last_switch,tick),self.last_switch)
  self.previous=choice.clone();self.last_action=actual_action_manager_before_reset.detach().clone()
  self.last_action[ended]=0;self.previous[ended]=-1;self.last_switch[ended]=-1000000
  self.pending=None;self.completed_controls+=1
 def fullsave(self,generator):
  assert self.pending is None,'Only complete physical controls may be checkpointed'
  return clone_tree(dict(version=1,architecture='S4_35view_two_frozen_experts_hardtop1_scalarGaussian_v1',expert_refs=self.refs,expert_actor_snapshots=[e.snapshot() for e in self.experts],expert_std=self.std,gate=self.gate.state_dict(),critic=self.critic.state_dict(),new_gate_and_critic_optimizer=self.optimizer.state_dict(),private_generator=generator.get_state(),last_action=self.last_action,previous=self.previous,last_switch=self.last_switch,last_tick=self.last_tick,observation_calls=self.observation_calls,completed_controls=self.completed_controls,switch_count=self.switch_count,trained_gate=False,CPU_contract_only=True,environment_DR_and_global_named_private_CPUCUDA_fullsave_pending=True))
 def restore(self,s,generator):
  assert self.pending is None and s['version']==1 and s['architecture']=='S4_35view_two_frozen_experts_hardtop1_scalarGaussian_v1'
  assert s['expert_refs']==self.refs and torch.equal(s['expert_std'].to(self.device),self.std)
  assert len(s['expert_actor_snapshots'])==2
  for e,snapshot in zip(self.experts,s['expert_actor_snapshots']):
   assert set(snapshot)==set(e.snapshot()) and all(torch.equal(v.to(self.device),e.snapshot()[k]) for k,v in snapshot.items())
  assert s['last_action'].shape==(self.n,6) and torch.isfinite(s['last_action']).all() and (s['last_action'].abs()<=6).all()
  assert s['previous'].shape==s['last_switch'].shape==(self.n,) and s['previous'].dtype==s['last_switch'].dtype==torch.int64
  assert ((s['previous']>=-1)&(s['previous']<2)).all() and isinstance(s['last_tick'],int) and s['last_tick']>=-1
  assert (s['last_switch']<=s['last_tick']).all() and all(isinstance(s[k],int) and s[k]>=0 for k in ('observation_calls','completed_controls','switch_count'))
  self.gate.load_state_dict(s['gate'],strict=True);self.critic.load_state_dict(s['critic'],strict=True);self.optimizer.load_state_dict(s['new_gate_and_critic_optimizer']);generator.set_state(s['private_generator'])
  for key in ('last_action','previous','last_switch'):setattr(self,key,s[key].to(self.device).clone())
  assert self.last_action.shape==(self.n,6) and self.previous.shape==self.last_switch.shape==(self.n,)
  for key in ('last_tick','observation_calls','completed_controls','switch_count'):setattr(self,key,s[key])
