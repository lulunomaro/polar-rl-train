"""400Hz Mod4v3Mujoco Closed-Loop RL Single-Step (200mm) Environment with Progressive DR & Zero-Tolerance Anti-Cheat.

Lightweight single-model loader (does NOT instantiate duplicate NativeGeometry on import) so multiple
environments run in a single 220 MB process via ThreadPoolExecutor with zero Windows virtual-memory pressure.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET

import mujoco as mj
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
D_BEST = REPO / 'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
PLANT = D_BEST / 'plant/MOD4v3_HW300N60_R3'
E_TEACH = REPO / 'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1'

for p_str in [str(D_BEST / 'runtime/core'), str(E_TEACH), str(E_TEACH / 'sim'), str(E_TEACH.parent)]:
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

from mod4_retarget import Mod4Retarget
from play_mod4v3 import Mod4v3Mujoco, RobotSpec, _q_from_bank, _q_from_runtime

PPO_TO_NATIVE = np.array([0, 2, 1, 3, 4, 5])
NAMES = [
    'left_front1_joint',
    'right_front1_joint',
    'left_rear1_joint',
    'right_rear1_joint',
    'left_wheel_joint',
    'right_wheel_joint',
]
PIN = '77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f'

_SHARED_CACHE: dict | None = None


def _get_shared_assets(base_step_height: float = 0.20) -> dict:
    global _SHARED_CACHE
    if _SHARED_CACHE is not None and abs(_SHARED_CACHE['height'] - base_step_height) < 1e-9:
        return _SHARED_CACHE

    original = PLANT / 'mjcf/scene.xml'
    assert hashlib.sha256(original.read_bytes()).hexdigest() == PIN
    tree = ET.parse(original)
    root = tree.getroot()
    root.find('compiler').set('meshdir', str(original.parent / 'assets'))
    base = root.find(".//body[@name='base_link']")
    ET.SubElement(base, 'site', name='native_teacher_imu', pos='0 0 0', size='.001')
    sensor = root.find('sensor')
    if sensor is None:
        sensor = ET.SubElement(root, 'sensor')
    for key, tag in [('quat', 'framequat'), ('gyro', 'gyro'), ('accel', 'accelerometer')]:
        name = 'native_teacher_' + key
        attrs = {'name': name, 'objtype': 'site', 'objname': 'native_teacher_imu'} if tag == 'framequat' else {'name': name, 'site': 'native_teacher_imu'}
        ET.SubElement(sensor, tag, **attrs)
    for side in ['left', 'right']:
        for role, joint in [('front', 'front1_joint'), ('back', 'rear1_joint'), ('wheel', 'wheel_joint')]:
            for suffix, tag in [('pos', 'jointpos'), ('vel', 'jointvel')]:
                ET.SubElement(sensor, tag, name=f'native_teacher_{side}_{role}_{suffix}', joint=f'{side}_{joint}')
    for side in ['left', 'right']:
        for role, joint in [('front', 'front1_joint'), ('rear', 'rear1_joint')]:
            ET.SubElement(sensor, 'actuatorfrc', name=f'{side}_{role}_hip_torque', actuator=f'{side}_{joint}_motor')
    if base_step_height > 0:
        ET.SubElement(
            root.find('worldbody'),
            'geom',
            name='native_teacher_platform',
            type='box',
            pos=f'{1.2 + 0.9} 0 {base_step_height / 2}',
            size=f'.9 1.1 {base_step_height / 2}',
            contype='1',
            conaffinity='2',
            friction='.9 .005 .0001',
        )

    tmp_dir = Path(tempfile.mkdtemp(prefix='mod4v3_rl_stair_'))
    xml_path = tmp_dir / 'scene.xml'
    tree.write(xml_path, encoding='utf8', xml_declaration=True)

    spec = RobotSpec(**json.loads((D_BEST / 'runtime/core/template_spec.json').read_text(encoding='utf8'))['spec'])
    runtime = json.loads((PLANT / 'runtime_config.json').read_text(encoding='utf8'))
    default = _q_from_runtime(runtime, spec.joint_names)
    bank = json.loads((D_BEST / 'plant/reset_bank.json').read_text(encoding='utf8'))
    sem = json.loads((PLANT / 'semantics.json').read_text(encoding='utf8'))
    bq, bz = _q_from_bank(bank, sem, spec.joint_names)

    ik = Mod4Retarget()
    initial_length = base_step_height + 0.2091 - 0.0625
    nom_fit_qpos = ik.fit(np.sqrt(initial_length ** 2 + ik.lateral_offset ** 2), 0.0)['qpos'].copy()
    connect_pairs = [(x.get('site1'), x.get('site2')) for x in root.findall('equality/connect')]

    _SHARED_CACHE = {
        'height': base_step_height,
        'xml_path': xml_path,
        'spec': spec,
        'default': default,
        'bq': bq,
        'bz': bz,
        'initial_length': initial_length,
        'nom_fit_qpos': nom_fit_qpos,
        'connect_pairs': connect_pairs,
    }
    return _SHARED_CACHE


class SingleStepRLEnv:
    """Closed-loop 500-step (10.0s) single-step 200mm RL environment with progressive DR and anti-cheat."""

    def __init__(self, base_step_height: float = 0.20):
        self.base_step_height = float(base_step_height)
        shared = _get_shared_assets(self.base_step_height)

        self.env = Mod4v3Mujoco(str(shared['xml_path']), shared['spec'], shared['default'], shared['bq'], shared['bz'], action_clip=6.0)
        self.m, self.d = self.env.m, self.env.d
        self.m.opt.timestep = 0.0025

        self.qa = np.array([self.m.jnt_qposadr[self.m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
        self.va = np.array([self.m.jnt_dofadr[self.m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
        self.baseline = np.r_[self.env.default_q[self.env.leg_ids].numpy(), [0.0, 0.0]][PPO_TO_NATIVE]
        self.tire = np.array([self.m.geom(s + '_tire').id for s in ['left', 'right']])
        self.bodies = self.m.geom_bodyid[self.tire]
        self.platform = self.m.geom('native_teacher_platform').id
        self.guide_geoms = np.array(
            [g for g in range(self.m.ngeom) if (self.m.geom(g).name or '').startswith('guide_wheel_')],
            dtype=int,
        )
        self.chassis_geoms = np.array(
            [
                g
                for g in range(self.m.ngeom)
                if self.m.geom_bodyid[g] == self.env.base_id and self.m.geom_contype[g] != 0
            ],
            dtype=int,
        )
        self.pairs = [(self.m.site(s1).id, self.m.site(s2).id) for s1, s2 in shared['connect_pairs']]

        self.nom_body_mass = self.m.body_mass.copy()
        self.nom_body_inertia = self.m.body_inertia.copy()
        self.nom_body_ipos = self.m.body_ipos.copy()
        self.nom_geom_friction = self.m.geom_friction.copy()
        self.nom_platform_pos = self.m.geom_pos[self.platform].copy()
        self.nom_platform_size = self.m.geom_size[self.platform].copy()

        self.initial_length = shared['initial_length']
        self.nom_fit_qpos = shared['nom_fit_qpos'].copy()

        self.dr_scale = 0.0
        self.kp_scale = 1.0
        self.kd_scale = 1.0
        self.wheel_scale = 1.0
        self.torque_limit_scale = 1.0
        self.action_delay = 0
        self.step_height = self.base_step_height
        self.rng = np.random.default_rng(0)

        self.k = 0
        self.offset_mm = 0.0
        self.prev_act = np.zeros(6, np.float32)
        self.delayed_act = np.zeros(6, np.float32)
        self.landed = False
        self.stop = False
        self.hold = 0.0
        self.best_hold = 0.0
        self.physical_hold = 0.0
        self.physical_best = 0.0
        self.entry = None
        self.approach_speed = 0.0
        self.episode_peak_speed = 0.0
        self.pitch_peak = 0.0
        self.max_closure = 0.0
        self.tilt_dwell = 0
        self.single_top_frames = 0
        self.max_x_reached = 0.0
        self.top = np.zeros(2, bool)

    def _apply_dr(self, dr_scale: float, seed: int | None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        s = float(np.clip(dr_scale, 0.0, 1.0))
        self.dr_scale = s

        if s <= 1e-8:
            self.m.body_mass[:] = self.nom_body_mass
            self.m.body_inertia[:] = self.nom_body_inertia
            self.m.body_ipos[:] = self.nom_body_ipos
            self.m.geom_friction[:] = self.nom_geom_friction
            self.m.geom_pos[self.platform] = self.nom_platform_pos
            self.m.geom_size[self.platform] = self.nom_platform_size
            self.step_height = self.base_step_height
            self.kp_scale = 1.0
            self.kd_scale = 1.0
            self.wheel_scale = 1.0
            self.torque_limit_scale = 1.0
            self.action_delay = 0
            mj.mj_setConst(self.m, self.d)
            return

        r = self.rng
        mass_scales = r.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s, size=self.m.nbody)
        mass_scales[0] = 1.0
        self.m.body_mass[:] = self.nom_body_mass * mass_scales
        self.m.body_inertia[:] = self.nom_body_inertia * mass_scales[:, None]

        self.m.body_ipos[:] = self.nom_body_ipos
        self.m.body_ipos[self.env.base_id] = self.nom_body_ipos[self.env.base_id] + r.uniform(-0.020 * s, 0.020 * s, size=3)

        fric_scale = float(r.uniform(1.0 - 0.35 * s, 1.0 + 0.25 * s))
        self.m.geom_friction[:] = self.nom_geom_friction
        for g in [*self.tire, self.platform, 0]:
            self.m.geom_friction[g, 0] = max(0.35, self.nom_geom_friction[g, 0] * fric_scale)

        dh = float(r.uniform(-0.005 * s, 0.005 * s))
        self.step_height = self.base_step_height + dh
        self.m.geom_size[self.platform, 2] = self.step_height * 0.5
        self.m.geom_pos[self.platform, 2] = self.step_height * 0.5

        self.kp_scale = float(r.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s))
        self.kd_scale = float(r.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s))
        self.wheel_scale = float(r.uniform(1.0 - 0.12 * s, 1.0 + 0.12 * s))
        self.torque_limit_scale = float(r.uniform(1.0 - 0.10 * s, 1.0 + 0.10 * s))
        self.action_delay = int(r.random() < 0.35 * s)
        mj.mj_setConst(self.m, self.d)

    def reset(self, offset_mm: float = 0.0, dr_scale: float = 0.0, seed: int | None = None) -> tuple[np.ndarray, np.ndarray]:
        self._apply_dr(dr_scale, seed)
        mj.mj_resetData(self.m, self.d)
        self.offset_mm = float(offset_mm)
        self.d.qpos[:] = self.nom_fit_qpos
        self.d.qpos[:3] = [self.offset_mm / 1000.0, 0.0, self.initial_length + 0.0625 + 0.001]
        self.d.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]
        self.d.qvel[:] = 0.0
        mj.mj_forward(self.m, self.d)

        self.k = 0
        self.prev_act = np.zeros(6, np.float32)
        self.delayed_act = np.zeros(6, np.float32)
        self.landed = False
        self.stop = False
        self.hold = 0.0
        self.best_hold = 0.0
        self.physical_hold = 0.0
        self.physical_best = 0.0
        self.entry = None
        self.approach_speed = 0.0
        self.episode_peak_speed = 0.0
        self.pitch_peak = 0.0
        self.max_closure = 0.0
        self.tilt_dwell = 0
        self.single_top_frames = 0
        self.max_x_reached = float(self.d.qpos[0])
        self.top[:] = False
        return self._get_obs(), self._get_critic_obs()

    def _get_obs(self) -> np.ndarray:
        age = self.k * 0.02
        v = 0.47 if age >= 1.0 and not self.stop else 0.0
        height = 0.20 if self.landed else (self.base_step_height + 0.2091)
        rot = self.d.xmat[self.env.base_id].reshape(3, 3)
        q = self.d.qpos[self.qa] - self.baseline
        q[4:] = 0.0
        gyro = self.d.qvel[3:6] * 0.5
        grav = rot.T @ np.array([0.0, 0.0, -1.0])
        dq = self.d.qvel[self.va] * 0.1

        if self.dr_scale > 1e-8:
            s = self.dr_scale
            gyro = gyro + self.rng.normal(0.0, 0.012 * s, size=3)
            grav = grav + self.rng.normal(0.0, 0.008 * s, size=3)
            q[:4] = q[:4] + self.rng.normal(0.0, 0.006 * s, size=4)
            dq = dq + self.rng.normal(0.0, 0.010 * s, size=6)

        return np.r_[
            [v, 0.0, 0.0, height * 5.0],
            gyro,
            grav,
            q,
            dq,
            self.prev_act,
            [0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        ].astype(np.float32)

    def _get_critic_obs(self) -> np.ndarray:
        obs35 = self._get_obs()
        wheel = self.d.geom_xpos[self.tire]
        rot = self.d.xmat[self.env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-rot[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(rot[2, 1]), float(rot[2, 2]))
        dx_edge = 1.20 - float(self.d.qpos[0])
        dw_edge = 1.20 - wheel[:, 0]
        wz = wheel[:, 2] - self.step_height
        extra = np.array(
            [
                float(self.d.qpos[0]),
                float(self.d.qpos[1]),
                float(self.d.qpos[2]),
                float(self.d.qvel[0]),
                float(self.d.qvel[1]),
                float(self.d.qvel[2]),
                pitch,
                roll,
                dx_edge,
                float(dw_edge[0]),
                float(dw_edge[1]),
                float(wz[0]),
                float(wz[1]),
                float(self.top[0]),
                float(self.top[1]),
                float(self.landed),
                float(self.stop),
                min(self.hold, 2.0),
                min(self.episode_peak_speed, 1.5),
                float(self.k) / 500.0,
                self.step_height,
                self.kp_scale - 1.0,
                self.kd_scale - 1.0,
                self.wheel_scale - 1.0,
                self.torque_limit_scale - 1.0,
                float(self.action_delay),
                self.dr_scale,
            ],
            dtype=np.float32,
        )
        pad = np.zeros(78 - 35 - len(extra), dtype=np.float32)
        return np.concatenate([obs35, extra, pad]).astype(np.float32)

    def _compute_torque_dr(self, a_nat_t: torch.Tensor) -> np.ndarray:
        if self.dr_scale <= 1e-8:
            return self.env._torque(a_nat_t).numpy().reshape(-1)
        tau = self.env._torque(a_nat_t).numpy().reshape(-1)
        tau[:4] *= self.kp_scale
        tau[4:] *= self.wheel_scale
        lim_leg = 40.0 * self.torque_limit_scale
        lim_whl = 5.775909774436091 * self.torque_limit_scale
        tau[:4] = np.clip(tau[:4], -lim_leg, lim_leg)
        tau[4:] = np.clip(tau[4:], -lim_whl, lim_whl)
        return tau

    def step(self, action_ppo: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, bool, dict]:
        a = np.clip(np.asarray(action_ppo, dtype=np.float32), -6.0, 6.0).copy()
        exec_a = self.delayed_act.copy() if (self.action_delay > 0 and self.k > 0) else a.copy()
        self.delayed_act = a.copy()

        native = exec_a[PPO_TO_NATIVE]
        a_t = torch.from_numpy(native).reshape(1, 6)
        pre_v = float(np.linalg.norm(self.d.qvel[:2]))
        pre_x = float(self.d.qpos[0])

        for j in range(8):
            tau = self._compute_torque_dr(a_t)
            if j % 4 == 0:
                self.d.ctrl[self.env.act_ids[:4]] = tau[:4]
            self.d.ctrl[self.env.act_ids[4:]] = tau[4:]
            mj.mj_step(self.m, self.d)

        self.k += 1
        age = self.k * 0.02

        if not np.isfinite(self.d.qpos).all() or not np.isfinite(self.d.qvel).all():
            self.prev_act = a
            return self._get_obs(), self._get_critic_obs(), -25.0, True, {'reason': 'nonfinite', 'success': False, 'physical_crossed': False, 'physical_stable': False, 'max_speed_m_s': 9.9, 'final_hold_s': 0.0, 'final_vx': 0.0, 'final_x': 0.0, 'pitch_peak_deg': 90.0, 'max_closure_m': 1.0, 'slid_back': False}

        closure = max(float(np.linalg.norm(self.d.site_xpos[l] - self.d.site_xpos[r])) for l, r in self.pairs)
        self.max_closure = max(self.max_closure, closure)
        if closure > 1.0:
            self.prev_act = a
            return self._get_obs(), self._get_critic_obs(), -25.0, True, {'reason': 'catastrophic_closure_above1m', 'success': False, 'physical_crossed': False, 'physical_stable': False, 'max_speed_m_s': 9.9, 'final_hold_s': 0.0, 'final_vx': 0.0, 'final_x': 0.0, 'pitch_peak_deg': 90.0, 'max_closure_m': closure, 'slid_back': False}

        self.top[:] = False
        contact = False
        guide_top = False
        chassis_hit = False
        for i in range(self.d.ncon):
            c = self.d.contact[i]
            g1, g2 = int(c.geom1), int(c.geom2)
            f = np.zeros(6)
            mj.mj_contactForce(self.m, self.d, i, f)
            if f[0] <= 5.0:
                continue
            if g1 in self.chassis_geoms or g2 in self.chassis_geoms:
                chassis_hit = True
            if self.platform not in (g1, g2):
                continue
            other = g2 if g1 == self.platform else g1
            if other in self.guide_geoms and float(c.pos[2]) > self.step_height - 0.025:
                guide_top = True
            body = self.m.geom_bodyid[other]
            for side, b in enumerate(self.bodies):
                if body != b:
                    continue
                contact = True
                normal = (1 if body == self.m.geom_bodyid[g2] else -1) * np.asarray(c.frame).reshape(3, 3)[0]
                if normal[2] > 0.7 and abs(float(c.pos[2]) - self.step_height) < 0.012:
                    self.top[side] = True

        if contact and self.entry is None:
            self.entry = pre_v

        vx = float(self.d.qvel[0])
        vy = float(self.d.qvel[1])
        speed = float(np.linalg.norm(self.d.qvel[:2]))
        rot = self.d.xmat[self.env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-rot[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(rot[2, 1]), float(rot[2, 2]))
        self.pitch_peak = max(self.pitch_peak, abs(pitch))
        wheel = self.d.geom_xpos[self.tire]

        self.episode_peak_speed = max(self.episode_peak_speed, speed)
        near = bool(np.min(np.abs(wheel[:, 0] - 1.20)) < 0.45)
        if near or self.entry is not None:
            self.approach_speed = max(self.approach_speed, speed)

        crossed = bool(self.top.all() and self.d.qpos[0] > 1.23 and np.all(wheel[:, 0] > 1.225))
        just_crossed = crossed and (not self.landed)
        self.landed |= crossed
        if self.top.any() and not self.top.all():
            self.single_top_frames += 1

        self.max_x_reached = max(self.max_x_reached, float(self.d.qpos[0]))
        slid_back = bool(
            (self.landed and (np.any(wheel[:, 2] < self.step_height + 0.0625 - 0.035) or self.d.qpos[0] < 1.15))
            or (self.single_top_frames >= 6 and np.all(wheel[:, 2] < self.step_height + 0.0625 - 0.055) and self.d.qpos[0] < 1.14)
        )

        physical_stable = bool(
            crossed
            and not slid_back
            and max(abs(pitch), abs(roll)) < math.radians(25.0)
            and np.linalg.norm(self.d.qvel[3:6]) < 1.5
            and abs(self.d.qvel[2]) < 0.25
            and speed <= 0.60
        )
        self.physical_hold = self.physical_hold + 0.02 if physical_stable else 0.0
        self.physical_best = max(self.physical_best, self.physical_hold)

        stable = bool(
            physical_stable
            and self.entry is not None
            and 0.10 <= self.entry <= 0.60
            and self.approach_speed <= 0.60
            and self.episode_peak_speed <= 0.60
        )
        self.hold = self.hold + 0.02 if stable else 0.0
        self.best_hold = max(self.best_hold, self.hold)
        if self.hold >= 0.40 - 1e-7 or self.physical_hold >= 0.40 - 1e-7:
            self.stop = True

        tilt = abs(pitch) > math.radians(40.0) or abs(roll) > math.radians(40.0)
        self.tilt_dwell = self.tilt_dwell + 1 if tilt else 0

        rew = 0.0
        da = float(np.mean((a - self.prev_act) ** 2))
        sym_err = float(np.mean((a[:2] - a[2:4]) ** 2) + 0.35 * ((a[4] - a[5]) ** 2))
        rew -= 0.015 * da + 0.025 * sym_err + 0.25 * abs(vy) + 0.20 * abs(roll)
        if chassis_hit:
            rew -= 0.80

        if speed > 0.54:
            rew -= 6.0 * (speed - 0.54)
        if speed > 0.585:
            rew -= 22.0 * (speed - 0.585)

        if age < 1.0:
            rew += 0.15 * math.exp(-((speed / 0.04) ** 2))
        elif not self.landed:
            dx = float(self.d.qpos[0]) - pre_x
            rew += 4.5 * np.clip(dx, -0.015, 0.011)
            if guide_top and vx >= 0.05 and speed <= 0.57:
                rew += 0.10
            if self.top.any() and vx >= 0.05 and speed <= 0.57:
                rew += 0.22 * float(self.top.sum())
            if just_crossed:
                rew += 8.0 if self.episode_peak_speed <= 0.59 else 2.0
        elif not self.stop:
            rew += 0.45 * math.exp(-(((vx - 0.34) / 0.14) ** 2))
            rew += 0.25 * math.exp(-((abs(pitch) / 0.22) ** 2))
            if vx < 0.05:
                rew -= 0.35
        else:
            rew += 0.55 * math.exp(-((vx / 0.035) ** 2))
            rew += 0.20 * math.exp(-(((float(self.d.qpos[0]) - 1.44) / 0.18) ** 2))
            rew += 0.15 * math.exp(-((abs(pitch) / 0.12) ** 2))
            rew -= 3.5 * abs(vx)
            if vx < -0.01:
                rew -= 10.0 * (-vx - 0.01)

        self.prev_act = a

        done = False
        reason = 'running'
        if slid_back:
            rew -= 25.0
            done = True
            reason = 'slid_off_step_regression'
        elif self.tilt_dwell >= 10:
            rew -= 15.0
            done = True
            reason = 'tilt_above40deg_for0.2s'
        elif self.d.qpos[2] < 0.11:
            rew -= 20.0
            done = True
            reason = 'fell_below_ground'
        elif abs(self.d.qpos[0]) > 3.05 or abs(self.d.qpos[1]) > 1.30:
            rew -= 12.0
            done = True
            reason = 'left_platform_scene'
        elif self.k >= 500:
            done = True
            reason = 'timeout'

        success = False
        if done:
            success = bool(self.best_hold >= 0.40 - 1e-7 and self.hold >= 0.40 - 1e-7 and self.top.all())
            if success:
                reason = 'qualified_stable_final_top_support'
                spd_margin = max(0.0, 0.60 - self.episode_peak_speed)
                rew += 18.0 + 40.0 * min(spd_margin, 0.08) + 4.0 * math.exp(-((vx / 0.03) ** 2))

        info = {
            'reason': reason,
            'success': success,
            'physical_crossed': bool(self.landed),
            'physical_stable': bool(self.physical_best >= 0.40 - 1e-7),
            'max_speed_m_s': float(self.episode_peak_speed),
            'final_hold_s': float(self.hold),
            'final_vx': vx,
            'final_x': float(self.d.qpos[0]),
            'pitch_peak_deg': math.degrees(self.pitch_peak),
            'max_closure_m': float(self.max_closure),
            'slid_back': slid_back,
        }
        return self._get_obs(), self._get_critic_obs(), float(rew), done, info
