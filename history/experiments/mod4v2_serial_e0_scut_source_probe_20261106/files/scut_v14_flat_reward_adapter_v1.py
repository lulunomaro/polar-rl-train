"""SCUT Robotics-Wheelbipe-V14-Flat-v0 rewards only; MOD4 mechanical mapping.
ABI: configure(cfg, task_module) BEFORE env construction; env.reset() once using
its existing startup path; bind(env) BEFORE the first step. No launch/stage code.
Source-derived, AST-only checked: no SDK/tensor/simulator execution validation.
Commands, dones, reset distribution, DR and actor35/critic38 remain caller-owned;
upstream critic78 is NOT transplanted. No learner/norm/Adam/LR/STD changes here.
"""
from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
from types import MethodType

UPSTREAM = "C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL"
TASK_SOURCE = "F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/e0_hour_actual_recipe_sources/mod4_task.py"
SDK_SOURCE = "F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/sdk_scut_alignment_abi_source_v1"
WB = UPSTREAM + "/source/agent_tasks/agent_tasks/direct/wheelbipe"
SOURCE_REFERENCES = {
    "registration": WB + "/wheelbipe_V14/__init__.py:17-25",
    "flat_parameters_weights": WB + "/wheelbipe_V14/env_cfg.py:737-757,834-914",
    "inherited_parameters": WB + "/wheelbipe25_v3/env_cfg.py:333-334,388-398,473-488",
    "flat_no_state_machine": WB + "/wheelbipe_V14/cfg_utils.py:749-766",
    "physical_state_and_raw_actions": WB + "/wheelbipe25_v3/env.py:2135-2136,2811-2837",
    "action_history_observation_reset": WB + "/wheelbipe25_v3/env.py:3100-3108,5030-5058",
    "regularization": WB + "/wheelbipe25_v3/env.py:3501-3582",
    "orientation_tracking_nofork_height": WB + "/wheelbipe25_v3/env.py:3584-3600,3690-3833",
    "contact_history": WB + "/wheelbipe25_v3/env.py:3905-3937",
    "weight_sanitize_sum": WB + "/wheelbipe25_v3/env.py:3998-4019,4054-4063",
    "numerical_reward_mask": WB + "/wheelbipe25_v3/env.py:4924-4947",
    "absolute_height_target": WB + "/wheelbipe25_v3/env.py:512-549,1730-1742",
    "source_contact_body_groups": WB + "/wheelbipe_V14/env.py:118-130",
    "ppo_inheritance": WB + "/agents/rsl_rl_ppo_cfg.py:26-51,208-270",
    "mod4_joint_body_contract": TASK_SOURCE + ":105-116,245-247,1284-1293",
    "mod4_height_buffer": TASK_SOURCE + ":418-424",
    "mod4_sensor_prim_layout": TASK_SOURCE + ":1150-1168",
    "sdk_compute_reset": SDK_SOURCE + "/managers/reward_manager.py:101-159,217-247",
    "sdk_step_order": SDK_SOURCE + "/envs/manager_based_rl_env.py:231-270,377-407",
    "sdk_raw_action_order": SDK_SOURCE + "/managers/action_manager.py:256-259,344-387",
}
SDK_SHA256 = {
    "reward_compute": "6be44a98df5aed8a0ebac2913ebea33010633e007e816697a6d99f7ccfd731db",
    "env_step": "a963cfcdb4cd60955cd022ed709d27c99a6935685b69180bb29d74f8983f6566",
    "action_process": "2facb9eaee7722509603b0794c57bf760f8b6eb7290830d4899b413bbd40109d",
}
STEP_DT = 0.02
SENSOR_NAME = "scut_v14_reward_contacts"
STATE_NAME = "_scut_v14_flat_reward_v1"
LEGS = ("left_crank", "left_hip", "right_crank", "right_hip")
WHEELS = ("left_wheel_spin", "right_wheel_spin")
WHEEL_BODIES = ("left_wheel", "right_wheel")
# Original OrderedDict order, INCLUDING explicit zero keys. No other rewards.
REWARD_WEIGHTS = {
    "termination": -200., "leg_joint_acc": -5e-7, "leg_joint_vel": -5.0e-3,
    "leg_joint_pair_pos_diff": -0.0, "joint_torque": -1e-4,
    "wheel_acc": -1e-8, "wheel_vel": -1e-5, "wheel_power": -1e-4,
    "wheel_air_spin": 0., "lin_vel_z": -0.5, "ang_vel_xy": -0.05,
    "action_smoothness_leg": -0.05, "action_rate": -0.01,
    "action_smoothness_wheel": -0.01, "flat_orientation_y": -0.0,
    "flat_orientation_y_v": -2.0, "flat_orientation_y_exp": 1.0,
    "flat_orientation_x": -0.0, "flat_orientation_x_v": -2.0,
    "flat_orientation_x_exp": 1.0, "track_lin_vel_xy": 1.0,
    "track_lin_vel_xy_tight": 0.0, "track_lin_vel_xy_square": -1.0,
    "track_ang_vel_z": 1.0, "track_ang_vel_z_square": -1.0,
    "stand_still_lin_vel": -1.0, "stand_still": -0.0,
    "track_height_exp": 0.0, "track_height_exp_soft": 0.0,
    "track_height_exp_tight": 1.0, "track_height_square": -1.0,
    "track_height_exp_both_wheels_contact": 0.0, "no_fork": -1.0,
    "no_fork_square": -1.0, "no_fork_exp": -0.0,
    "no_fork_z_exp": -0.0, "undesired_contact": -2.0,
}
ACTIVE_WEIGHTS = {k: w for k, w in REWARD_WEIGHTS.items() if w != 0.0}
# Source defaults for the caller's explicit PPO alignment, NOT applied here.
EXPECTED_PPO_ALGORITHM = {
    "value_loss_coef": 4.0, "use_clipped_value_loss": True, "clip_param": 0.2,
    "entropy_coef": 0.005, "num_learning_epochs": 5, "num_mini_batches": 4,
    "learning_rate": 1.0e-4, "schedule": "adaptive", "gamma": 0.99,
    "lam": 0.95, "desired_kl": 0.01, "max_grad_norm": 1.0,
}
PENDING_ELSEWHERE = (
    "SCUT special-mode commands, heading/deadzone command generation and height sampling",
    "SCUT timeout/contact/40deg persistent20-step dones, numerical immediate termination",
    "SCUT predefined reset distribution, zero-torque/start-reset phases and DR",
    "explicit PPO gamma/lam/value/etc alignment while preserving learned STD/current LR",
    "A0 actor35/critic38 retained versus upstream35/78: interface difference unresolved",
    "runtime admission and tensor/SDK verification; this module is not a runtime PASS",
)


