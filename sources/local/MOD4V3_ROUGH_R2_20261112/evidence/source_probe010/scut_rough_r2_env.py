"""README R2: feasible low-drop reset over the existing full-DR R1 plant."""
import math
from copy import deepcopy
import torch
from isaaclab.utils.math import quat_from_euler_xyz
from mod4v1_scut.math_ops import euler_xyz_from_quat
from .scut_flat_env import tensor
from .scut_flat_forward_square_env import configuration_forward_square
from .scut_flat_rewards import configuration_v1, make_reward_class
from .scut_rough_r1_env import ScutRoughR1Env


def configuration_r2():
    cfg = configuration_forward_square()
    reference = configuration_v1()
    cfg.enable_state_machines = True
    cfg.airborne_state_machine_cfg = deepcopy(reference.airborne_state_machine_cfg)
    # The deployed actor keeps the original constant seven control-mode slots.
    # Only the internal SCUT reward segmentation is enabled.
    cfg.ctrl_mode_obs_enabled = False
    for name, weight in reference.rewards.items():
        if name.startswith('airborne_'):
            cfg.rewards[name] = weight
    return cfg


class ScutRoughR2Env(ScutRoughR1Env):
    air_reset_fraction = .30  # conditional on eligible flat/shallow terrain
    r2_drop_range = (.05, .10)
    r2_counter_names = ('air_starts', 'observed_clearance', 'first_contact',
                        'posture_recovered', 'command_recovered', 'ended_without_recovery')

    def __init__(self, cfg, meta, bank):
        self._r2_ready = False
        self.r2_force_air = False
        super().__init__(cfg, meta, bank)
        n = self.num_envs
        self.r2_air_reset = torch.zeros(n, device=self.device, dtype=torch.bool)
        self.r2_cleared = self.r2_air_reset.clone()
        self.r2_landed = self.r2_air_reset.clone()
        self.r2_recovered = self.r2_air_reset.clone()
        self.r2_tracked = self.r2_air_reset.clone()
        self.r2_contact_step = torch.full((n,), -1, device=self.device, dtype=torch.long)
        self.r2_stable_steps = torch.zeros(n, device=self.device, dtype=torch.long)
        self.r2_track_steps = self.r2_stable_steps.clone()
        self.r2_drop = torch.zeros(n, device=self.device)
        self.r2_peak_force = self.r2_drop.clone()
        self.r2_counts = torch.zeros(2, len(self.r2_counter_names), device=self.device, dtype=torch.long)
        self.r2_air_state_samples = 0
        self.r2_peak_impact_n = 0.
        self._r2_ready = True

    def _make_reward(self, meta):
        return make_reward_class(meta, cfg_factory=configuration_r2)(self.view, self.num_envs, self.device)

    def _r2_count(self, mask, col):
        nominal = self.full_dr.nominal_env_mask
        self.r2_counts[0, col] += (mask & nominal).sum()
        self.r2_counts[1, col] += (mask & ~nominal).sum()

    def _reset_idx(self, ids):
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        if self._r2_ready:
            failed = torch.zeros(self.num_envs, device=self.device, dtype=torch.bool)
            failed[ids] = self.r2_air_reset[ids] & ~self.r2_recovered[ids]
            self._r2_count(failed, 5)
        super()._reset_idx(ids)
        if not self._r2_ready or not ids.numel():
            return
        for buf in (self.r2_air_reset, self.r2_cleared, self.r2_landed,
                    self.r2_recovered, self.r2_tracked):
            buf[ids] = False
        self.r2_contact_step[ids] = -1
        self.r2_stable_steps[ids] = 0
        self.r2_track_steps[ids] = 0
        self.r2_drop[ids] = 0.
        self.r2_peak_force[ids] = 0.
        level = self.terrain.terrain_levels[ids]
        family = self.terrain_family[ids]
        eligible = self.flat_terrain_mask[ids] | ((level <= 1) & (family != 4) & (family != 6))
        selected = eligible & (torch.rand(len(ids), device=self.device, generator=self.reset_generator) < self.air_reset_fraction)
        if self.r2_force_air:
            selected[:] = True
        air = ids[selected]
        if not air.numel():
            return
        n = len(air)
        gen = self.reset_generator
        pick = torch.randint(len(self._bank_h), (n,), device=self.device, generator=gen)
        q = self._bank_q[pick][:, self._bank_ids].clone()
        root = tensor(self.robot.data.default_root_state)[air].clone()
        root[:, :3] += self.scene.env_origins[air]
        drop = torch.empty(n, device=self.device).uniform_(*self.r2_drop_range, generator=gen)
        root[:, 2] = self.scene.env_origins[air, 2] + self._bank_h[pick] + drop
        def uniform(lo, hi):
            return torch.empty(n, device=self.device).uniform_(lo, hi, generator=gen)
        root[:, 3:7] = quat_from_euler_xyz(uniform(-.03,.03), uniform(-.03,.03), uniform(-math.pi,math.pi))
        root[:, 7:] = 0.
        root[:, 7:9] = torch.empty(n, 2, device=self.device).uniform_(-.1,.1,generator=gen)
        self.robot.write_root_state_to_sim(root, env_ids=air)
        self.robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=air)
        self.actions[air] = 0.
        self.torque[air] = 0.
        self.zero_torque_remaining[air] = 0
        # Replacing a ground reset also removes its 1.5s command override.
        self.command[air] = self._ground_original_command[air]
        self.heading_env[air] = self._ground_original_heading[air]
        self._ground_command_until[air] = 0
        self.reset_count_by_mode -= torch.bincount(self.reset_modes[air], minlength=3)
        self.reset_modes[air] = -1  # air is reported separately, not as ground
        self.r2_air_reset[air] = True
        self.r2_drop[air] = drop
        starts = torch.zeros_like(self.r2_air_reset)
        starts[air] = True
        self._r2_count(starts, 0)
        self._execution_pending[air] = True
        self._sensor_pending[air] = True
        self.reward.reset(air)
        self.reward.command.copy_(self.command)
        self.reward.height_cmd.copy_(self.height)
        request = getattr(self.reward, 'airborne_force_enter_request', None)
        if request is None:
            request = torch.zeros(self.num_envs, device=self.device, dtype=torch.bool)
            self.reward.airborne_force_enter_request = request
        request[air] = True
        self.reward._invalidate_step_caches()

    def prepare_endpoint(self):
        super().prepare_endpoint()
        # Same hook as the existing Flat-v1 environment, with no actor mode change.
        if getattr(self.reward.cfg, 'enable_state_machines', False):
            self.reward._on_command_updated()
            self.reward.state_machine_manager.on_observation_step(self.reward)

    def _get_dones(self):
        term, timeout = super()._get_dones()
        if not self._r2_ready:
            return term, timeout
        r = self.reward
        force = r._get_wheel_contact_force_peaks(r.contact_sensor.data.net_forces_w_history)
        gaps = self.view.data.body_pos_w[:,r._wheel_link_idx,2] - r.ground_wheels - .0625
        genuine_clear = self.r2_air_reset & ~self.r2_cleared & (gaps > .01).all(-1) & (force < 1.).all(-1)
        self._r2_count(genuine_clear, 1)
        self.r2_cleared |= genuine_clear
        contact = self.r2_air_reset & self.r2_cleared & ~self.r2_landed & (force > 1.).any(-1)
        self._r2_count(contact, 2)
        self.r2_landed |= contact
        self.r2_contact_step[contact] = self.episode_length_buf[contact]
        near_landing = self.r2_air_reset & self.r2_landed & ((self.episode_length_buf-self.r2_contact_step) <= 25)
        self.r2_peak_force = torch.maximum(self.r2_peak_force, force.amax(-1)*near_landing)
        self.r2_peak_impact_n = max(self.r2_peak_impact_n, float(self.r2_peak_force.max()))
        roll, pitch, _ = euler_xyz_from_quat(self.view.data.root_quat_w)
        near_wheels = (gaps.abs() < .025).all(-1)
        stable = self.r2_landed & (roll.abs() < .2) & (pitch.abs() < .2) & near_wheels & ~term
        stable &= (self._height_observation()-self.height).abs() < .05
        self.r2_stable_steps = torch.where(stable, self.r2_stable_steps+1, 0)
        recovered = self.r2_air_reset & ~self.r2_recovered & (self.r2_stable_steps >= 25)
        self._r2_count(recovered, 3)
        self.r2_recovered |= recovered
        tracking = stable & ((self.view.data.root_lin_vel_b[:,0]-self.command[:,0]).abs() < .3)
        tracking &= (self.view.data.root_ang_vel_b[:,2]-self.command[:,2]).abs() < .5
        self.r2_track_steps = torch.where(tracking, self.r2_track_steps+1, 0)
        tracked = self.r2_air_reset & ~self.r2_tracked & (self.r2_track_steps >= 25)
        self._r2_count(tracked, 4)
        self.r2_tracked |= tracked
        self.r2_air_state_samples += int(self.reward.height_reward_airborne_state.sum())
        return term, timeout

    def r2_summary(self):
        return dict(stage='MOD4-R2', counters_by_group={name:dict(zip(self.r2_counter_names,row)) for name,row in zip(('nominal','full_DR'),self.r2_counts.tolist())}, extra_drop_range_m=list(self.r2_drop_range),air_probability_on_eligible_reset=self.air_reset_fraction,active_air_resets=int(self.r2_air_reset.sum()),airborne_state_env_step_samples=self.r2_air_state_samples,peak_landing_wheel_force_n=self.r2_peak_impact_n,ctrl_mode_obs_enabled=False,metric='posture/command recovered after25continuous policy endpoints; geometric near-wheel support, not claimed graduation; end failures can include physics guard',reset_counts_excluding_air=self.reset_count_by_mode.tolist())

    def r2_checkpoint_state(self):
        return dict(counters=self.r2_counts,air_state_samples=self.r2_air_state_samples,peak_impact_n=self.r2_peak_impact_n,air_reset=self.r2_air_reset,drop=self.r2_drop,landed=self.r2_landed,recovered=self.r2_recovered,scope='cumulative counters plus diagnostic current episode; fresh physical episodes on resume')

    def restore_r2_counters(self, state):
        self.r2_counts.copy_(state['counters'].to(self.r2_counts))
        self.r2_air_state_samples = int(state['air_state_samples'])
        self.r2_peak_impact_n = float(state['peak_impact_n'])
