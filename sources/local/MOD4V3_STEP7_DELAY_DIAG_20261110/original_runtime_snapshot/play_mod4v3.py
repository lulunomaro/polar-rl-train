# SPDX-License-Identifier: MIT
"""Local MuJoCo playback for the MOD4v3 SuperMimic checkpoint.

This reproduces the training-time controller:
  - official action order
  - runtime default joint pose for observations
  - 60/2 leg PD, 0.6 wheel velocity servo
  - DC voltage envelope, 8 physics substeps, 100 Hz torque refresh
  - MOD4v3 reset-bank pose
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
REPO = Path(r"D:\claude2\fangzhen\refs\supermimic_wheelbipe_20261106_repo\RadiantForever-supermimic_wheelbipe-0bf3456")
sys.path.insert(0, str(REPO))

from supermimic_wheelbipe.command import CommandLib  # noqa: E402
from supermimic_wheelbipe.mdp import MDP  # noqa: E402
from supermimic_wheelbipe.networks import Policy  # noqa: E402
from supermimic_wheelbipe.spec import RobotSpec  # noqa: E402

ACTION_CLIP = 3.0
ACTION_SCALE_LEG = 0.5
ACTION_SCALE_WHEEL = 10.0
WHEEL_VEL_LIMIT = 150.0
CONTROL_DT = 0.02
LEG_DELTA_BOUNDS = (0.17265192458887935, 1.7508937980913823)
STALL = np.array([53.333333333333336] * 4 + [28.18525375641699] * 2, dtype=np.float32)
NO_LOAD = np.array([16.755160819145562] * 4 + [55.35573187814664] * 2, dtype=np.float32)
PEAK = np.array([40.0] * 4 + [5.775909774436091] * 2, dtype=np.float32)


def _q_from_runtime(runtime: dict, names: list[str]) -> torch.Tensor:
    vals = runtime.get("initial_joint_positions", {})
    return torch.tensor([float(vals.get(n, 0.0)) for n in names], dtype=torch.float32)


def _q_from_bank(bank: dict, semantics: dict, names: list[str], root_height: float | None = None):
    rows = semantics["coordinates"]["native_from_v2"]
    poses = [p for p in bank.get("poses", []) if 0.24 <= float(p["root_height_m"]) <= 0.272]
    if not poses:
        raise RuntimeError("reset bank has no feasible poses")
    pose = poses[0] if root_height is None else min(poses, key=lambda p: abs(float(p["root_height_m"]) - root_height))
    native = {n: float(pose["joint_pos"].get(row["source"], 0.0)) + float(row["offset_si"])
              for n, row in rows.items()}
    q = torch.tensor([native.get(n, 0.0) for n in names], dtype=torch.float32)
    return q, float(pose["root_height_m"])


def _continuous_leg_target(target: torch.Tensor, current: torch.Tensor) -> torch.Tensor:
    out = target.clone()
    low, high = LEG_DELTA_BOUNDS
    for front, rear in ((0, 2), (1, 3)):
        delta = out[:, front] - out[:, rear]
        delta = delta + ((current[:, front] - current[:, rear] - delta) / (2.0 * math.pi)).round() * (2.0 * math.pi)
        delta = delta.clamp(low, high)
        hip = out[:, rear]
        hip = hip + ((current[:, rear] - hip) / (2.0 * math.pi)).round() * (2.0 * math.pi)
        out[:, rear] = hip
        out[:, front] = hip + delta
    return out


class Mod4v3Mujoco:
    def __init__(self, xml: str, spec: RobotSpec, default_q: torch.Tensor, bank_q: torch.Tensor,
                 bank_z: float, device: str = "cpu", action_clip: float = 3.0):
        self.m = mujoco.MjModel.from_xml_path(xml)
        self.d = mujoco.MjData(self.m)
        self.spec = spec
        self.device = device
        self.action_clip = float(action_clip)
        self.default_q = default_q.to(device)
        self.bank_q = bank_q.to(device)
        self.bank_z = float(bank_z)
        self.dt = float(self.m.opt.timestep)
        self.decim = max(1, int(round(CONTROL_DT / self.dt)))

        self.joint_ids = {n: int(self.m.joint(n).id) for n in spec.joint_names}
        self.qadr_all = np.array([int(self.m.jnt_qposadr[self.joint_ids[n]]) for n in spec.joint_names], dtype=np.int64)
        self.dadr_all = np.array([int(self.m.jnt_dofadr[self.joint_ids[n]]) for n in spec.joint_names], dtype=np.int64)
        self.qadr = self.qadr_all[np.asarray(spec.q_idx, dtype=np.int64)]
        self.dadr = self.dadr_all[np.asarray(spec.qd_idx, dtype=np.int64)]
        self.base_id = int(self.m.body("base_link").id)

        act = {mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(self.m.nu)}
        self.act_ids = []
        for j in spec.act_idx:
            key = spec.joint_names[j] + "_motor"
            if key not in act:
                raise RuntimeError(f"missing MJCF actuator {key}")
            self.act_ids.append(int(act[key]))
        self.act_ids = np.asarray(self.act_ids, dtype=np.int64)
        self.leg_ids = np.asarray(spec.act_leg_idx, dtype=np.int64)
        self.wheel_ids = np.asarray(spec.act_wheel_idx, dtype=np.int64)
        self.spring_ids = np.asarray(spec.spring_idx, dtype=np.int64)
        self.a_prev = torch.zeros(1, spec.na, device=device)
        self.reset()

    def reset(self):
        self.d.qpos[:] = 0.0
        self.d.qvel[:] = 0.0
        self.d.ctrl[:] = 0.0
        self.d.qpos[0:3] = (0.0, 0.0, self.bank_z)
        self.d.qpos[3:7] = (1.0, 0.0, 0.0, 0.0)
        self.d.qpos[self.qadr_all] = self.bank_q.detach().cpu().numpy()
        mujoco.mj_forward(self.m, self.d)
        self.a_prev.zero_()

    def state(self):
        d = self.d
        p = torch.tensor(d.qpos[0:3], dtype=torch.float32, device=self.device).unsqueeze(0)
        R = torch.tensor(np.array(d.xmat[self.base_id], dtype=np.float64).reshape(1, 3, 3),
                         dtype=torch.float32, device=self.device)
        v = torch.tensor(d.qvel[0:3], dtype=torch.float32, device=self.device).unsqueeze(0)
        w_b = torch.tensor(d.qvel[3:6], dtype=torch.float32, device=self.device)
        w = (R[0] @ w_b).unsqueeze(0)
        q = torch.tensor(d.qpos[self.qadr], dtype=torch.float32, device=self.device).unsqueeze(0)
        qd = torch.tensor(d.qvel[self.dadr], dtype=torch.float32, device=self.device).unsqueeze(0)
        return p, R, v, w, q, qd

    @property
    def z(self) -> float:
        return float(self.d.qpos[2])

    @property
    def cos_tilt(self) -> float:
        return float(self.d.xmat[self.base_id].reshape(3, 3)[2, 2])

    @property
    def vx(self) -> float:
        R = self.d.xmat[self.base_id].reshape(3, 3)
        fx, fy = float(R[0, 0]), float(R[1, 0])
        n = max(float(np.hypot(fx, fy)), 1e-6)
        return float((self.d.qvel[0] * fx + self.d.qvel[1] * fy) / n)

    def _torque(self, a: torch.Tensor):
        q_full = torch.tensor(self.d.qpos[self.qadr_all], dtype=torch.float32, device=self.device).unsqueeze(0)
        qd_full = torch.tensor(self.d.qvel[self.dadr_all], dtype=torch.float32, device=self.device).unsqueeze(0)
        q_leg = q_full[:, self.leg_ids]
        qd_leg = qd_full[:, self.leg_ids]
        qd_wheel = qd_full[:, self.wheel_ids]
        target = self.default_q[self.leg_ids].unsqueeze(0) + ACTION_SCALE_LEG * a[:, :4]
        target = _continuous_leg_target(target, q_leg)
        v_target = torch.clamp(ACTION_SCALE_WHEEL * a[:, 4:6], -WHEEL_VEL_LIMIT, WHEEL_VEL_LIMIT)
        raw = torch.cat((60.0 * (target - q_leg) - 2.0 * qd_leg, 0.6 * (v_target - qd_wheel)), -1)
        v_act = torch.cat((qd_leg, qd_wheel), -1)
        stall = torch.tensor(STALL, device=self.device).unsqueeze(0)
        no_load = torch.tensor(NO_LOAD, device=self.device).unsqueeze(0)
        peak = torch.tensor(PEAK, device=self.device).unsqueeze(0)
        upper = (stall * (1.0 - v_act / no_load)).clamp_min(0.0).minimum(peak)
        lower = (-stall * (1.0 + v_act / no_load)).clamp_max(0.0).maximum(-peak)
        return raw.minimum(upper).maximum(lower)

    def step(self, a: torch.Tensor):
        a = torch.clamp(a, -self.action_clip, self.action_clip)
        for j in range(self.decim):
            if j % 4 == 0:
                self.d.ctrl[self.act_ids] = self._torque(a).detach().cpu().numpy().reshape(-1)
            mujoco.mj_step(self.m, self.d)
        self.a_prev = a.detach().clamp(-self.action_clip, self.action_clip).to(self.device)
        return self.state()


def auto_cmd(t: float):
    if t < 1.0:
        return 0.0, 0.0, 0.24
    if t < 3.0:
        return 0.5, 0.0, 0.24
    if t < 5.0:
        return 0.8, 0.0, 0.26
    if t < 7.0:
        return 0.0, 2.0, 0.24
    return -0.3, 0.0, 0.24


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--xml", required=True)
    ap.add_argument("--runtime", required=True)
    ap.add_argument("--semantics", required=True)
    ap.add_argument("--bank", required=True)
    ap.add_argument("--cmd", type=float, nargs=3, default=(0.0, 0.0, 0.24), metavar=("VX", "WZ", "H"))
    ap.add_argument("--teacher", default=None, help="optional wheeled-legged_RL teacher checkpoint")
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--steps", type=int, default=0)
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--log_every", type=int, default=10)
    ap.add_argument("--term_height", type=float, default=0.18)
    a = ap.parse_args()

    torch.set_num_threads(1)
    ck = torch.load(a.ckpt, map_location=a.device)
    spec = RobotSpec(**ck["spec"])
    runtime = json.loads(Path(a.runtime).read_text(encoding="utf-8"))
    semantics = json.loads(Path(a.semantics).read_text(encoding="utf-8"))
    bank = json.loads(Path(a.bank).read_text(encoding="utf-8"))
    default_q = _q_from_runtime(runtime, spec.joint_names)
    bank_q, bank_z = _q_from_bank(bank, semantics, spec.joint_names)
    K = int(ck["args"].get("goal_frames", 10))
    Hh = int(ck["args"].get("hist", 10))
    pi = Policy(spec.nq + spec.nd + 6 + spec.na, spec.na, 4 * K, hist=Hh).to(a.device)
    pi.load_state_dict(ck["pi"])
    pi.eval()
    teacher = None
    if a.teacher:
        from supermimic_wheelbipe.teacher import Teacher
        teacher = Teacher(spec, spec.joint_names, default_q, a.teacher, device=a.device)
    cmd = CommandLib.fixed([[a.cmd[0], 0.0, a.cmd[1], a.cmd[2]]], device=a.device, frames=1000000)
    mdp = MDP(spec, cmd, kin=None, default_q=default_q, qd_limit=None)
    env = Mod4v3Mujoco(a.xml, spec, default_q, bank_q, bank_z, device=a.device)
    print(f"[play] iteration={ck.get('iteration')} xml={a.xml}")
    print(f"[play] reset bank z={bank_z:.4f} q={bank_q.tolist()}")
    print(f"[play] nq={env.m.nq} nv={env.m.nv} nu={env.m.nu} dt={env.dt*1e3:.3f}ms decim={env.decim}")

    viewer = None
    if not a.headless:
        viewer = mujoco.viewer.launch_passive(env.m, env.d)
        viewer.cam.type = 1
        viewer.cam.trackbodyid = env.base_id
        viewer.cam.distance = 1.6
        viewer.cam.azimuth = 120.0
        viewer.cam.elevation = -18.0

    hist = None
    f = 0
    t0 = time.perf_counter()
    n = 0
    n_reset = 0
    try:
        while True:
            if a.auto:
                t = n * CONTROL_DT
                vx, wz, h = auto_cmd(t)
                cmd.cmd[:] = torch.tensor([[vx, 0.0, wz, h]], dtype=torch.float32)
            S = env.state()
            o = mdp.obs(S, env.a_prev)
            hist = o.unsqueeze(1).repeat(1, Hh, 1) if hist is None else torch.cat((hist[:, 1:], o.unsqueeze(1)), 1)
            with torch.no_grad():
                if teacher is not None:
                    act = teacher.act(S, cmd.cmd[:1]).clamp(-ACTION_CLIP, ACTION_CLIP)
                else:
                    act = pi(hist, cmd.goal(torch.tensor([f % 1000000]), K)).clamp(-ACTION_CLIP, ACTION_CLIP)
            env.step(act)
            f += 1
            n += 1
            z, cos_t = env.z, env.cos_tilt
            if z < a.term_height or cos_t < 0.766 or not np.isfinite(z):
                print(f"[term] step={n} z={z:.3f} cos={cos_t:.3f} vx={env.vx:+.2f}; reset")
                env.reset()
                hist, f = None, 0
                n_reset += 1
            if n % a.log_every == 0:
                c = cmd.cmd[min(f, cmd.num_frames - 1)].detach().cpu().numpy()
                print(f"step={n:5d} z={z:.3f} cos={cos_t:.3f} vx={env.vx:+.2f} cmd={c[0]:+.2f}/{c[2]:+.2f} h={c[3]:.3f} act_max={float(act.abs().max()):.2f}")
            if viewer is not None:
                try:
                    viewer.set_texts((f"z={z:.3f} cos={cos_t:.2f} vx={env.vx:+.2f} cmd={c[0]:+.2f}/{c[2]:+.2f} h={c[3]:.2f}",))
                except Exception:
                    pass
                viewer.sync()
            if a.steps and n >= a.steps:
                break
            target_t = t0 + n * CONTROL_DT
            dt = target_t - time.perf_counter()
            if dt > 0:
                time.sleep(dt)
    except KeyboardInterrupt:
        print("interrupted")
    finally:
        if viewer is not None:
            viewer.close()
    print(f"[done] steps={n} resets={n_reset} wall={time.perf_counter()-t0:.2f}s")


if __name__ == "__main__":
    main()

