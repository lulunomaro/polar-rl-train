"""E0 source adapter for Robotics-Wheelbipe-V14-Flat-v0, not Play/Flat1/Flat2/Rough.

Call configure(cfg, task_module) after the parent's hardware gates, before construction;
then bind(env), set_training_iteration(env, real_runner_iteration), before reset/step.
The parent owns PPO, normalizers, physics/scene/RNG state and complete checkpoint I/O.
This module was source-adapted, not executed against IsaacLab or a simulator.
"""
from copy import deepcopy
from math import pi
from types import MethodType

import torch
from isaaclab.envs.mdp.commands.velocity_command import UniformVelocityCommand
from isaaclab.managers import TerminationTermCfg
from isaaclab.utils.math import euler_xyz_from_quat, wrap_to_pi

_SCUT = "C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/"
_LOCAL = "F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/"
SOURCE_REFERENCES = {
    "alignment": _LOCAL + "SCUT_ORIGINAL_TRAINING_ALIGNMENT_V1.md:1-100",
    "flat_cfg": _SCUT + "direct/wheelbipe/wheelbipe_V14/env_cfg.py:468-607,769-830,975-1086",
    "special_command": _SCUT + "manager/mdp/isaaclab/commands.py:275-295,321-395,406-552,577-604",
    "contact_bodies": _SCUT + "direct/wheelbipe/wheelbipe_V14/env.py:134-145",
    "height": _SCUT + "direct/wheelbipe/wheelbipe25_v3/env.py:1321-1346,5075-5080,5590-5602",
    "done": _SCUT + "direct/wheelbipe/wheelbipe25_v3/env.py:4863-5028,5054-5058",
    "obs_gate": _SCUT + "direct/wheelbipe/wheelbipe25_v3/env.py:2483-2518,3164-3179,4091-4095",
    "reward_mask": _SCUT + "direct/wheelbipe/wheelbipe25_v3/env.py:4007-4018",
    "mod4": _LOCAL + "e0_hour_actual_recipe_sources/mod4_task.py:418-476,735-811,1150-1160,1205-1313,1468-1488,1647,1783-1833",
    "reset": _LOCAL + "e0_hour_actual_recipe_sources/scut_flat_rescue.py:84-116",
    "hardware_gates": _LOCAL + "e0_hour_actual_recipe_sources/train_mod4v1_e0.py:139-141",
    "sdk_uniform": _LOCAL + "sdk_scut_alignment_abi_source_v1/envs/mdp/commands/velocity_command.py:51-98,134-198",
    "sdk_command": _LOCAL + "sdk_scut_alignment_abi_source_v1/managers/command_manager.py:114-181",
    "sdk_order": _LOCAL + "sdk_scut_alignment_abi_source_v1/envs/manager_based_rl_env.py:233-270,362-407",
}
# Source order matters for mode IDs and randomized probability-bucket ordering.
SPECIAL_MODES = (
    ("spin_low", 3000, .15, ((-.1, .1),), ((0., 0.),), ((2*pi, 3.25*pi), (-3.25*pi, -2*pi))),
    ("spin_mid", 4000, .15, ((-.1, .1),), ((0., 0.),), ((3.25*pi, 4.5*pi), (-4.5*pi, -3.25*pi))),
    ("dash", 2000, .30, ((2., 3.), (-3., -2.)), ((0., 0.),), ((-2*pi, 2*pi),)),
)
GUIDES = tuple(f"guide_roller_{i:02d}" for i in range(8))
RECEIPT = {
    "status": "SOURCE_ONLY_NOT_RUNTIME_VALIDATED", "expert": "E0", "task": "Robotics-Wheelbipe-V14-Flat-v0",
    "reference_head_reported_by_parent": "b8ff79f3df855faf9dc92f4a282bd80c42649466",
    "commands": {"resampling_time_range": (5., 15.), "rel_standing_envs": .1,
                 "rel_heading_envs": .5, "heading_control_stiffness": 5., "heading_command": True,
                 "vx": (-2.7, 2.7), "vy": (0., 0.), "yaw": (-2*pi, 2*pi), "heading": (-pi, pi)},
    "special_modes": SPECIAL_MODES, "iteration_end": -1, "special_min_episode_s": 5.,
    "special_require_stable": False, "special_assignment": "exclusive randomized probability buckets",
    "dash_disable_jump_takeoff": True, "height_default": .22, "height_range": (.20, .42),
    "special_height_modes_enabled": False, "special_height_sine_step_rel_envs": (0., 0.),
    "done": {"episode_s": 20., "timeout": "episode_length_buf >= max_episode_length - 1",
             "contact_N_strict_gt": 1., "roll_pitch_deg_strict_gt": 40., "consecutive_controls": 20,
             "active_joint_speed_strict_gt": 500., "root_ang_component_strict_gt": 200.,
             "root_lin_component_strict_gt": 100., "raw_obs_abs_strict_gt": 120.,
             "obs_gate": "terminate_on_obs_outlier and value_debug_step > 10",
             "debug_value_diagnosis_default": False, "default_obs_gate": "dormant: debug counter stays zero"},
    "body_mapping": {"base_link": "chassis", ".*_guide_link": GUIDES,
                     "gimbal_yaw_link/gimbal_pitch_link": "absent; no fabricated MOD4 body"},
    "differences": (
        "MOD4 actor35/critic38/action6 and existing twist/height_cmd/mode_onehot semantics retained; upstream35/78/6 is not observation identity",
        "reset-morphology adaptation: retain MOD4 feasible closed-chain reset bank; no SCUT q/random-start numeric-pose equivalence",
        "true runner iteration supplied explicitly; no source step-based iteration extrapolation or learner-iteration rewrite",
        "source parent normal resampling draws standing a second time; .1 is configured probability, not guaranteed final standing fraction",
        "MOD4 Manager order retained: dones -> rewards -> selected resets -> commands -> observations",
        "height follows command resampling; source-special reset pose/air overrides are not imported across morphologies",
        "MOD4 original closure/mimic and supplied nonfinite hardware gates retained as additional hard dones",
    ),
    "untouched": "300N/140-200mm/31 bodies/joints; 50Hz control/100Hz feedback/.0025/TGS32,4; per-env closure .01m/mimic .01; learner/independent norms",
    "full_checkpoint_owner": "parent: learner, normalization, global RNG, physics and all non-adapter environment state",
}
_COMMAND_BUFFERS = ("vel_command_b", "heading_target", "is_heading_env", "is_standing_env", "time_left",
                    "command_counter", "special_mode_id", "_error_xy_sum", "_error_yaw_sum", "_step_count")