class Unknown(RuntimeError):
    """Required source/SDK/physical mapping is absent or different; never fill zero."""


def _need(obj, name):
    value = getattr(obj, name, None)
    if value is None:
        raise Unknown("Required field missing: " + type(obj).__name__ + "." + name)
    return value


def _item(mapping, name):
    try:
        value = mapping[name]
    except (KeyError, IndexError, TypeError) as error:
        raise Unknown("Required named item missing: " + str(name)) from error
    if value is None:
        raise Unknown("Required named item is None: " + str(name))
    return value


def _source_sha(callable_object, key):
    try:
        filename = inspect.getsourcefile(callable_object)
        digest = None if filename is None else hashlib.sha256(Path(filename).read_bytes()).hexdigest()
    except (OSError, TypeError) as error:
        raise Unknown("SDK source unreadable for " + key) from error
    if digest != SDK_SHA256[key]:
        raise Unknown("Unverified SDK source/order for " + key + ": " + str(filename))


def _raw_term(env, name):
    state = _need(env, STATE_NAME)
    if state.raw is None:
        raise Unknown("Reward terms require bind(env)'s compute hook")
    return state.raw[name]


def configure(cfg, task_module):
    """Replace ALL old rewards prebuild, install needed contact sensor, return spec.

    Caller must explicitly supply the .02s control clock; no physics, command,
    done, reset or DR configuration is silently rewritten to satisfy it.
    """
    if getattr(cfg, STATE_NAME, None) is not None:
        raise Unknown("configure called twice")
    dt = float(_need(_need(cfg, "sim"), "dt")) * int(_need(cfg, "decimation"))
    if abs(dt - STEP_DT) > 1e-10:
        raise Unknown("SCUT rewards require caller-owned step_dt=.02; received " + str(dt))
    if tuple(_need(task_module, "LEG_ORDER")) != LEGS or tuple(_need(task_module, "WHEEL_ORDER")) != WHEELS:
        raise Unknown("MOD4 active-motor/action order changed")
    bodies = tuple(_item(_need(task_module, "CONTRACT"), "bodies"))
    guides = tuple(b for b in bodies if b.startswith("guide_roller_"))
    limbs = tuple(b for b in bodies if b.startswith(("left_", "right_")) and b not in WHEEL_BODIES)
    mapped = ("chassis",) + limbs + guides
    if not guides or not limbs or set(mapped + WHEEL_BODIES) != set(bodies):
        raise Unknown("MOD4 base/leg/guide body map is incomplete or includes unknown bodies")
    if set(_need(task_module, "LIMB_BODIES")) != set(limbs + guides):
        raise Unknown("Task limb/guide contract disagrees with explicit mechanical map")
    if tuple(_need(task_module, "WHEEL_BODIES")) != WHEEL_BODIES:
        raise Unknown("Unknown wheel rigid-body mapping")
    scene = _need(cfg, "scene")
    if getattr(scene, SENSOR_NAME, None) is not None:
        raise Unknown("Reward contact sensor already exists")
    # New net-force sensor, not chassis-only / filtered / current-force fallback.
    scene_sensor = _need(task_module, "ContactSensorCfg")(
        prim_path="{ENV_REGEX_NS}/Robot/links/.*", history_length=3,
        update_period=0.005, track_air_time=True, debug_vis=False)
    old = _need(cfg, "rewards")
    removed = tuple(old if isinstance(old, dict) else vars(old))
    rewards = {k: _need(task_module, "RewTerm")(
        func=_raw_term, weight=w, params={"name": k}) for k, w in ACTIVE_WEIGHTS.items()}
    spec = {
        "abi": "SCUT_V14_FLAT_REWARD_V1", "task": "Robotics-Wheelbipe-V14-Flat-v0",
        "step_dt": STEP_DT, "removed_reward_names": removed,
        "all_weights_in_source_order": dict(REWARD_WEIGHTS),
        "explicit_zero_keys_not_evaluated": tuple(k for k, w in REWARD_WEIGHTS.items() if w == 0),
        "contact_map": {"base_link": ("chassis",), "rear/front_leg_links": limbs,
                        "guide_links": guides, "gimbal_yaw_link": (), "gimbal_pitch_link": ()},
        "gimbal_note": "MOD4 has no gimbal; absent by explicit mechanical mapping, not zero force",
        "all_contract_bodies": bodies, "undesired_bodies": mapped,
        "pending_elsewhere": PENDING_ELSEWHERE, "source_references": dict(SOURCE_REFERENCES),
        "ppo_dictionary_applied": False, "learned_std_current_lr_preserved": True,
        "runtime_validated": False,
    }
    setattr(scene, SENSOR_NAME, scene_sensor)
    cfg.rewards = rewards
    setattr(cfg, STATE_NAME, spec)
    return spec


