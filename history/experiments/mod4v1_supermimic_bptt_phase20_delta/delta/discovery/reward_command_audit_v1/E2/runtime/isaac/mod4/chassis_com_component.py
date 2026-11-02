"""Chassis-only body-link COM translation in meters; no simulation dependency."""
import torch
PROFILE='chassis_link_local_independent_xyz_5mm_v1'

class ChassisCOM:
    def __init__(self,num_envs,device,seed,enabled):
        if num_envs<=0:raise ValueError('Positive environment count required')
        self.num_envs=int(num_envs);self.device=torch.device(device);self.enabled=bool(enabled)
        self.delta_m=torch.zeros((num_envs,3),device=self.device)
        self.episode=torch.zeros(num_envs,dtype=torch.long,device=self.device)
        self.generators=[torch.Generator(device=self.device).manual_seed(int(seed)+190009+i*100003) for i in range(3)]
    def reset(self,ids):
        raw=torch.as_tensor(ids,device=self.device)
        if raw.dtype not in (torch.int32,torch.int64) or raw.ndim!=1:raise ValueError('Integer environment index vector required')
        ids=raw.long()
        if not len(ids):return
        if int(ids.min())<0 or int(ids.max())>=self.num_envs or len(torch.unique(ids))!=len(ids):raise ValueError('Invalid selected environment indices')
        self.episode[ids]+=1
        if self.enabled:
            for axis,g in enumerate(self.generators):
                self.delta_m[ids,axis]=torch.empty(len(ids),device=self.device).uniform_(-.005,.005,generator=g)
        else:self.delta_m[ids]=0
    def state_dict(self):
        return dict(version=1,profile=PROFILE,enabled=self.enabled,num_envs=self.num_envs,delta_m=self.delta_m.clone(),
                    episode=self.episode.clone(),private_xyz_RNG=[g.get_state().clone() for g in self.generators])
    def load_state_dict(self,state):
        if state['version']!=1 or state['profile']!=PROFILE or state['enabled']!=self.enabled or state['num_envs']!=self.num_envs:raise ValueError('COM state scope mismatch')
        delta=state['delta_m'].to(self.device);episode=state['episode'].to(self.device)
        if delta.shape!=(self.num_envs,3) or episode.shape!=(self.num_envs,) or episode.dtype!=torch.long:raise ValueError('COM state shape/type mismatch')
        if not bool(torch.isfinite(delta).all()) or bool((delta.abs()>.005001).any()) or bool((episode<0).any()):raise ValueError('Invalid COM state')
        if not self.enabled and bool((delta!=0).any()):raise ValueError('Disabled COM state must be zero')
        if len(state['private_xyz_RNG'])!=3:raise ValueError('Three private axis RNG states required')
        self.delta_m.copy_(delta);self.episode.copy_(episode)
        for g,s in zip(self.generators,state['private_xyz_RNG']):g.set_state(s.cpu())
