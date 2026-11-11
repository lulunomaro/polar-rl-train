"""Strengthen both velocity-error tails: retain square and add absolute cubic."""
import torch
from .scut_flat_physical_delay_env import ScutFlatPhysicalDelayEnv
from .scut_flat_rewards import configuration_v2, make_reward_class
from mod4v1_scut.math_ops import euler_xyz_from_quat


def configuration_forward_square():
    cfg=configuration_v2()
    cfg.lin_vel_xy_square_sigma=1.0
    cfg.rewards['track_lin_vel_xy_square']=-2.0
    cfg.lin_vel_abs_cubic_reference_speed=1.0
    return cfg


class ScutFlatForwardSquareEnv(ScutFlatPhysicalDelayEnv):
    def _make_reward(self, meta):
        RewardBase=make_reward_class(meta,cfg_factory=configuration_forward_square)
        class SquareAbsoluteCubicRewards(RewardBase):
            def _postprocess_reward_terms(self, terms):
                # Use the original horizontal-speed error and deadzone. Multiply
                # the existing gated term so its gates/time scaling stay intact.
                command=self.command[:,0]
                if bool(getattr(self.cfg,'stand_still_deadzone_enabled',False)):
                    threshold=max(float(getattr(self.cfg,'stand_still_deadzone_threshold',.2)),0.)
                    command=torch.where(command.abs()<threshold,torch.zeros_like(command),command)
                pitch=euler_xyz_from_quat(self.robot.data.root_quat_w)[1]
                error_abs=(command-self.robot.data.root_lin_vel_b[:,0]*torch.cos(pitch)).abs()
                adjusted=dict(terms)
                adjusted['track_lin_vel_xy_square']=terms['track_lin_vel_xy_square']*(1.+error_abs/self.cfg.lin_vel_abs_cubic_reference_speed)
                return super()._postprocess_reward_terms(adjusted)
        return SquareAbsoluteCubicRewards(self.view,self.num_envs,self.device)