_ENV_BUFFERS = ("_scut_v14_duration_counter", "_scut_v14_duration_raw", "_scut_v14_numerical_failure_mask", "_mod4_height_cmd")


def _tensor(value):
    if isinstance(value, torch.Tensor):
        return value
    converted = getattr(value, "torch", None)
    if isinstance(converted, torch.Tensor):
        return converted
    raise TypeError("SCUT adapter requires the source-verified torch tensor / .torch SDK ABI")


def _ids(env, ids):
    if ids is None or isinstance(ids, slice):
        all_ids = torch.arange(env.num_envs, device=env.device, dtype=torch.long)
        return all_ids if ids is None else all_ids[ids]
    return torch.as_tensor(ids, device=env.device, dtype=torch.long)


class ScutV14FlatCommand(UniformVelocityCommand):
    """Original Uniform ABI plus the ordinary V14Flat special-mode source algorithm."""
    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        self.special_mode_id = torch.full((self.num_envs,), -1, device=self.device, dtype=torch.long)
        self.training_iteration = 0
        self._resetting = False
        height = getattr(env, "_mod4_height_cmd", None)
        if height is None:
            env._mod4_height_cmd = torch.full((self.num_envs, 1), .22, dtype=torch.float, device=self.device)
        elif isinstance(height, torch.Tensor) and height.shape == (self.num_envs, 1):
            height.fill_(.22)
        else:
            raise RuntimeError("MOD4 height_cmd ABI must remain [num_envs,1]")

    def set_training_iteration(self, n):
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise ValueError("Pass the real nonnegative integer runner iteration")
        self.training_iteration = n

    def reset(self, env_ids=None):
        # Manager clears episode_length only AFTER command.reset; reset is not an old-episode resample.
        self._resetting = True
        try:
            return super().reset(_ids(self._env, env_ids))
        finally:
            self._resetting = False

    @staticmethod
    def _sample(spec, n, device):
        intervals = []
        for lo, hi in sorted((min(a, b), max(a, b)) for a, b in spec):
            if intervals and lo <= intervals[-1][1] + 1e-6:
                intervals[-1] = (intervals[-1][0], max(intervals[-1][1], hi))
            else:
                intervals.append((lo, hi))
        if len(intervals) == 1:
            lo, hi = intervals[0]
            return torch.full((n,), lo, dtype=torch.float, device=device) if lo == hi else torch.empty(n, dtype=torch.float, device=device).uniform_(lo, hi)
        widths = torch.tensor([hi-lo for lo, hi in intervals], device=device, dtype=torch.float)
        probs = widths / widths.sum() if widths.sum() > 0 else torch.ones_like(widths) / len(intervals)
        bins = torch.multinomial(probs, n, replacement=True)
        result = torch.empty(n, dtype=torch.float, device=device)
        for i, (lo, hi) in enumerate(intervals):
            mask = bins == i
            count = int(mask.sum().item())
            if count:
                result[mask] = lo if lo == hi else torch.empty(count, dtype=torch.float, device=device).uniform_(lo, hi)
        return result

    def _resample_command(self, env_ids):
        ids = _ids(self._env, env_ids)
        self.is_standing_env[ids] = torch.empty(ids.numel(), device=self.device).uniform_(0., 1.) <= self.cfg.rel_standing_envs
        self.special_mode_id[ids] = -1
        nonstanding = ids[~self.is_standing_env[ids]]
        ready = self._env.episode_length_buf[nonstanding].float() * self._env.step_dt >= 5.
        if self._resetting:
            ready[:] = False
        candidates, delayed = nonstanding[ready], nonstanding[~ready]
        active = [i for i, mode in enumerate(SPECIAL_MODES) if self.training_iteration >= mode[1]]
        if candidates.numel() and active:
            order = torch.randperm(len(active), device=self.device).tolist()
            u = torch.rand(candidates.numel(), device=self.device)
            cumulative = 0.
            for j in order:
                mode = active[j]
                high = cumulative + SPECIAL_MODES[mode][2]
                self.special_mode_id[candidates[(u >= cumulative) & (u < high)]] = mode
                cumulative = high
        for i, mode in enumerate(SPECIAL_MODES):
            selected = candidates[self.special_mode_id[candidates] == i]
            if selected.numel():
                for axis, spec in enumerate(mode[3:]):
                    self.vel_command_b[selected, axis] = self._sample(spec, int(selected.numel()), self.device)
        normal = torch.cat((delayed, candidates[self.special_mode_id[candidates] < 0]))
        if normal.numel():
            super()._resample_command(normal)  # Preserve the source's second standing draw.
        height = self._env._mod4_height_cmd
        if not isinstance(height, torch.Tensor) or height.shape != (self.num_envs, 1):
            raise RuntimeError("MOD4 height_cmd ABI must remain [num_envs,1]")
        height[ids, 0] = torch.empty(ids.numel(), dtype=torch.float, device=self.device).uniform_(.20, .42)

    def _update_command(self):
        heading_ids = (self.is_heading_env & (self.special_mode_id < 0)).nonzero(as_tuple=False).flatten()
        if heading_ids.numel():
            error = wrap_to_pi(self.heading_target[heading_ids] - _tensor(self.robot.data.heading_w)[heading_ids])
            self.vel_command_b[heading_ids, 2] = torch.clip(5. * error, -2*pi, 2*pi)
        self.vel_command_b[self.is_standing_env.nonzero(as_tuple=False).flatten()] = 0.


