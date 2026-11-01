"""Separate D7 explicit motor PD coefficient pressure, never implicit joint damping."""
import torch
PROFILE='explicit_motor_PD_independent_095_105_v1'
class ExplicitPD:
    def __init__(self,num_envs,device,seed,enabled):
        if num_envs<=0:raise ValueError('Positive environment count required')
        self.num_envs=int(num_envs);self.device=torch.device(device);self.enabled=bool(enabled)
        self.factor={name:torch.ones((num_envs,width),device=self.device) for name,width in (('leg_kp',4),('leg_kd',4),('wheel_kd',2))}
        self.episode=torch.zeros(num_envs,dtype=torch.long,device=self.device)
        self.generators={name:torch.Generator(device=self.device).manual_seed(int(seed)+230003+i*100003) for i,name in enumerate(self.factor)}
    def reset(self,ids):
        ids=torch.as_tensor(ids,device=self.device)
        if ids.dtype not in (torch.int32,torch.int64) or ids.ndim!=1:raise ValueError('Integer index vector required')
        ids=ids.long()
        if not len(ids):return
        if int(ids.min())<0 or int(ids.max())>=self.num_envs or len(torch.unique(ids))!=len(ids):raise ValueError('Invalid selected indices')
        self.episode[ids]+=1
        for name,value in self.factor.items():
            value[ids]=torch.empty_like(value[ids]).uniform_(.95,1.05,generator=self.generators[name]) if self.enabled else 1.
    def coefficients(self):
        return dict(leg_kp=60.*self.factor['leg_kp'],leg_kd=2.*self.factor['leg_kd'],wheel_kd=.6*self.factor['wheel_kd'])
    def state_dict(self):
        return dict(version=1,profile=PROFILE,num_envs=self.num_envs,enabled=self.enabled,
                    factor={k:v.clone() for k,v in self.factor.items()},episode=self.episode.clone(),
                    private_group_RNG={k:g.get_state().clone() for k,g in self.generators.items()})
    def load_state_dict(self,state):
        if state['version']!=1 or state['profile']!=PROFILE or state['num_envs']!=self.num_envs or state['enabled']!=self.enabled:raise ValueError('PD state scope mismatch')
        if state['factor'].keys()!=self.factor.keys() or state['private_group_RNG'].keys()!=self.generators.keys():raise ValueError('PD state groups mismatch')
        values={k:v.to(self.device) for k,v in state['factor'].items()};episodes=state['episode'].to(self.device)
        if episodes.shape!=(self.num_envs,) or episodes.dtype!=torch.long or bool((episodes<0).any()):raise ValueError('PD episode state invalid')
        for k,v in values.items():
            if v.shape!=self.factor[k].shape or not bool(torch.isfinite(v).all()) or bool(((v<.949999)|(v>1.050001)).any()):raise ValueError('PD factor invalid')
            if not self.enabled and bool((v!=1).any()):raise ValueError('Disabled PD factor must be1')
        for k,v in values.items():self.factor[k].copy_(v)
        self.episode.copy_(episodes)
        for k,g in self.generators.items():g.set_state(state['private_group_RNG'][k].cpu())
