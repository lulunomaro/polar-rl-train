"""50Hz measured-input boundary. The separately pinned JUMP methods are unchanged."""
import copy
import torch
from literal_original_methods import LiteralOriginalFudanRewardMethods
from literal_original_config import LiteralOriginalConfig, class_to_dict

class LiteralJump194(LiteralOriginalFudanRewardMethods):
    def __init__(self,n,device,dt,body_names):
        assert dt == .02 and len(body_names)==31 and len(set(body_names))==31
        self.num_envs=n; self.device=device; self.dt=dt
        self.cfg=LiteralOriginalConfig()
        self.reward_scales=copy.deepcopy(class_to_dict(self.cfg.rewards.scales))
        self.feet_indices=torch.tensor([body_names.index(x) for x in ('left_wheel','right_wheel')],device=device)
        self.penalised_contact_indices=torch.tensor([i for i,x in enumerate(body_names) if x not in ('left_wheel','right_wheel')],device=device)
        self.rew_buf=torch.zeros(n,device=device)
        self.base_air_time=torch.zeros(n,device=device)
        self.last_contacts=torch.zeros(n,2,device=device,dtype=torch.bool)
        self.contact_filt=torch.zeros_like(self.last_contacts)
        self.was_in_flight=torch.zeros(n,device=device,dtype=torch.bool)
        self._prepare_reward_function()
        assert len(self.reward_names)==16 and self.cfg.rewards.clip_single_reward==2.5
        self.calls=0; self.last_tick=None

    def measured_step(self,frame,tick):
        if self.last_tick is not None and tick!=self.last_tick+1:raise RuntimeError('Duplicate or gapped reward clock')
        shapes=dict(commands=(self.num_envs,4),root_states=(self.num_envs,13),base_lin_vel=(self.num_envs,3),
            base_ang_vel=(self.num_envs,3),projected_gravity=(self.num_envs,3),L0=(self.num_envs,2),theta0=(self.num_envs,2),
            torques=(self.num_envs,6),actions=(self.num_envs,6),last_actions=(self.num_envs,6,2),contact_forces=(self.num_envs,31,3))
        assert set(frame)==set(shapes)
        for name,shape in shapes.items():
            x=frame[name]
            if x.shape!=shape or x.dtype!=torch.float32 or not torch.isfinite(x).all():raise ValueError('Invalid actual field '+name)
            setattr(self,name,x)
        self.last_tick=tick
        self.check_jump()
        self.compute_reward()
        self.calls+=1
        assert torch.isfinite(self.rew_buf).all()
        return self.rew_buf

    def reset_sums(self,ids):
        # Original reset_idx clears episode sums and external action history;
        # it does NOT clear last_contacts/contact_filt/was_in_flight/base_air_time.
        for x in self.episode_sums.values():x[ids]=0
