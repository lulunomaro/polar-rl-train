"""Declared external rescue request and capped upright progress; no action or mode oracle."""
import torch
class RecoveryPhase:
 def __init__(self,n,device):
  self.n=n;self.device=device;self.age=torch.zeros(n,dtype=torch.long,device=device);self.recipe=torch.arange(n,device=device,dtype=torch.long)%13;self.peak=torch.zeros(n,device=device);self.delta=torch.zeros(n,device=device);self.stable=torch.zeros(n,dtype=torch.long,device=device);self.credited=torch.zeros(n,dtype=torch.bool,device=device);self.request=torch.zeros(n,dtype=torch.bool,device=device)
 def mode(self):return torch.where((self.recipe!=12)&(self.age<300),3,0).long()
 def begin(self):self.request.copy_((self.recipe!=12)&(self.age<300));self.delta.zero_()
 def update(self,gravity_z,root_speed,angular_speed):
  upright=((1-gravity_z)/2).clamp(0,1);now=torch.where(self.request,torch.maximum(self.peak,upright),self.peak);self.delta.copy_(now-self.peak);self.peak.copy_(now)
  good=(gravity_z<-0.984807753)&(root_speed<.03)&(angular_speed<.2)&self.request;self.stable.copy_(torch.where(good,self.stable+1,0));event=(self.stable>=50)&~self.credited;self.delta.add_(event.float());self.credited|=event;self.age+=1
 def reset(self,ids,initial_upright=None):
  for v in (self.age,self.peak,self.delta,self.stable,self.credited,self.request):v[ids]=0
  if initial_upright is not None:self.peak[ids]=initial_upright
 def state_dict(self):return dict(version=1,tensors={k:getattr(self,k).clone() for k in ('age','recipe','peak','delta','stable','credited','request')})
 def load_state_dict(self,s):
  assert s['version']==1 and set(s['tensors'])=={'age','recipe','peak','delta','stable','credited','request'}
  for k,v in s['tensors'].items():
   a=getattr(self,k);assert a.shape==v.shape and a.dtype==v.dtype and (not v.is_floating_point() or torch.isfinite(v).all());a.copy_(v.to(a.device))
  assert (self.age>=0).all() and ((self.recipe>=0)&(self.recipe<=12)).all() and ((self.peak>=0)&(self.peak<=1)).all()