class _RewardState:
    def __init__(self, env, spec):
        import torch
        try:
            from isaaclab.utils.math import euler_xyz_from_quat, quat_apply_inverse, wrap_to_pi
        except ImportError as error:
            raise Unknown("Required SDK quaternion operations absent") from error
        self.t, self.env, self.spec = torch, env, spec
        self.euler, self.qinv_apply, self.wrap = euler_xyz_from_quat, quat_apply_inverse, wrap_to_pi
        self.robot = _item(_need(env, "scene"), "robot")
        self.sensor = _item(env.scene, SENSOR_NAME)
        self.manager = _need(env, "reward_manager")
        names = list(_need(self.robot, "joint_names"))
        if any(names.count(n) != 1 for n in LEGS + WHEELS):
            raise Unknown("Missing/duplicate active leg or wheel joint")
        self.leg = [names.index(n) for n in LEGS]
        self.wheel = [names.index(n) for n in WHEELS]
        self.active = self.leg + self.wheel
        body_names = list(_need(self.robot, "body_names"))
        sensor_names = list(_need(self.sensor, "body_names"))
        if set(body_names) != set(spec["all_contract_bodies"]):
            raise Unknown("Articulation rigid bodies differ from task contract")
        if any(sensor_names.count(n) != 1 for n in spec["undesired_bodies"]):
            raise Unknown("Contact sensor lacks named base/leg/guide bodies; no fallback")
        self.contact_ids = [sensor_names.index(n) for n in spec["undesired_bodies"]]
        self.wheel_body = [body_names.index(n) for n in WHEEL_BODIES]
        sensor_cfg = _need(self.sensor, "cfg")
        if sensor_cfg.history_length != 3 or abs(sensor_cfg.update_period - .005) > 1e-10:
            raise Unknown("SCUT contact history must be three .005s samples")
        action_manager = _need(env, "action_manager")
        if tuple(action_manager.active_terms) != ("legs", "wheels") or list(action_manager.action_term_dim) != [4, 2]:
            raise Unknown("Required raw action ABI is legs4 followed by wheels2")
        for key, expected in (("legs", LEGS), ("wheels", WHEELS)):
            term_cfg = _need(_item(_need(action_manager, "_terms"), key), "cfg")
            if tuple(_need(term_cfg, "joint_names")) != expected or not _need(term_cfg, "preserve_order"):
                raise Unknown("Action joint permutation changed: " + key)
        if bool(torch.any(_need(env, "episode_length_buf") != 0)):
            raise Unknown("bind must follow initial reset and precede the first step")
        self.prev = torch.zeros_like(_need(action_manager, "action"))
        if tuple(self.prev.shape) != (env.num_envs, 6):
            raise Unknown("Raw action tensor must have shape [num_envs,6]")
        self.prevprev = torch.zeros_like(self.prev)
        self.last_step = int(_need(env, "common_step_counter"))
        self.raw = None
        self.last_weighted_terms = None
        self.numeric_bad = None
        self.original_compute, self.original_reset = self.manager.compute, self.manager.reset
        self._inputs()  # Required fields only: no observation/command/RNG/physics calls.

    def _inputs(self):
        t, env = self.t, self.env
        data = _need(self.robot, "data")
        fields = {k: _need(data, k) for k in (
            "joint_acc", "joint_vel", "applied_torque", "root_lin_vel_b", "root_ang_vel_b",
            "projected_gravity_b", "root_pos_w", "root_quat_w", "body_pos_w")}
        n, j, b = env.num_envs, len(self.robot.joint_names), len(self.robot.body_names)
        shapes = {"joint_acc": (n, j), "joint_vel": (n, j), "applied_torque": (n, j),
                  "root_lin_vel_b": (n, 3), "root_ang_vel_b": (n, 3),
                  "projected_gravity_b": (n, 3), "root_pos_w": (n, 3),
                  "root_quat_w": (n, 4), "body_pos_w": (n, b, 3)}
        for key, value in fields.items():
            if not isinstance(value, t.Tensor) or tuple(value.shape) != shapes[key]:
                raise Unknown("Unexpected robot tensor shape: " + key)
        try:
            command = _need(_need(env, "command_manager"), "get_command")("twist")
        except KeyError as error:
            raise Unknown("Required unscaled twist command is absent") from error
        height = _need(env, "_mod4_height_cmd")
        forces = _need(_need(self.sensor, "data"), "net_forces_w_history")
        if not isinstance(command, t.Tensor) or tuple(command.shape) != (env.num_envs, 3):
            raise Unknown("Unscaled twist command [N,3] required")
        if not isinstance(height, t.Tensor) or tuple(height.shape) != (env.num_envs, 1):
            raise Unknown("Initialized unscaled MOD4 absolute height command [N,1] required")
        if not isinstance(forces, t.Tensor) or tuple(forces.shape) != (env.num_envs, 3, len(self.sensor.body_names), 3):
            raise Unknown("Net force history ABI [N,history3,bodies,xyz] required")
        terminated = _need(env, "reset_terminated")
        if tuple(terminated.shape) != (env.num_envs,) or terminated.dtype != t.bool:
            raise Unknown("Fresh termination mask required before reward computation")
        return fields, command, height[:, 0], forces, terminated

    def build_raw(self):
        t, env = self.t, self.env
        d, cmd, height, forces, terminated = self._inputs()
        v, omega = d["root_lin_vel_b"], d["root_ang_vel_b"]
        jv, ja, torque = d["joint_vel"], d["joint_acc"], d["applied_torque"]
        action = env.action_manager.action
        delta2 = action - 2 * self.prev + self.prevprev
        stand = t.abs(cmd[:, 0]) < .1
        yaw_stand = t.abs(cmd[:, 2]) < .1
        tracking = cmd.clone()
        tracking[stand, 0], tracking[yaw_stand, 2] = 0.0, 0.0
        gx, gy = d["projected_gravity_b"][:, 0], d["projected_gravity_b"][:, 1]
        gain = 2. * t.exp(-t.square(cmd[:, 0]) / 3.) + 2.
        pitch = self.wrap(self.euler(d["root_quat_w"])[1])
        ev = tracking[:, 0] - v[:, 0] * t.cos(pitch)
        ew = tracking[:, 2] - omega[:, 2]
        eh = d["root_pos_w"][:, 2] - height  # absolute world z, NO terrain subtraction/height clip
        rel = d["body_pos_w"][:, self.wheel_body] - d["root_pos_w"][:, None, :]
        quat = d["root_quat_w"][:, None, :].expand(-1, 2, -1)
        wheel_b = self.qinv_apply(quat.reshape(-1, 4), rel.reshape(-1, 3)).reshape(-1, 2, 3)
        dx = wheel_b[:, 0, 0] - wheel_b[:, 1, 0]
        contact = t.linalg.vector_norm(forces[:, :, self.contact_ids], dim=-1) > 3.
        raw = {
            "termination": terminated.float(),
            "leg_joint_acc": t.square(ja[:, self.leg]).sum(-1),
            "leg_joint_vel": t.square(jv[:, self.leg]).sum(-1),
            "joint_torque": t.square(torque[:, self.active]).sum(-1),
            "wheel_acc": t.square(ja[:, self.wheel]).sum(-1),
            "wheel_vel": t.square(jv[:, self.wheel]).sum(-1),
            "wheel_power": t.clamp(torque[:, self.wheel] * jv[:, self.wheel], min=0).sum(-1),
            "lin_vel_z": t.square(v[:, 2]), "ang_vel_xy": t.square(omega[:, :2]).sum(-1),
            "action_smoothness_leg": t.square(delta2[:, :4]).sum(-1),
            "action_rate": t.square(action - self.prev).sum(-1),
            "action_smoothness_wheel": t.square(delta2[:, 4:6]).sum(-1),
            "flat_orientation_y_v": t.square(gain * gx),
            "flat_orientation_y_exp": t.exp(-t.square(gx) / .02),
            "flat_orientation_x_v": t.square(gain * gy),
            "flat_orientation_x_exp": t.exp(-t.square(gy) / .01),
            "track_lin_vel_xy": t.exp(-t.square(t.clamp(ev, -1., 1.)) / .5),
            "track_lin_vel_xy_square": t.square(ev * .25),
            "track_ang_vel_z": t.exp(-t.square(t.clamp(ew, -.8, .8)) / .25),
            "track_ang_vel_z_square": t.square(ew * .5),
            "stand_still_lin_vel": t.abs(v[:, :2]).sum(-1) * stand.float(),
            "track_height_exp_tight": t.exp(-t.square(t.clamp(eh, -.15, .15)) / .001),
            "track_height_square": t.square(10. * eh),
            "no_fork": (t.abs(dx) > .05).float(), "no_fork_square": t.square(dx * 5.),
            "undesired_contact": t.max(t.max(contact, dim=1)[0], dim=1)[0].float(),
        }
        # Exact upstream numerical reward mask, NOT a new done or obs-outlier rule.
        self.numeric_bad = (
            ~t.isfinite(jv[:, self.active]).all(-1) | ~t.isfinite(v).all(-1)
            | ~t.isfinite(omega).all(-1) | (t.abs(jv[:, self.active]).amax(-1) > 500.)
            | (t.abs(omega).amax(-1) > 200.) | (t.abs(v).amax(-1) > 100.))
        return raw, action

    def compute(self, manager, dt):
        t, env = self.t, self.env
        if abs(float(dt) - STEP_DT) > 1e-10 or abs(float(env.step_dt) - STEP_DT) > 1e-10:
            raise Unknown("Control dt changed from .02")
        step = int(env.common_step_counter)
        if step != self.last_step + 1:
            raise Unknown("Reward compute must occur exactly once after each physics step")
        if tuple(manager._term_names) != tuple(ACTIVE_WEIGHTS):
            raise Unknown("Extra/missing/reordered rewards injected after configure")
        self.raw, action = self.build_raw()
        zero = t.zeros(env.num_envs, device=env.device)
        weighted = {}
        keep = (~self.numeric_bad).float()
        # Match SCUT operation order, sanitization, zero slots and reduction order.
        for name, weight in REWARD_WEIGHTS.items():
            value = (self.raw[name] * dt) * weight if weight != 0.0 else zero
            weighted[name] = t.nan_to_num(value, nan=0., posinf=0., neginf=0.) * keep
        for i, (name, cfg) in enumerate(zip(manager._term_names, manager._term_cfgs)):
            if cfg.func is not _raw_term or cfg.weight != ACTIVE_WEIGHTS[name] or cfg.params != {"name": name}:
                raise Unknown("Reward configuration mutated: " + name)
            value = weighted[name]
            manager._episode_sums[name] += value
            manager._step_reward[:, i] = value / dt
        total = t.stack(list(weighted.values()), dim=-1).sum(dim=-1)
        manager._reward_buf.copy_(t.nan_to_num(total, nan=0., posinf=0., neginf=0.))
        self.last_weighted_terms = {k: v.detach() for k, v in weighted.items()}
        # Same next-reward history as upstream reward -> reset -> observations.
        # No observation callback, noise/delay update, RNG or physics invocation.
        self.prevprev.copy_(self.prev)
        self.prev.copy_(action.detach())
        self.last_step = step
        return manager._reward_buf

    def reset(self, manager, env_ids=None):
        result = self.original_reset(env_ids=env_ids)  # Preserve SDK stats/reset contract.
        ids = slice(None) if env_ids is None else env_ids
        self.prev[ids] = 0.
        self.prevprev[ids] = 0.
        self.raw = None
        return result


