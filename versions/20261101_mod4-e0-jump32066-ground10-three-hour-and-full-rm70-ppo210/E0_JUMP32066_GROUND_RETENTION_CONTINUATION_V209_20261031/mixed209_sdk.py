"""Disjoint original E0 ground and literal Fudan JUMP tasks on the own MOD4.

Only task assignment/SDK reward routing/command selection live here. Original
reward functions and their weights remain in their separate frozen sources.
"""
import copy
import inspect
import torch
from isaaclab.managers import ManagerTermBase, RewardTermCfg
from isaaclab.envs.mdp.commands.velocity_command import UniformVelocityCommand
from directional_spin_runtime import DirectionalSpinCommand
from spring_nominal_sdk_readback import tensor
import mod4_task as task
import jump194_sdk as jump


def assignment(env):
    if getattr(env, '_mixed209_flat', None) is None:
        assert env.num_envs % 10 == 0
        env._mixed209_flat = torch.arange(env.num_envs, device=env.device) % 10 == 0
        env._mixed209_mode = (~env._mixed209_flat).long()
    return env._mixed209_flat


class OriginalFlat209Term(ManagerTermBase):
    """Preserve each E0 term, including original stateful term reset calls."""
    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        inner_cfg = copy.deepcopy(cfg)
        inner_cfg.func = cfg.params['original_func']
        inner_cfg.params = copy.deepcopy(cfg.params['original_params'])
        self.original = (inner_cfg.func(inner_cfg, env)
                         if inspect.isclass(inner_cfg.func) else inner_cfg.func)
        self.original_params = inner_cfg.params

    def __call__(self, env, original_func, original_params):
        value = tensor(self.original(env, **self.original_params))
        return torch.where(assignment(env), value, torch.zeros_like(value))

    def reset(self, env_ids=None):
        reset = getattr(self.original, 'reset', None)
        return reset(env_ids) if reset is not None else {}


def original_jump209_rate(env):
    value = env.original_jump_once() / env.step_dt
    return torch.where(assignment(env), torch.zeros_like(value), value)


class Mixed209Command(DirectionalSpinCommand):
    """Original E0 command for flat IDs; original JUMP command for jump IDs."""
    def __init__(self, cfg, env):
        assignment(env)
        super().__init__(cfg, env)
        self.command_uid209 = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)

    def _resample_command(self, env_ids):
        ids = torch.as_tensor(env_ids, dtype=torch.long, device=self.device)
        flat = ids[assignment(self._env)[ids]]
        airborne_task = ids[~assignment(self._env)[ids]]
        if len(flat):
            super()._resample_command(flat)
            task.height_cmd(self._env)[flat, 0] = .25
        if len(airborne_task):
            # Call the actual SDK uniform sampler with the exact original JUMP
            # configuration. The original E0 dynamic updater sees false flags
            # for these persistent IDs and therefore leaves them unchanged.
            saved_cfg = self.cfg
            self.cfg = copy.deepcopy(saved_cfg)
            self.cfg.ranges.lin_vel_x = (-2.1, 2.1)
            self.cfg.ranges.lin_vel_y = (0., 0.)
            self.cfg.ranges.ang_vel_z = (-2., 2.)
            self.cfg.ranges.heading = (-3.14, 3.14)
            self.cfg.rel_standing_envs = 0.
            self.cfg.rel_heading_envs = 0.
            try:
                UniformVelocityCommand._resample_command(self, airborne_task)
            finally:
                self.cfg = saved_cfg
            for name in ('is_pure_spin', 'is_moving_spin', 'is_transition_spin'):
                getattr(self, name)[airborne_task] = False
            self.signed_yaw[airborne_task] = 0.
            self.phase_elapsed[airborne_task] = 0.
            self.time_left[airborne_task] = 20.
            task.height_cmd(self._env)[airborne_task, 0] = torch.empty(
                len(airborne_task), device=self.device).uniform_(.12, .15)
        self._env._mod4_mode_bit = self._env._mixed209_mode.clone()
        if hasattr(self, 'command_uid209'):
            self.command_uid209[ids] += 1


def configure(cfg):
    # cfg was built with the frozen E0 environment variables and original
    # directional command configuration, before the JUMP scene adapter runs.
    ground_rewards = cfg.rewards
    ground_command = copy.deepcopy(cfg.commands.twist)
    assert ground_command.class_type is DirectionalSpinCommand
    assert tuple(ground_command.resampling_time_range) == (12., 16.)
    assert ground_command.rel_standing_envs == .1
    jump.configure(cfg)
    cfg.commands.twist = ground_command
    cfg.commands.twist.class_type = Mixed209Command
    selected = {}
    for name, value in vars(ground_rewards).items():
        if isinstance(value, RewardTermCfg) and value.weight != 0.:
            selected[name] = dict(weight=value.weight, params=copy.deepcopy(value.params),
                                  function=value.func.__module__ + '.' + value.func.__name__)
            original_func = value.func
            original_params = copy.deepcopy(value.params)
            value.func = OriginalFlat209Term
            value.params = dict(original_func=original_func, original_params=original_params)
    ground_rewards.original_jump209 = RewardTermCfg(func=original_jump209_rate, weight=1.)
    cfg.rewards = ground_rewards
    cfg.mixed209_original_ground_terms = selected
    return cfg


class Mixed209Env(jump.JumpMod4Env):
    def _reset_idx(self, ids):
        out = super()._reset_idx(ids)
        flat = assignment(self)
        self._mod4_mode_bit = self._mixed209_mode.clone()
        # The JUMP superclass resets only its literal reward sums/action/root
        # history. It deliberately retains the pinned contact-flight memory.
        # Ground history reset remains the original E0 reset_history event.
        ground_ids = torch.as_tensor(ids, device=self.device, dtype=torch.long)
        ground_ids = ground_ids[flat[ground_ids]]
        task.height_cmd(self)[ground_ids, 0] = .25
        return out

    def binding_receipt(self):
        flat = assignment(self)
        return dict(original_jump_binding=super().binding_receipt(),
                    flat_envs=int(flat.sum()), jump_envs=int((~flat).sum()),
                    task_modes=dict(ground=0, jump=1),
                    flat_command='Original E0_DIRECTIONAL_SPIN_V1, standing .1, pure .3, moving .2; resample12..16s',
                    flat_height_m=.25, jump_resample_s=20.,
                    ground_terms=self.cfg.mixed209_original_ground_terms,
                    reward_routing='disjoint per-environment original E0 or original FudanJUMP, no blended terms',
                    original_frozen_E0_file_untouched=True,
                    trainable_input='latest E0-JUMP32066 full actor/critic/STD/17Adam',
                    all_physical_guards_unchanged=True)
