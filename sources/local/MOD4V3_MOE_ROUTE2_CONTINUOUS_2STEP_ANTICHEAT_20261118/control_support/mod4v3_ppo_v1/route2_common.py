"""Two independent experts, whole-episode mode routing and one continuous history queue."""
import torch
from torch import nn
H=12;OBS=35;LATENT=16
class HistoryQueue:
 def __init__(self):self.buffer=None
 def reset(self,obs):self.buffer=obs.unsqueeze(-2).repeat(*([1]*(obs.ndim-1)),H,1).clone();return self.buffer.flatten(-2)
 def append(self,obs,done=None):
  if self.buffer is None:return self.reset(obs)
  self.buffer=torch.cat((self.buffer[...,1:,:],obs.unsqueeze(-2)),-2)
  if done is not None and bool(done.any()):self.buffer[done]=obs[done,None,:].expand(-1,H,-1)
  return self.buffer.flatten(-2)
def action_mlp(n):return nn.Sequential(nn.Linear(n,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6))
class HistoryFeatures(nn.Module):
 def __init__(self):
  super().__init__();self.register_buffer('mean',torch.zeros(OBS));self.register_buffer('scale',torch.ones(OBS));self.net=nn.Sequential(nn.Linear(420,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,LATENT))
 def forward(self,h):
  h=((h.reshape(*h.shape[:-1],H,OBS)-self.mean)/self.scale).clamp(-10,10).flatten(-2);z=self.net(h);return torch.cat((z[...,:3],z[...,3:5].sigmoid(),z[...,5:]),-1)
class StairExpert(nn.Module):
 def __init__(self):super().__init__();self.encoder=HistoryFeatures();self.head=action_mlp(OBS+LATENT)
 def forward(self,x,h):return self.head(torch.cat((x,self.encoder(h)),-1))
class Route2Body(nn.Module):
 def __init__(self):super().__init__();self.e0=action_mlp(OBS);self.e0.requires_grad_(False);self.e1=StairExpert()
 def forward(self,inputs):
  x=inputs[...,:OBS];h=inputs[...,OBS:];route=x[...,29:30]>.5;normal_x=x.clone();normal_x[...,28:35]=normal_x.new_tensor([1,0,0,0,0,0,0]);a0=self.e0(normal_x);a1=self.e1(x,h);return torch.where(route,a1,a0)
class LocalStd(nn.Module):
 def __init__(self):super().__init__();self.e0_std=nn.Parameter(torch.ones(6),requires_grad=False);self.e1_log_std=nn.Parameter(torch.tensor([.25,.25,.25,.25,.4,.4]).log())
 def std(self,obs):return torch.where(obs[...,29:30]>.5,self.e1_log_std.exp().expand(*obs.shape[:-1],6),self.e0_std.expand(*obs.shape[:-1],6))
class LocalRoute2Actor(nn.Module):
 def __init__(self):super().__init__();self.mlp=Route2Body();self.distribution=LocalStd()
 def forward(self,obs,history):return self.mlp(torch.cat((obs,history),-1))
 def load_checkpoint(self,ck):self.load_state_dict(ck['actor_state_dict'],strict=True);return self
class StatefulRoute2Actor(LocalRoute2Actor):
 def __init__(self):super().__init__();self.queue=HistoryQueue()
 def reset_history(self):self.queue=HistoryQueue()
 def forward(self,obs):return super().forward(obs,self.queue.append(obs))
