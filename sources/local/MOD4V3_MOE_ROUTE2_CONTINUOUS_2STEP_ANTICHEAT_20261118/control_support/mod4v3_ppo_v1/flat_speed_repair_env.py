"""Flat-speed recovery from the selected Rough-v1 actor; original full DR."""
import os,torch
from .scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
from .scut_flat_env import configuration,tensor
from .scut_flat_rewards import make_reward_class
from .scut_rough_scut_v1_env import configuration_scut_v1

class FlatSpeedRepairEnv(ScutFlatMixedRemainingDREnv):
    enforce_closure_reset=True
    def __init__(self,cfg,meta,bank):
        self._speed_ready=False
        self.leg_pd_decimation=int(os.environ['FLAT_SPEED_LEG_PD_DECIMATION'])
        self.wheel_pd_decimation=int(os.environ['FLAT_SPEED_WHEEL_PD_DECIMATION'])
        super().__init__(cfg,meta,bank)
        self.command_vx=(-2.2,2.2);self.height_range=(.20,.42)
        self._speed_ready=True
    def _make_reward(self,meta):
        return make_reward_class(meta,cfg_factory=configuration_scut_v1)(self.view,self.num_envs,self.device)
    def _sample_command(self,ids):
        super()._sample_command(ids)
        if not self._speed_ready:return
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten();n=len(ids)
        draw=torch.rand(n,device=self.device);straight=draw<.5;stop=(draw>=.5)&(draw<.7)
        velocity=torch.empty(n,device=self.device).uniform_(-2.2,2.2)
        fast=torch.rand(n,device=self.device)<.4
        sign=torch.where(torch.rand(n,device=self.device)<.5,-1.,1.)
        velocity[fast]=torch.empty(n,device=self.device).uniform_(2.,2.2)[fast]*sign[fast]
        chosen=ids[straight|stop];self.command[ids[straight],0]=velocity[straight]
        self.command[chosen,1:]=0.;self.command[ids[stop]]=0.;self.heading_env[chosen]=False;self.standing_env[ids[straight]]=False;self.standing_env[ids[stop]]=True
    def physical_delay_summary(self):
        d=super().physical_delay_summary();d.update(pd_dt_ms=self.leg_pd_decimation*float(self.cfg.sim.dt)*1000,wheel_pd_dt_ms=self.wheel_pd_decimation*float(self.cfg.sim.dt)*1000,profile='flat_speed_repair_controller_recipe')
        return d