def scut_time_out(env):
    return env.episode_length_buf >= env.max_episode_length - 1


def scut_termination(env):
    if not getattr(env, "_scut_v14_bound", False):
        raise RuntimeError("Call bind(env) before the first control step")
    data = env.scene["robot"].data
    velocities = (_tensor(data.joint_vel)[:, env._scut_v14_active_joint_ids],
                  _tensor(data.root_ang_vel_b), _tensor(data.root_lin_vel_b))
    numerical = torch.zeros(env.num_envs, device=env.device, dtype=torch.bool)
    for value, limit in zip(velocities, (500., 200., 100.)):
        numerical |= ~torch.isfinite(value).all(dim=-1) | (value.abs().amax(dim=-1) > limit)
    # This is ready before RewardManager.compute; obs-only/hardware failures do not enter it.
    env._scut_v14_numerical_failure_mask.copy_(numerical)
    immediate = numerical.clone()
    debug_enabled, obs_enabled, obs_override, obs_alert = env._scut_v14_obs_gate_config
    if obs_enabled and env._scut_v14_value_debug_step > 10:
        # Provider must expose cached pre-clip/pre-scale MOD4 policy/critic stats, never recompute observations.
        stats = env._scut_v14_raw_observation_statistics()
        if set(stats) != {"policy_max_abs", "critic_max_abs", "policy_nonfinite", "critic_nonfinite"}:
            raise RuntimeError("Exact cached raw-observation statistics are required")
        obs_threshold = obs_override if obs_override > 0. else obs_alert
        for key, value in stats.items():
            value = _tensor(value)
            if value.shape != (env.num_envs,):
                raise RuntimeError("Raw-observation statistics must be per-environment")
            if key.endswith("nonfinite"):
                immediate |= value
            elif obs_threshold > 0.:
                immediate |= value > obs_threshold
    raw = torch.zeros_like(numerical)
    for name in ("chassis_contact", "guide_contact"):
        forces = _tensor(env.scene[name].data.net_forces_w)
        raw |= (torch.linalg.vector_norm(forces, dim=-1) > 1.).any(dim=-1)
    roll, pitch, _ = euler_xyz_from_quat(_tensor(data.root_quat_w))
    raw |= (wrap_to_pi(roll).abs() > 40.*pi/180.) | (wrap_to_pi(pitch).abs() > 40.*pi/180.)
    delayed = raw & ~immediate
    env._scut_v14_duration_raw.copy_(delayed)
    counter = env._scut_v14_duration_counter
    counter.copy_(torch.where(delayed, (counter + 1).clamp(max=20), torch.zeros_like(counter)))
    # With debug disabled the original source never increments its reward-debug counter.
    if debug_enabled:
        env._scut_v14_value_debug_step += 1  # Next done sees the preceding reward-call count.
    return (counter >= 20) | immediate


