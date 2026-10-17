"""Frozen source85 actor9 only; caller supplies the actual declared public mode0 or3."""
from pathlib import Path
import hashlib,torch
from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35
from recovery_closed85_source_guard_v1 import validate_E3_source
EXPECTED='8043c7fbcd8abf2690672aa956fcfae0c17c24172fc6baaef0e75e5e44a1c208'
class Single35:
 def __init__(self,path,n,device):
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==EXPECTED and isinstance(n,int) and n>0
  ck=torch.load(path,map_location='cpu',weights_only=False);validate_E3_source(ck)
  self.model=FrozenMean35(ck['actor_state_dict']).to(device).eval();self.model.requires_grad_(False);self.source={k:v.detach().cpu().clone() for k,v in ck['actor_state_dict'].items()};self.n=n;self.device=torch.device(device);self.last=torch.zeros(n,6,device=device);self.tick=-1;self.pending=None;self.calls=0;self.controls=0
 def begin(self,tick,provider,public_mode):
  if self.pending is not None:assert self.tick==tick;return self.pending
  assert self.tick<0 or tick==self.tick+1
  x=provider();assert x.shape==(self.n,35) and x.dtype==torch.float32 and x.device==self.device and torch.isfinite(x).all() and torch.equal(x[:,22:28],self.last)
  assert isinstance(public_mode,int) and public_mode in (0,3);mode=torch.zeros_like(x[:,28:35]);mode[:,public_mode]=1;assert torch.equal(x[:,28:35],mode)
  a=self.model(x);assert a.shape==(self.n,6) and torch.isfinite(a).all();self.pending=dict(shared_obs=x.detach().clone(),raw_action=a.detach().clone(),clipped_action=a.detach().clamp(-6,6),declared_actual_public_mode=public_mode);self.tick=tick;self.calls+=1;return self.pending
 def finish(self,actual,ended):
  assert self.pending is not None and actual.shape==(self.n,6) and ended.shape==(self.n,) and ended.dtype==torch.bool and torch.equal(actual,self.pending['clipped_action'])
  self.last=actual.detach().clone();self.last[ended]=0;self.pending=None;self.controls+=1
 def exact(self):
  assert all(torch.equal(v.detach().cpu(),self.source[k]) for k,v in self.model.snapshot().items());return True
