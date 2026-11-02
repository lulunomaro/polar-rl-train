"""Isolated S1A CPU component; not an Isaac observation adapter or training entry."""
from __future__ import annotations
from copy import deepcopy
import torch
from torch import nn

class FeedbackHistory:
    """Five oldest-to-current deployable35 frames; selected resets never mix episodes."""
    def __init__(self,num_envs,*,device='cpu',dtype=torch.float32):
        if num_envs<=0:raise ValueError('Positive environment count required')
        self.frames=torch.zeros(num_envs,5,35,device=device,dtype=dtype)
        self.pending=torch.ones(num_envs,device=device,dtype=torch.bool)
        self.last_tick=None
        self.advances=0

    def reset_rows(self,ids):
        ids=torch.as_tensor(ids,device=self.frames.device,dtype=torch.long)
        if ids.ndim!=1 or torch.any(ids<0) or torch.any(ids>=self.frames.shape[0]):
            raise ValueError('Invalid selected reset rows')
        self.pending[ids]=True

    def observe(self,current35,tick):
        if current35.shape!=(self.frames.shape[0],35) or current35.dtype!=self.frames.dtype or current35.device!=self.frames.device:
            raise ValueError('History only accepts matching deployable35 feedback')
        if not torch.isfinite(current35).all():raise ValueError('Nonfinite actual feedback')
        if not isinstance(tick,int) or isinstance(tick,bool) or tick<0:
            raise ValueError('Integer common control tick required')
        if self.last_tick is not None and tick not in (self.last_tick,self.last_tick+1):
            raise ValueError('Backward or missing control frame')
        new_tick=self.last_tick is None or tick!=self.last_tick
        if new_tick:
            retained=~self.pending
            self.frames[retained,:-1]=self.frames[retained,1:].clone()
            self.frames[retained,-1]=current35[retained]
            self.advances+=1
        if torch.any(self.pending):
            self.frames[self.pending]=current35[self.pending,None,:].expand(-1,5,-1)
            self.pending.zero_()
        self.last_tick=tick
        # Returned buffers cannot mutate the retained episode state.
        return self.frames.flatten(1).clone()

class VelocityEncoder(nn.Module):
    """175->128->64->3 body-velocity candidate, built with an independent CPU RNG."""
    def __init__(self,seed=20261007):
        super().__init__()
        with torch.random.fork_rng(devices=[]):
            torch.random.default_generator.manual_seed(seed)
            self.net=nn.Sequential(nn.Linear(175,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,3))
    def forward(self,history175):
        if history175.ndim!=2 or history175.shape[1]!=175:raise ValueError('Five35 frames required')
        return self.net(history175)

def actor_input(current35,history175,encoder,variant):
    if current35.ndim!=2 or current35.shape[1]!=35 or history175.shape!=(current35.shape[0],175):
        raise ValueError('Only current feedback and matching deployable history accepted')
    if variant not in ('A1','A2'):raise ValueError('Explicit A1/A2 required')
    latent=encoder(history175)
    return torch.cat((current35,latent.detach() if variant=='A1' else latent),dim=1)

def supervised_velocity_loss(history175,encoder,body_velocity_m_s):
    # SDK must independently read the actual body frame and COM/link point.
    # This function deliberately has no critic-observation slice convention.
    if body_velocity_m_s.shape!=(history175.shape[0],3) or not torch.isfinite(body_velocity_m_s).all():
        raise ValueError('Actual finite Body velocity3 label required')
    return torch.nn.functional.mse_loss(encoder(history175),body_velocity_m_s.detach())

def expand_actor_state(state):
    """Actual rsl5 actor dictionary: preserve all old columns, std and remaining weights."""
    if 'mlp.0.weight' not in state or state['mlp.0.weight'].shape!=(256,35):
        raise ValueError('Expected actual23509 actor first layer256x35')
    if 'distribution.std_param' not in state or state['distribution.std_param'].shape!=(6,):
        raise ValueError('Actual six-dimensional source std required')
    if any(not torch.isfinite(x).all() for x in state.values()):raise ValueError('Nonfinite source actor')
    out=deepcopy(state);w=state['mlp.0.weight']
    out['mlp.0.weight']=torch.cat((w,torch.zeros(256,3,device=w.device,dtype=w.dtype)),dim=1)
    return out
