"""One observation/history policy with two frozen complete experts and a differentiable learned router.
The gate receives policy history only. No world positions, teacher calls, contact sensors,
FSM state, or playback clocks are read by this actor.
"""
import torch
from torch import nn
class ContactBody(nn.Module):
 def __init__(self):
  super().__init__();self.normal=nn.Sequential(nn.Linear(35,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6));self.normal.requires_grad_(False)
  self.skill=nn.Sequential(nn.Linear(40,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,6));self.skill.requires_grad_(False)
  self.gate=nn.Sequential(nn.Linear(420,128),nn.ELU(),nn.Linear(128,32),nn.ELU(),nn.Linear(32,1));nn.init.zeros_(self.gate[-1].weight);nn.init.constant_(self.gate[-1].bias,-6.)
  self.register_buffer('history_mean',torch.zeros(35));self.register_buffer('history_scale',torch.ones(35))
 def gate_logit(self,history):
  h=history.reshape(*history.shape[:-1],12,35);return self.gate(((h-self.history_mean)/self.history_scale).clamp(-10,10).flatten(-2))
 def forward(self,inputs):
  x=inputs[...,:35];z=inputs[...,35:40];history=inputs[...,40:];normal_x=x.clone();normal_x[...,28:35]=normal_x.new_tensor([1,0,0,0,0,0,0])
  normal=self.normal(normal_x);skill=self.skill(torch.cat((x,z),-1));g=torch.sigmoid(self.gate_logit(history))*x[...,29:30].clamp(0,1)
  self.last_gate=g.detach()
  return normal+g*(skill-normal)
