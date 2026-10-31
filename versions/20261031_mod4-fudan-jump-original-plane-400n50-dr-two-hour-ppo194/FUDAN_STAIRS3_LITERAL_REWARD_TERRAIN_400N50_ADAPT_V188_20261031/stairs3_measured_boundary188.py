"""Own SDK state is mapped outside the unchanged original reward functions."""
import copy
import torch
from literal_stairs3_original_methods import OriginalStairs3Methods
from literal_stairs3_original_config import OriginalStairs3Cfg,class_to_dict

REQUIRED=('commands','base_lin_vel','base_ang_vel','projected_gravity','base_height',
          'torques','dof_vel','dof_acc','dof_pos','dof_pos_limits','actions',
          'last_actions','theta0','contact_forces','penalised_contact_indices')

class LiteralStairs3Kernel(OriginalStairs3Methods):
    def __init__(self,n,device,dt):
        assert dt==.02
        self.cfg=OriginalStairs3Cfg();self.num_envs=n;self.device=device;self.dt=dt
        self.reward_scales=copy.deepcopy(class_to_dict(self.cfg.rewards.scales))
        self.rew_buf=torch.zeros(n,device=device)
        self._prepare_reward_function()
        assert len(self.reward_names)==16
        self.calls=0;self.last_tick=None

    def bind_and_compute_once(self,frame,control_tick):
        if self.last_tick==control_tick:raise RuntimeError('Reward called twice for one physical control')
        missing=set(REQUIRED)-set(frame)
        if missing:raise ValueError('Missing actual STAIRS3 measured input '+repr(sorted(missing)))
        n=self.num_envs
        shapes={'commands':(n,4),'base_lin_vel':(n,3),'base_ang_vel':(n,3),'projected_gravity':(n,3),
            'base_height':(n,),'torques':(n,6),'dof_vel':(n,6),'dof_acc':(n,6),'dof_pos':(n,6),
            'dof_pos_limits':(6,2),'actions':(n,6),'last_actions':(n,6,2),'theta0':(n,2)}
        for name,shape in shapes.items():
            value=frame[name]
            if not torch.is_tensor(value) or tuple(value.shape)!=shape or not torch.isfinite(value).all():
                raise ValueError('Wrong/nonfinite measured '+name)
        if frame['penalised_contact_indices'].numel()!=0:
            raise ValueError('Original selected WheelLeggedCfg penalize_contacts_on=[] must remain empty')
        for name in REQUIRED:setattr(self,name,frame[name])
        self.compute_reward();self.calls+=1;self.last_tick=control_tick
        if not torch.isfinite(self.rew_buf).all():raise RuntimeError('Original STAIRS3 reward became nonfinite')
        return self.rew_buf

    def reset_sums(self,ids):
        for value in self.episode_sums.values():value[ids]=0
