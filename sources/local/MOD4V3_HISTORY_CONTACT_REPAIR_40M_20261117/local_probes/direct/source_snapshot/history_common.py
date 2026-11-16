"""Shared Isaac/MuJoCo history semantics and deployable deterministic actor."""
import torch
from torch import nn
H=12;OBS=35;LATENT=5
class HistoryQueue:
 def __init__(self,H=H):self.H=H;self.buffer=None
 def reset(self,obs):
  self.buffer=obs.unsqueeze(-2).repeat(*([1]*(obs.ndim-1)),self.H,1).clone();return self.buffer.flatten(-2)
 def append(self,obs,done=None):
  if self.buffer is None:return self.reset(obs)
  self.buffer=torch.cat((self.buffer[...,1:,:],obs.unsqueeze(-2)),-2)
  if done is not None and bool(done.any()):self.buffer[done]=obs[done,None,:].expand(-1,self.H,-1)
  return self.buffer.flatten(-2)
class HistoryEncoder(nn.Module):
 def __init__(self):
  super().__init__();self.register_buffer('mean',torch.zeros(OBS));self.register_buffer('scale',torch.ones(OBS));self.net=nn.Sequential(nn.Linear(H*OBS,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,LATENT))
 def forward(self,x):
  h=x.reshape(*x.shape[:-1],H,OBS);h=((h-self.mean)/self.scale).clamp(-10,10).flatten(-2);z=self.net(h)
  return torch.cat((z[...,:3],torch.sigmoid(z[...,3:])),dim=-1)
class LocalHistoryActor(nn.Module):
 def __init__(self):
  super().__init__();self.mlp=nn.Sequential(nn.Linear(OBS+LATENT,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6));self.encoder=HistoryEncoder()
 def forward(self,obs,history):return self.mlp(torch.cat((obs,self.encoder(history).detach()),-1))
 def load_checkpoint(self,data):
  source=data['actor_state_dict'];filtered={k:v for k,v in source.items()if k!='distribution.std_param'};self.load_state_dict(filtered,strict=True);return self
class StatefulLocalActor(nn.Module):
 def __init__(self,data):super().__init__();self.actor=LocalHistoryActor().load_checkpoint(data);self.queue=HistoryQueue();self.last=None
 def forward(self,obs):
  # Reset identity is supplied by replay hook; direct single-step evaluators explicitly reset.
  history=self.queue.append(obs);return self.actor(obs,history)
 def reset(self):self.queue=HistoryQueue();self.last=None

def warm_state(parent,encoder_state):
 state={k:v.clone()for k,v in parent['actor_state_dict'].items()};old=state['mlp.0.weight'];new=old.new_zeros(old.shape[0],OBS+LATENT);new[:,:OBS]=old;state['mlp.0.weight']=new;state.update({'encoder.'+k:v.clone()for k,v in encoder_state.items()});return state
