"""S4 CPU interface prototype, not a GPU policy or trained gate.

One normal35 observation is shared by frozen expert means and the gate.
Hard routing chooses one entire six-action vector. No oracle input or blend.
"""
import torch
from torch import nn
from torch.nn import functional as F

class FrozenMean35(nn.Module):
 def __init__(self, state):
  super().__init__()
  expected=['distribution.std_param']+[f'mlp.{i}.{s}' for i in (0,2,4,6) for s in ('weight','bias')]
  assert set(state)==set(expected)
  widths=(35,256,128,64,6)
  self.keys=expected
  for i,k in enumerate(expected):
   v=state[k];assert v.device.type=='cpu' and v.dtype==torch.float32 and torch.isfinite(v).all()
   self.register_buffer('frozen_'+str(i),v.detach().clone())
  for i,(src,dst) in zip((0,2,4,6),zip(widths,widths[1:])):
   assert state[f'mlp.{i}.weight'].shape==(dst,src) and state[f'mlp.{i}.bias'].shape==(dst,)
  self.eval()
 def snapshot(self):return {k:getattr(self,'frozen_'+str(i)).clone() for i,k in enumerate(self.keys)}
 def forward(self,obs):
  assert obs.ndim==2 and obs.shape[1]==35 and obs.dtype==torch.float32 and torch.isfinite(obs).all()
  values={k:getattr(self,'frozen_'+str(i)) for i,k in enumerate(self.keys)}
  x=obs
  with torch.no_grad():
   for i in (0,2,4,6):
    x=F.linear(x,values[f'mlp.{i}.weight'],values[f'mlp.{i}.bias'])
    if i!=6:x=F.elu(x)
  assert x.shape==(len(obs),6) and torch.isfinite(x).all()
  return x

class Gate35CPU(nn.Module):
 """Deterministic untrained35→64→32→K fixture, no random initialization draws."""
 def __init__(self,experts=2):
  super().__init__();assert experts==2
  for name,shape in [('w1',(64,35)),('b1',(64,)),('w2',(32,64)),('b2',(32,)),('w3',(experts,32)),('b3',(experts,))]:
   n=1
   for size in shape:n*=size
   value=torch.sin(torch.arange(n,dtype=torch.float32)).reshape(shape)*.01 if name.startswith('w') else torch.zeros(shape)
   self.register_parameter(name,nn.Parameter(value))
 def forward(self,obs):
  assert obs.ndim==2 and obs.shape[1]==35 and torch.isfinite(obs).all()
  return F.linear(F.elu(F.linear(F.elu(F.linear(obs,self.w1,self.b1)),self.w2,self.b2)),self.w3,self.b3)

def choose_whole_action(expert_raw,logits,eligible,previous=None,hysteresis=0.):
 assert expert_raw.ndim==3 and expert_raw.shape[1:]==(2,6)
 assert logits.shape==expert_raw.shape[:2] and eligible.shape==logits.shape and eligible.dtype==torch.bool
 assert torch.isfinite(expert_raw).all() and torch.isfinite(logits).all() and eligible.any(-1).all()
 assert isinstance(hysteresis,(float,int)) and hysteresis>=0
 scores=logits.masked_fill(~eligible,float('-inf'));choice=scores.argmax(-1)
 if previous is not None:
  assert previous.shape==choice.shape and previous.dtype==torch.int64 and ((previous>=0)&(previous<2)).all()
  rows=torch.arange(len(choice));can_keep=eligible[rows,previous] & ((scores[rows,choice]-scores[rows,previous])<=hysteresis)
  choice=torch.where(can_keep,previous,choice)
 selected=expert_raw[torch.arange(len(choice)),choice]
 assert torch.equal(selected,expert_raw[torch.arange(len(choice)),choice])
 return selected,choice,selected.clamp(-6.,6.)
