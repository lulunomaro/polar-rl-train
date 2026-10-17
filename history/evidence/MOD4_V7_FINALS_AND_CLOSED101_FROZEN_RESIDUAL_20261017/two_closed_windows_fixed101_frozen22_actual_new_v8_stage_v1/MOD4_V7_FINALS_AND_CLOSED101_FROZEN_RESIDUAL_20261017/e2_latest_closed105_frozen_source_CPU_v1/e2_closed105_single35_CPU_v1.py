"""Frozen E2 closed109: one normal35 tick, actor9 only, whole6 clip and selected reset."""
from pathlib import Path
import hashlib,torch
from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35
from e2_closed105_source_guard_CPU_v1 import validate_E2_source
EXPECTED='ef60ea74af483a281e7cbba436dbcd912b7568f86c4310865c1100e0e42b6b41'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Single35:
 def __init__(self,path,n,device):
  assert sha(path)==EXPECTED and isinstance(n,int) and n>0
  source=torch.load(path,map_location='cpu',weights_only=False)
  assert source.get('history_architecture',{}).get('variant','A0')=='A0';validate_E2_source(source)
  self.model=FrozenMean35(source['actor_state_dict']).to(device).eval();self.model.requires_grad_(False)
  self.source={k:v.detach().cpu().clone() for k,v in source['actor_state_dict'].items()};assert len(self.source)==9
  self.n=n;self.device=torch.device(device);self.last=torch.zeros(n,6,device=device);self.tick=-1;self.pending=None;self.calls=0;self.controls=0
 def begin(self,tick,provider):
  if self.pending is not None:assert self.tick==tick;return self.pending
  assert self.tick<0 or tick==self.tick+1
  x=provider();assert x.shape==(self.n,35) and x.dtype==torch.float32 and x.device==self.device and torch.isfinite(x).all()
  assert torch.equal(x[:,22:28],self.last)
  normal=torch.zeros_like(x[:,28:35]);normal[:,0]=1;assert torch.equal(x[:,28:35],normal)
  a=self.model(x);assert a.shape==(self.n,6) and torch.isfinite(a).all()
  self.pending=dict(shared_obs=x.detach().clone(),raw_action=a.detach().clone(),clipped_action=a.detach().clamp(-6,6));self.tick=tick;self.calls+=1
  return self.pending
 def finish(self,actual,ended):
  assert self.pending is not None and actual.shape==(self.n,6) and ended.shape==(self.n,) and ended.dtype==torch.bool
  assert torch.equal(actual,self.pending['clipped_action'])
  self.last=actual.detach().clone();self.last[ended]=0;self.pending=None;self.controls+=1
 def exact(self):
  assert all(torch.equal(v.detach().cpu(),self.source[k]) for k,v in self.model.snapshot().items())
  return True