def configure(cfg, task_module):
    """Prebuild-only: replace commands/performance dones, preserve original plant/reset/obs/actions."""
    if getattr(task_module, "TERRAIN", None) != "flat":
        raise ValueError("This adapter is exclusively the E0 flat expert")
    if getattr(cfg, "_scut_v14_configured", False):
        raise RuntimeError("configure is prebuild and single-use")
    for name in ("closure", "mimic"):
        term = getattr(cfg.terminations, name)
        if term is None or term.params["threshold"] != .01:
            raise ValueError("Parent must retain its original per-env closure/mimic .01 hardware rules before configure")
    performance = {"bad_orientation", "base_contact", "low_base", "tunnel_roof_hit"}
    hardware = {"closure", "mimic", "nonfinite", "nonfinite_state", "finite_state", "hardware_integrity"}
    for name, term in tuple(vars(cfg.terminations).items()):
        if name in performance:
            setattr(cfg.terminations, name, None)
        elif term is not None and hasattr(term, "func") and name not in hardware | {"time_out"}:
            raise ValueError(f"Unclassified termination {name!r}; identify its real hardware/performance semantics")
    cfg.terminations.time_out = TerminationTermCfg(func=scut_time_out, time_out=True)
    cfg.terminations.scut_v14 = TerminationTermCfg(func=scut_termination)
    disabled = []
    if cfg.curriculum is not None:
        for name, term in tuple(vars(cfg.curriculum).items()):
            if term is not None and hasattr(term, "func"):
                disabled.append(name)
                setattr(cfg.curriculum, name, None)  # Flat-v0 curriculum=None, not the old gyro schedule.
    command = cfg.commands.twist
    command.class_type = ScutV14FlatCommand  # Never subclass/retain WorldGyro behavior.
    command.resampling_time_range = (5., 15.)
    command.rel_standing_envs, command.rel_heading_envs = .1, .5
    command.heading_command, command.heading_control_stiffness = True, 5.
    command.ranges.lin_vel_x, command.ranges.lin_vel_y = (-2.7, 2.7), (0., 0.)
    command.ranges.ang_vel_z, command.ranges.heading = (-2*pi, 2*pi), (-pi, pi)
    if hasattr(cfg.events, "reset_height_command"):
        cfg.events.reset_height_command = None  # Remove duplicate legacy height RNG, not the feasible pose reset.
    cfg.episode_length_s = 20.
    cfg._scut_v14_active_joint_names = tuple(task_module.LEG_ORDER + task_module.WHEEL_ORDER)
    cfg._scut_v14_configured = True
    receipt = deepcopy(RECEIPT)
    receipt["removed_manager_curricula"] = tuple(disabled)
    receipt["source_references"] = deepcopy(SOURCE_REFERENCES)
    return receipt