def bind(env):
    """Install reward-only compute/reset hooks; return source/ABI receipt, not PASS."""
    if getattr(env, STATE_NAME, None) is not None:
        raise Unknown("Reward adapter already bound")
    spec = _need(_need(env, "cfg"), STATE_NAME)
    manager = _need(env, "reward_manager")
    _source_sha(manager.compute, "reward_compute")
    _source_sha(env.step, "env_step")  # Unknown subclass step order is not guessed.
    _source_sha(env.action_manager.process_action, "action_process")
    if abs(float(env.step_dt) - STEP_DT) > 1e-10:
        raise Unknown("bind requires .02s control dt")
    if tuple(manager.active_terms) != tuple(ACTIVE_WEIGHTS):
        raise Unknown("configure must replace all old reward terms BEFORE env construction")
    for name in ("_term_names", "_term_cfgs", "_reward_buf", "_step_reward", "_episode_sums"):
        _need(manager, name)
    if len(manager._term_cfgs) != len(ACTIVE_WEIGHTS):
        raise Unknown("Reward manager term cfg length differs from active terms")
    if tuple(manager._reward_buf.shape) != (env.num_envs,) or tuple(manager._step_reward.shape) != (env.num_envs, len(ACTIVE_WEIGHTS)):
        raise Unknown("Reward manager statistical tensor ABI changed")
    state = _RewardState(env, spec)
    setattr(env, STATE_NAME, state)
    manager.compute = MethodType(lambda mgr, dt: state.compute(mgr, dt), manager)
    manager.reset = MethodType(lambda mgr, env_ids=None: state.reset(mgr, env_ids), manager)
    return {
        "abi": spec["abi"], "active_weights": dict(ACTIVE_WEIGHTS),
        "explicit_zero_keys": spec["explicit_zero_keys_not_evaluated"],
        "operation_order": "(raw*.02)*weight -> per-term finite sanitize -> numerical-env zero -> source-order stack sum",
        "only_positive": False, "source_sha256": dict(SDK_SHA256),
        "memory": "raw input actions; legs4/wheels2; prevprev advances once after reward; reset clears selected rows",
        "contact": "net_forces_w_history[N,3,B,3], any(history, mapped base/legs/guide), norm>3N",
        "mechanical_mapping": spec["contact_map"], "pending_elsewhere": PENDING_ELSEWHERE,
        "runtime_validated": False, "learner_network_norm_optimizer_lr_std_modified": False,
    }
