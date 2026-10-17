"""Frozen H1 actor9; only actual published per-environment public0/4 is accepted."""
from pathlib import Path
import hashlib, torch
from h1_frozen_mean35_exact_v1 import FrozenMean35
from h1_closed24_source_guard_v1 import EXPECTED,validate_H1_source
class Single35:
 def __init__(self,path,n,device):
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==EXPECTED and type(n) is int and n>0
  ck=torch.load(path,map_location='cpu',weights_only=False);validate_H1_source(ck)
  self.model=FrozenMean35(ck['actor_state_dict']).to(device).eval();self.model.requires_grad_(False)
  self.source={key:value.detach().cpu().clone() for key,value in ck['actor_state_dict'].items()}
  self.n=n;self.device=torch.device(device);self.last=torch.zeros(n,6,device=device);self.tick=-1;self.pending=None;self.calls=0;self.controls=0
 def begin(self,tick,provider,public_modes):
  assert type(tick) is int and tick>=0
  assert torch.is_tensor(public_modes) and public_modes.shape==(self.n,) and public_modes.dtype==torch.long and public_modes.device==self.device and ((public_modes==0)|(public_modes==4)).all()
  if self.pending is not None:
   assert self.tick==tick and torch.equal(self.pending['declared_actual_public_modes'],public_modes);return self.pending
  assert self.tick<0 or tick==self.tick+1
  x=provider();assert torch.is_tensor(x) and x.shape==(self.n,35) and x.dtype==torch.float32 and x.device==self.device and torch.isfinite(x).all()
  assert not x[:,:3].any() and torch.equal(x[:,22:28],self.last)
  assert torch.equal(x[:,28:35],torch.nn.functional.one_hot(public_modes,7).to(dtype=x.dtype))
  a=self.model(x);assert a.shape==(self.n,6) and torch.isfinite(a).all()
  self.pending=dict(shared_obs=x.detach().clone(),raw_action=a.detach().clone(),clipped_action=a.detach().clamp(-6,6),declared_actual_public_modes=public_modes.detach().clone());self.tick=tick;self.calls+=1;return self.pending
 def finish(self,actual,ended):
  assert self.pending is not None and torch.is_tensor(actual) and actual.shape==(self.n,6) and actual.dtype==torch.float32 and actual.device==self.device and torch.equal(actual,self.pending['clipped_action'])
  assert torch.is_tensor(ended) and ended.shape==(self.n,) and ended.dtype==torch.bool and ended.device==self.device
  self.last=actual.detach().clone();self.last[ended]=0;self.pending=None;self.controls+=1
 def exact(self):
  assert all(torch.equal(value.detach().cpu(),self.source[key]) for key,value in self.model.snapshot().items());return True