def bind(env):
    """Postbuild: validate the real ABI and attach only selected-ID counter cleanup."""
    if not getattr(env.cfg, "_scut_v14_configured", False) or getattr(env, "_scut_v14_bound", False):
        raise RuntimeError("bind requires a configured, not-yet-bound environment")
    command = env.command_manager.get_term("twist")
    if type(command) is not ScutV14FlatCommand:
        raise TypeError("twist must be the source adapter, without the old WorldGyro subclass")
    robot = env.scene["robot"]
    if len(robot.body_names) != 31 or "chassis" not in robot.body_names or not set(GUIDES) <= set(robot.body_names):
        raise RuntimeError("Expected the original MOD4 31-body chassis/eight-guide morphology")
    for sensor_name, expected in (("chassis_contact", ("chassis",)), ("guide_contact", GUIDES)):
        actual = tuple(env.scene[sensor_name].body_names)
        if len(actual) != len(expected) or set(actual) != set(expected):
            raise RuntimeError(f"{sensor_name} must measure exactly {expected!r}, got {actual!r}")
    ids, names = robot.find_joints(list(env.cfg._scut_v14_active_joint_names), preserve_order=True)
    if tuple(names) != env.cfg._scut_v14_active_joint_names or len(ids) != 6:
        raise RuntimeError("Expected original four-leg/two-wheel active joints")
    env._scut_v14_obs_gate_config = (bool(getattr(env.cfg, "debug_value_diagnosis", False)),
                                    bool(getattr(env.cfg, "terminate_on_obs_outlier", True)),
                                    float(getattr(env.cfg, "terminate_obs_abs", 0.)),
                                    float(getattr(env.cfg, "debug_obs_alert_threshold", 120.)))
    if all(env._scut_v14_obs_gate_config[:2]) and not callable(getattr(env, "_scut_v14_raw_observation_statistics", None)):
        raise RuntimeError("Nondefault debug-enabled obs gate requires an exact cached raw-stats provider; no zero/processed-obs fallback")
    env._scut_v14_active_joint_ids = ids
    env._scut_v14_duration_counter = torch.zeros(env.num_envs, device=env.device, dtype=torch.int32)
    env._scut_v14_duration_raw = torch.zeros(env.num_envs, device=env.device, dtype=torch.bool)
    env._scut_v14_numerical_failure_mask = torch.zeros_like(env._scut_v14_duration_raw)
    env._scut_v14_value_debug_step = 0
    original_reset = env._reset_idx

    def reset_selected(self, env_ids):
        result = original_reset(env_ids)
        selected = _ids(self, env_ids)
        self._scut_v14_duration_counter[selected] = 0
        self._scut_v14_duration_raw[selected] = False
        self._scut_v14_numerical_failure_mask[selected] = False
        return result

    env._reset_idx = MethodType(reset_selected, env)
    env._scut_v14_bound = True
    return deepcopy(RECEIPT)


def set_training_iteration(env, n):
    """Parent supplies real runner iteration, including after complete checkpoint restoration."""
    env.command_manager.get_term("twist").set_training_iteration(n)


def state_dict(env):
    """Adapter-owned state plus inherited command buffers/metrics; caller saves global RNG separately."""
    if not getattr(env, "_scut_v14_bound", False):
        raise RuntimeError("bind first")
    command = env.command_manager.get_term("twist")
    clone = lambda value: _tensor(value).detach().cpu().clone()
    return {"version": 1, "task": RECEIPT["task"], "num_envs": env.num_envs,
            "training_iteration": command.training_iteration,
            "value_debug_step": env._scut_v14_value_debug_step,
            "obs_gate_config": env._scut_v14_obs_gate_config,
            "command": {name: clone(getattr(command, name)) for name in _COMMAND_BUFFERS},
            "metrics": {name: clone(value) for name, value in command.metrics.items()},
            "env": {name: clone(getattr(env, name)) for name in _ENV_BUFFERS}}


def load_state_dict(env, state):
    """Restore without reset/resampling/physics/obs computation or RNG use; restore the parent's full state too."""
    if not getattr(env, "_scut_v14_bound", False):
        raise RuntimeError("bind before adapter restoration")
    if (state["version"], state["task"], state["num_envs"]) != (1, RECEIPT["task"], env.num_envs):
        raise ValueError("Adapter checkpoint task/version/num_envs mismatch")
    if tuple(state["obs_gate_config"]) != env._scut_v14_obs_gate_config:
        raise ValueError("Adapter checkpoint observation-gate settings mismatch")
    command = env.command_manager.get_term("twist")
    for label, live in (("command", {n: getattr(command, n) for n in _COMMAND_BUFFERS}),
                        ("metrics", command.metrics), ("env", {n: getattr(env, n) for n in _ENV_BUFFERS})):
        if set(state[label]) != set(live):
            raise ValueError(f"Incomplete adapter checkpoint section {label}")
        for name, target in live.items():
            saved = _tensor(state[label][name])
            if target.shape != saved.shape or target.dtype != saved.dtype:
                raise ValueError(f"Adapter checkpoint shape/dtype mismatch: {name}")
            target.copy_(saved.to(device=target.device))
    command.set_training_iteration(state["training_iteration"])
    env._scut_v14_value_debug_step = state["value_debug_step"]
