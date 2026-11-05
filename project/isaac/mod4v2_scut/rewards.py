"""Use SCUT equations; continuous motors have no independent angular stop cost."""
import torch
from types import MethodType, SimpleNamespace
from .fudan_source import FudanJumpFunctions
from .math_ops import quat_apply_inverse
from .shared import load, export
_source=load('rewards')
export(_source,globals())


class ScutRewards(_source.ScutRewards):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fudan_last_contacts = torch.zeros(self.num_envs, 2, dtype=torch.bool, device=self.device)
        self.fudan_contact_filt = self.fudan_last_contacts.clone()
        self.fudan_was_in_flight = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self.fudan_base_air_time = torch.zeros(self.num_envs, device=self.device)
        self.fudan_leg_length = torch.zeros(self.num_envs, 2, device=self.device)
        self.fudan_leg_theta = self.fudan_leg_length.clone()
        self.fudan_reward_cfg = SimpleNamespace(rewards=SimpleNamespace(
            clip_single_reward=2.5, only_positive_rewards=False, tracking_sigma=.25))

    def virtual_legs(self):
        data = self.robot.data
        delta = data.body_pos_w[:, self._wheel_link_idx] - data.root_pos_w[:, None]
        q = data.root_quat_w[:, None].expand(-1, 2, -1)
        wheel_b = quat_apply_inverse(q, delta)
        anchors = delta.new_tensor([self.contract['joints'][side+'_hip']['local_pos0']
                                    for side in ('left', 'right')])
        leg = wheel_b - anchors[None]
        # Fudan L0/theta0 describe its sagittal hip-to-wheel virtual leg. Use
        # actual MOD4 poses, without the reference robot's link lengths/signs.
        length = torch.linalg.vector_norm(leg[..., [0, 2]], dim=-1)
        theta = torch.atan2(-leg[..., 0], -leg[..., 2])
        return length, theta

    def compute(self):
        data = self.robot.data
        self.fudan_leg_length, self.fudan_leg_theta = self.virtual_legs()
        commands = torch.stack((self.command[:, 0], self.command[:, 2], self.height_cmd), -1)
        view = SimpleNamespace(cfg=self.fudan_reward_cfg, dt=self.step_dt, device=self.device,
            root_states=torch.cat((data.root_pos_w, data.root_quat_w,
                                   data.root_lin_vel_w, data.root_ang_vel_b), -1),
            base_lin_vel=data.root_lin_vel_b, base_ang_vel=data.root_ang_vel_b,
            projected_gravity=data.projected_gravity_b,
            contact_forces=self.contact_sensor.data.net_forces_w,
            feet_indices=self._wheel_link_idx, penalised_contact_indices=self._reset_contact_link_idx,
            last_contacts=self.fudan_last_contacts, contact_filt=self.fudan_contact_filt,
            was_in_flight=self.fudan_was_in_flight, base_air_time=self.fudan_base_air_time,
            L0=self.fudan_leg_length, theta0=self.fudan_leg_theta, commands=commands,
            actions=self._actions, last_actions=self._previous_actions.unsqueeze(-1),
            torques=data.applied_torque[:, self._actuate_idx],
            rew_buf=torch.zeros(self.num_envs, device=self.device),
            episode_sums=self._episode_sums, reward_names=list(self.cfg.rewards),
            reward_scales={k:v*self.step_dt for k,v in self.cfg.rewards.items()})
        FudanJumpFunctions.check_jump(view)
        self.fudan_last_contacts = view.last_contacts
        self.fudan_contact_filt = view.contact_filt
        raw, weighted = {}, {}
        def instrument(name):
            original = MethodType(getattr(FudanJumpFunctions, '_reward_'+name), view)
            def term():
                value = original()
                raw[name] = value.clone()
                weighted[name] = (value*view.reward_scales[name]).clamp(-2.5*self.step_dt, 2.5*self.step_dt).detach()
                return value
            return term
        view.reward_functions = [instrument(name) for name in view.reward_names]
        for name in view.reward_names:
            self._episode_sums.setdefault(name, torch.zeros(self.num_envs, device=self.device))
        FudanJumpFunctions.compute_reward(view)
        self.raw_terms, self._last_reward_terms = raw, weighted
        self.command_generator.compute(self.step_dt)
        self._resample_custom_cmd(self.command_generator.command_counter)
        self.command = self.command_generator.command.clone()
        self._on_command_updated()
        self._last_total_reward = view.rew_buf.detach()
        return view.rew_buf

    def reset(self, ids):
        super().reset(ids)
        for name in ('fudan_last_contacts', 'fudan_contact_filt', 'fudan_was_in_flight',
                     'fudan_base_air_time', 'fudan_leg_length', 'fudan_leg_theta'):
            getattr(self, name)[ids] = 0

    def motor_stop_terms(self,airborne=False):
        # Upstream evaluates these helper outputs even when their weights are0.
        # Released v2 motors are continuous; no finite motor-angle boundary exists.
        for name in ('left_crank','left_hip','right_crank','right_hip'):
            if self.contract['joints'][name]['limits_si'] != [None,None]:
                raise ValueError('Unexpected finite v2 motor boundary: '+name)
        zeros=torch.zeros(self.num_envs,device=self.device)
        return zeros,zeros.clone(),zeros.clone()
