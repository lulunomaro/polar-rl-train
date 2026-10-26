"""Approved first D6 subset: gas damping only, two independent episode factors.

Reuse exact tested factor math; use a distinct private RNG namespace and an
unambiguous parameter state. No PD/friction setters, SDK or launch authority.
"""
import torch
from spring_pressure_component import SpringPressure

PROFILE='gas_damping_independent_episode_090_110_v1'
class GasDamping:
    def __init__(self,n,device,seed,enabled=True):
        self.math=SpringPressure(n,device,int(seed)+170003,enabled)
        self.n=n;self.device=self.math.device;self.enabled=enabled
    @property
    def factor(self):return self.math.factor
    @property
    def episode(self):return self.math.episode
    @property
    def rng(self):return self.math.rng
    def reset(self,ids):self.math.reset(ids)
    def actual_damping_Ns_per_m(self):
        return self.math.actual_stiffness(torch.tensor([3.,3.],device=self.device))
    def state_dict(self):
        state=self.math.state_dict();state['physical_parameter']=PROFILE
        state['scope']='Gas damping3Ns/m times independent episode.9-1.1; separate from PD derivative and joint friction; engineering only'
        return state
    def load_state_dict(self,state):
        if state.get('physical_parameter')!=PROFILE:raise ValueError('D6 damping parameter scope differs; cannot load D5 stiffness state')
        self.math.load_state_dict(state)
