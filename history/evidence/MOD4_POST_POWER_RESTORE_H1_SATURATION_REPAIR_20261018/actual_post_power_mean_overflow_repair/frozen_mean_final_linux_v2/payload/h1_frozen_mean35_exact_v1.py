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
