"""Isaac-policy to MuJoCo adapter for the closed-chain MOD4 chassis."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import mujoco
import numpy as np

from policy_runtime import OnnxPolicy


ACTION_ORDER = ("left_crank", "left_hip", "right_crank", "right_hip",
                "left_wheel_spin", "right_wheel_spin")
LEG_ORDER = ACTION_ORDER[:4]
WHEEL_ORDER = ACTION_ORDER[4:]
ACTUATOR_ORDER = ("left_hip_motor", "left_crank_motor", "left_wheel_spin_motor",
                  "right_hip_motor", "right_crank_motor", "right_wheel_spin_motor")
MODE_NAMES = ("normal", "stair", "slope", "recover", "jump", "height", "state_time")
POLICY_TERM_DIMS = (3, 1, 3, 3, 4, 2, 4, 2, 6, 7)
POLICY_FRAME_DIM = sum(POLICY_TERM_DIMS)


def pack_term_major_history(frames) -> np.ndarray:
    """Match Isaac Lab's per-term history flattening exactly.

    Each term stores its own oldest-to-newest FIFO, so a five-frame policy input is
    ``term0[t-4:t], term1[t-4:t], ...`` rather than five complete frames.
    """
    items = [np.asarray(frame, dtype=np.float32).reshape(POLICY_FRAME_DIM) for frame in frames]
    if not items:
        raise ValueError("observation history is empty")
    chunks = []
    start = 0
    for width in POLICY_TERM_DIMS:
        stop = start + width
        chunks.extend(frame[start:stop] for frame in items)
        start = stop
    return np.concatenate(chunks).astype(np.float32, copy=False)


@dataclass
class RuntimeConfig:
    leg_kp: float = 2500.0
    leg_kd: float = 10.0
    wheel_kd: float = 0.6
    crank_scale: float = 0.75
    hip_scale: float = 0.50
    wheel_scale: float = 10.0
    diff_min: float = -1.0843
    diff_max: float = 0.85
    leg_effort: float = 40.0
    leg_stall: float = 53.333333333333336
    leg_no_load: float = 16.755160819145562
    wheel_effort: float = 5.775909774436091
    wheel_stall: float = 28.18532894736838
    wheel_no_load: float = 55.3557
    policy_hz: float = 100.0
    yaw_assist_gain: float = 0.0


@dataclass
class UserCommand:
    vx: float = 0.0
    vy: float = 0.0
    wz: float = 0.0
    height: float = 0.34
    mode: int = 0
    auto_mode: bool = True

    def clamp(self):
        self.vx = float(np.clip(self.vx, -1.5, 2.8))
        self.vy = 0.0
        self.wz = float(np.clip(self.wz, -13.0, 13.0))
        self.height = float(np.clip(self.height, 0.178, 0.34))


class Mod4Sim:
    def __init__(self, xml_path: str | Path, policy_path: str | Path,
                 config: RuntimeConfig | None = None):
        self.xml_path = Path(xml_path).resolve()
        self.model = mujoco.MjModel.from_xml_path(str(self.xml_path))
        self.data = mujoco.MjData(self.model)
        self.policy = OnnxPolicy(policy_path)
        if self.policy.input_width % POLICY_FRAME_DIM:
            raise ValueError("policy input is not an integer number of 35-D frames")
        self.history_length = self.policy.input_width // POLICY_FRAME_DIM
        if self.history_length not in (1, 5):
            raise ValueError(f"unsupported policy history length: {self.history_length}")
        self.cfg = config or RuntimeConfig()
        self.command = UserCommand()
        if self.policy.manual_moe:
            self.command.auto_mode = False
        self._jump_ticks = 0
        self._jump_start_at = None
        self.last_action = np.zeros(6, dtype=np.float64)
        self.control_steps = 0
        self.max_closure_error = 0.0
        self.max_mimic_error = 0.0
        self.max_abs_torque = np.zeros(6, dtype=np.float64)
        self._push_remaining = 0
        self._push_force = np.zeros(3)
        self._observation_history = []

        expected_dt = 1.0 / self.cfg.policy_hz
        self.decimation = int(round(expected_dt / self.model.opt.timestep))
        if self.decimation < 1 or abs(self.decimation * self.model.opt.timestep - expected_dt) > 1e-9:
            raise ValueError("physics timestep is not an integer divisor of the 100 Hz policy")

        self.chassis_id = self._body("chassis")
        self.qpos = {name: self.model.jnt_qposadr[self._joint(name)] for name in ACTION_ORDER}
        self.qvel = {name: self.model.jnt_dofadr[self._joint(name)] for name in ACTION_ORDER}
        self.actuator = {name: self._actuator(name) for name in ACTUATOR_ORDER}
        self.site_pairs = tuple((self._site(a), self._site(b)) for a, b in (
            ("left_proximal_a", "left_proximal_b"), ("left_distal_a", "left_distal_b"),
            ("left_gas_end", "left_gas_mount"), ("right_proximal_a", "right_proximal_b"),
            ("right_distal_a", "right_distal_b"), ("right_gas_end", "right_gas_mount")))
        self.mimic_pairs = tuple((a, b) for a, b in (
            ("left_drive_hip_spin", "left_hip"), ("left_drive_input_spin", "left_crank"),
            ("right_drive_hip_spin", "right_hip"), ("right_drive_input_spin", "right_crank")))
        self._initial_body_mass = self.model.body_mass.copy()
        self._initial_body_inertia = self.model.body_inertia.copy()
        self._initial_friction = self.model.geom_friction.copy()
        self._initial_damping = self.model.dof_damping.copy()
        self.reset()

    def _joint(self, name):
        idx = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, name)
        if idx < 0:
            raise KeyError(f"joint missing: {name}")
        return idx

    def _actuator(self, name):
        idx = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, name)
        if idx < 0:
            raise KeyError(f"actuator missing: {name}")
        return idx

    def _body(self, name):
        idx = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, name)
        if idx < 0:
            raise KeyError(f"body missing: {name}")
        return idx

    def _site(self, name):
        idx = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, name)
        if idx < 0:
            raise KeyError(f"site missing: {name}")
        return idx

    @property
    def base_position(self):
        return self.data.qpos[:3]

    def reset(self, x=-4.0, y=0.0, yaw=0.0, ground_z=0.0):
        mujoco.mj_resetData(self.model, self.data)
        self.data.qpos[:3] = (x, y, ground_z + 0.337742301121)
        self.data.qpos[3:7] = (math.cos(yaw / 2), 0.0, 0.0, math.sin(yaw / 2))
        self.data.qvel[:] = 0.0
        self.data.ctrl[:] = 0.0
        self.data.xfrc_applied[:] = 0.0
        self.last_action[:] = 0.0
        self.control_steps = 0
        self.max_closure_error = 0.0
        self.max_mimic_error = 0.0
        self.max_abs_torque[:] = 0.0
        self.command = UserCommand()
        if self.policy.manual_moe:
            self.command.auto_mode = False
        self._jump_ticks = 0
        self._jump_start_at = None
        mujoco.mj_forward(self.model, self.data)
        self._seed_observation_history(self.observation_frame())

    def set_policy(self, policy_path: str | Path):
        """Switch policies without mixing histories from different contracts."""
        policy = OnnxPolicy(policy_path)
        if policy.input_width % POLICY_FRAME_DIM:
            raise ValueError("policy input is not an integer number of 35-D frames")
        history_length = policy.input_width // POLICY_FRAME_DIM
        if history_length not in (1, 5):
            raise ValueError(f"unsupported policy history length: {history_length}")
        self.policy = policy
        if policy.manual_moe:
            self.command.auto_mode = False
            self.cfg.yaw_assist_gain = 0.0
        self.history_length = history_length
        self.last_action[:] = 0.0
        self._seed_observation_history(self.observation_frame())

    def request_jump(self):
        """Publish the same mode4 operator request for 80 controls (0.8 s)."""
        self.command.auto_mode = False
        self.command.vx = self.command.vy = self.command.wz = 0.0
        if self.control_steps < 100:
            self.command.mode = 0
            self._jump_ticks = 0
            self._jump_start_at = 100
        else:
            self.command.mode = 4
            self._jump_ticks = 80
            self._jump_start_at = None

    def select_manual_mode(self, mode):
        self._jump_ticks = 0
        self._jump_start_at = None
        self.command.auto_mode = False
        self.command.mode = mode

    def _seed_observation_history(self, frame):
        frame = np.asarray(frame, dtype=np.float32).reshape(POLICY_FRAME_DIM)
        self._observation_history = [frame.copy() for _ in range(self.history_length)]

    def _append_observation(self, frame):
        frame = np.asarray(frame, dtype=np.float32).reshape(POLICY_FRAME_DIM)
        self._observation_history.append(frame.copy())
        del self._observation_history[:-self.history_length]

    def restore_nominal_parameters(self):
        self.model.body_mass[:] = self._initial_body_mass
        self.model.body_inertia[:] = self._initial_body_inertia
        self.model.geom_friction[:] = self._initial_friction
        self.model.dof_damping[:] = self._initial_damping
        mujoco.mj_setConst(self.model, self.data)

    def randomize(self, rng: np.random.Generator, mild=True):
        """Episode-level sim-to-sim perturbations matching the training categories."""
        self.restore_nominal_parameters()
        spread = 0.10 if mild else 0.20
        moving = np.arange(1, self.model.nbody)
        mass_scale = rng.uniform(1 - spread, 1 + spread)
        inertia_scale = rng.uniform(1 - spread, 1 + spread)
        self.model.body_mass[moving] *= mass_scale
        self.model.body_inertia[moving] *= inertia_scale
        # Contact friction on both tires, all rollers and the arena.
        friction_scale = rng.uniform(0.80 if mild else 0.60, 1.20 if mild else 1.40)
        self.model.geom_friction[:, 0] *= friction_scale
        self.model.dof_damping[:] *= rng.uniform(0.85 if mild else 0.70, 1.20 if mild else 1.40)
        mujoco.mj_setConst(self.model, self.data)
        return {"mass_scale": float(mass_scale), "inertia_scale": float(inertia_scale),
                "friction_scale": float(friction_scale)}

    def push(self, force_xyz=(0.0, 10.0, 0.0), duration_s=0.2):
        self._push_force[:] = force_xyz
        self._push_remaining = int(round(duration_s / self.model.opt.timestep))

    def _auto_task(self):
        x, y = self.base_position[:2]
        mode, height = 0, 0.34
        # Tunnel pre-crouch begins 0.40 m before its x=[1.35,1.65] roof.
        if abs(y) < 0.48 and 0.95 <= x <= 2.15:
            mode = 5
            if 0.95 <= x <= 1.75:
                height = 0.178
            else:
                height = 0.30
        elif abs(y + 2.5) < 0.8:
            mode, height = 1, 0.32
        elif abs(y - 2.5) < 0.8 or abs(y - 4.8) < 0.8:
            mode, height = 2, 0.32
        elif abs(y + 4.8) < 0.8 or (abs(x - 5.0) < 1.6 and abs(y + 3.0) < 1.2):
            mode, height = 4, 0.32
        elif abs(x - 5.0) < 1.7 and abs(y - 3.1) < 1.7:
            mode, height = 1, 0.32
        return mode, height

    def observation_frame(self):
        if self.command.auto_mode:
            mode, height = self._auto_task()
        else:
            mode, height = self.command.mode, self.command.height
        R = self.data.xmat[self.chassis_id].reshape(3, 3)
        projected_gravity = R.T @ np.array([0.0, 0.0, -1.0])
        try:
            gyro = np.asarray(self.data.sensor("base_gyro").data, dtype=np.float64).copy()
        except KeyError:
            vel = np.zeros(6)
            mujoco.mj_objectVelocity(self.model, self.data, mujoco.mjtObj.mjOBJ_BODY,
                                     self.chassis_id, vel, 1)
            gyro = vel[:3]
        leg_pos = np.array([self.data.qpos[self.qpos[n]] for n in LEG_ORDER])
        leg_vel = np.array([self.data.qvel[self.qvel[n]] for n in LEG_ORDER])
        wheel_vel = np.array([self.data.qvel[self.qvel[n]] for n in WHEEL_ORDER])
        mode_vec = np.zeros(7)
        mode_vec[int(np.clip(mode, 0, 6))] = 1.0
        obs = np.concatenate([
            np.array([self.command.vx, self.command.vy, self.command.wz]),
            np.array([height * 5.0]), gyro * 0.5, projected_gravity,
            leg_pos, np.zeros(2), leg_vel * 0.1, wheel_vel * 0.1,
            self.last_action, mode_vec,
        ]).astype(np.float32)
        if obs.shape != (35,) or not np.isfinite(obs).all():
            raise FloatingPointError(f"bad observation: shape={obs.shape}, finite={np.isfinite(obs).all()}")
        return obs

    def observation(self):
        if not self._observation_history:
            self._seed_observation_history(self.observation_frame())
        if self.history_length == 1:
            return self._observation_history[-1].copy()
        obs = pack_term_major_history(self._observation_history)
        if obs.shape != (self.policy.input_width,) or not np.isfinite(obs).all():
            raise FloatingPointError(f"bad policy observation: shape={obs.shape}")
        return obs

    @staticmethod
    def _dc_clip(raw, speed, effort, stall, no_load):
        max_effort = np.minimum(effort, stall * (1.0 - speed / no_load))
        min_effort = np.maximum(-effort, stall * (-1.0 - speed / no_load))
        # Beyond no-load speed the admissible interval can invert.  Motoring torque goes to zero,
        # while braking torque remains available in the opposite direction.
        if min_effort > max_effort:
            if speed >= 0:
                max_effort = 0.0
            else:
                min_effort = 0.0
        return float(np.clip(raw, min_effort, max_effort))

    def action_to_torque(self, action):
        a = np.clip(np.asarray(action, dtype=np.float64), -6.0, 6.0)
        target = a[:4] * np.array([self.cfg.crank_scale, self.cfg.hip_scale,
                                   self.cfg.crank_scale, self.cfg.hip_scale])
        # Project the two motor targets into the CAD input-difference stop window.
        target[0] = np.clip(target[0], target[1] + self.cfg.diff_min, target[1] + self.cfg.diff_max)
        target[2] = np.clip(target[2], target[3] + self.cfg.diff_min, target[3] + self.cfg.diff_max)
        q = np.array([self.data.qpos[self.qpos[n]] for n in LEG_ORDER])
        qd = np.array([self.data.qvel[self.qvel[n]] for n in LEG_ORDER])
        tau_leg_raw = self.cfg.leg_kp * (target - q) - self.cfg.leg_kd * qd
        tau_leg = np.array([self._dc_clip(t, v, self.cfg.leg_effort,
                                           self.cfg.leg_stall, self.cfg.leg_no_load)
                            for t, v in zip(tau_leg_raw, qd)])
        wheel_vel = np.array([self.data.qvel[self.qvel[n]] for n in WHEEL_ORDER])
        wheel_target = a[4:] * self.cfg.wheel_scale
        if self.cfg.yaw_assist_gain:
            gyro_z = float(self.data.sensor("base_gyro").data[2])
            correction = self.cfg.yaw_assist_gain * (self.command.wz - gyro_z)
            wheel_target += np.array([-correction, correction])
        tau_wheel_raw = self.cfg.wheel_kd * (wheel_target - wheel_vel)
        tau_wheel = np.array([self._dc_clip(t, v, self.cfg.wheel_effort,
                                             self.cfg.wheel_stall, self.cfg.wheel_no_load)
                              for t, v in zip(tau_wheel_raw, wheel_vel)])
        # Policy order -> MuJoCo actuator order.
        tau = np.array([tau_leg[1], tau_leg[0], tau_wheel[0],
                        tau_leg[3], tau_leg[2], tau_wheel[1]])
        return tau

    def step_control(self, observation_noise=0.0, action_delay=None):
        self._append_observation(self.observation_frame())
        obs = self.observation()
        if observation_noise:
            obs = obs + np.random.normal(0.0, observation_noise, obs.shape).astype(np.float32)
        action = self.policy(obs)
        if action_delay is not None:
            delayed = action_delay.push(action)
        else:
            delayed = action
        self.last_action[:] = np.clip(delayed, -6.0, 6.0)
        for _ in range(self.decimation):
            tau = self.action_to_torque(self.last_action)
            self.data.ctrl[:] = tau
            self.max_abs_torque = np.maximum(self.max_abs_torque, np.abs(tau))
            if self._push_remaining > 0:
                self.data.xfrc_applied[self.chassis_id, :3] = self._push_force
                self._push_remaining -= 1
            else:
                self.data.xfrc_applied[self.chassis_id] = 0.0
            mujoco.mj_step(self.model, self.data)
            if not np.isfinite(self.data.qpos).all() or not np.isfinite(self.data.qvel).all():
                raise FloatingPointError("MuJoCo state became non-finite")
        self.control_steps += 1
        if self._jump_start_at is not None and self.control_steps >= self._jump_start_at:
            self.command.mode = 4
            self._jump_ticks = 80
            self._jump_start_at = None
        elif self._jump_ticks:
            self._jump_ticks -= 1
            if self._jump_ticks == 0:
                self.command.mode = 0
        self.max_closure_error = max(self.max_closure_error, self.closure_error())
        self.max_mimic_error = max(self.max_mimic_error, self.mimic_error())
        return action

    def closure_error(self):
        return max(float(np.linalg.norm(self.data.site_xpos[a] - self.data.site_xpos[b]))
                   for a, b in self.site_pairs)

    def mimic_error(self):
        return max(abs(float(self.data.qpos[self.model.jnt_qposadr[self._joint(a)]] -
                             self.data.qpos[self.model.jnt_qposadr[self._joint(b)]]))
                   for a, b in self.mimic_pairs)

    def health(self):
        R = self.data.xmat[self.chassis_id].reshape(3, 3)
        upright_cos = float((R.T @ np.array([0.0, 0.0, -1.0]))[2] * -1.0)
        return {
            "time_s": float(self.data.time), "base_xyz": self.base_position.tolist(),
            "upright_cos": upright_cos, "closure_error_m": self.closure_error(),
            "mimic_error_rad": self.mimic_error(), "finite": bool(np.isfinite(self.data.qpos).all()),
            "max_closure_error_m": self.max_closure_error,
            "max_mimic_error_rad": self.max_mimic_error,
            "max_abs_torque_nm_actuator_order": self.max_abs_torque.tolist(),
        }


class ActionDelay:
    def __init__(self, steps=0):
        self.steps = max(0, int(steps))
        self.queue = [np.zeros(6, dtype=np.float64) for _ in range(self.steps + 1)]

    def push(self, value):
        self.queue.append(np.asarray(value, dtype=np.float64).copy())
        return self.queue.pop(0)
