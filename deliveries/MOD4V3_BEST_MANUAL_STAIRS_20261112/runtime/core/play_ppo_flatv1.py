# SPDX-License-Identifier: MIT
"""MuJoCo playback for the MOD4v3 Flat-v1 PPO actor.

This reconstructs the 35-D training observation:
  command(3), height_cmd(1), root_ang_vel_b(3), projected_gravity_b(3),
  joint_pos(6), joint_vel_leg(4), joint_vel_wheel(2), actions(6),
  ctrl_mode_obs(7).
The PPO action order is [LF, LR, RF, RR, left_wheel, right_wheel].
"""
from __future__ import annotations
import argparse
import json
import math
import sys
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np
import torch
import torch.nn as nn

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from play_mod4v3 import Mod4v3Mujoco, RobotSpec, _q_from_runtime, _q_from_bank  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_XML = ROOT / "plant/MOD4v3_HW300N60_R3/mjcf/scene.xml"
DEFAULT_RUNTIME = ROOT / "plant/MOD4v3_HW300N60_R3/runtime_config.json"
DEFAULT_SEMANTICS = ROOT / "plant/MOD4v3_HW300N60_R3/semantics.json"
DEFAULT_BANK = ROOT / "plant/reset_bank.json"
DEFAULT_TEMPLATE = HERE / "template_spec.json"
DEFAULT_CKPT = ROOT / "model/training_checkpoint.pt"
ACTION_CLIP = 3.0
CONTROL_DT = 0.02


class ActorMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(35, 256), nn.ELU(),
            nn.Linear(256, 128), nn.ELU(),
            nn.Linear(128, 64), nn.ELU(),
            nn.Linear(64, 6),
        )

    def forward(self, x):
        return self.mlp(x)


def _map(values, names, order):
    return torch.stack([values[names.index(n)] for n in order], 0)


def _auto_cmd(t):
    if t < 2.0:
        return 0.0, 0.0, 0.28
    if t < 5.0:
        return 0.35, 0.0, 0.28
    if t < 8.0:
        return 0.65, 0.0, 0.30
    if t < 11.0:
        return 0.0, 1.2, 0.28
    if t < 14.0:
        return 0.45, 0.0, 0.30
    return 0.0, 0.0, 0.28


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=str(DEFAULT_CKPT))
    ap.add_argument("--xml", default=str(DEFAULT_XML))
    ap.add_argument("--runtime", default=str(DEFAULT_RUNTIME))
    ap.add_argument("--semantics", default=str(DEFAULT_SEMANTICS))
    ap.add_argument("--bank", default=str(DEFAULT_BANK))
    ap.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="SuperMimic checkpoint used only for RobotSpec")
    ap.add_argument("--cmd", type=float, nargs=3, default=(0.0, 0.0, 0.28), metavar=("VX", "WZ", "H"))
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--air-start", action="store_true")
    ap.add_argument("--air-height", type=float, default=0.42)
    ap.add_argument("--steps", type=int, default=0)
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--log_every", type=int, default=10)
    ap.add_argument("--term_height", type=float, default=0.18)
    a = ap.parse_args()

    torch.set_num_threads(1)
    ck = torch.load(a.ckpt, map_location=a.device, weights_only=False)
    template = torch.load(a.template, map_location="cpu", weights_only=False)
    spec = RobotSpec(**template["spec"])
    runtime = json.loads(Path(a.runtime).read_text(encoding="utf-8"))
    semantics = json.loads(Path(a.semantics).read_text(encoding="utf-8"))
    bank = json.loads(Path(a.bank).read_text(encoding="utf-8"))
    default_q = _q_from_runtime(runtime, spec.joint_names)
    bank_q, bank_z = _q_from_bank(bank, semantics, spec.joint_names)
    order = list(ck["action_order"])
    if order != ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint", "left_wheel_joint", "right_wheel_joint"]:
        raise ValueError(f"unexpected PPO action order: {order}")

    actor = ActorMLP().to(a.device)
    actor.load_state_dict(ck["actor_state_dict"], strict=False)
    actor.eval()

    env = Mod4v3Mujoco(a.xml, spec, default_q, bank_q, bank_z, device=a.device)
    # Convert PPO order [LF,LR,RF,RR,LW,RW] to the MJCF/spec order
    # [LF,RF,LR,RR,LW,RW] only at the environment boundary.
    ppo_to_env = torch.tensor([0, 2, 1, 3, 4, 5], dtype=torch.long, device=a.device)
    active_names = order
    default_active = _map(default_q, spec.joint_names, active_names).to(a.device)

    def current_active():
        q_all = torch.tensor(env.d.qpos[env.qadr_all], dtype=torch.float32, device=a.device)
        qd_all = torch.tensor(env.d.qvel[env.dadr_all], dtype=torch.float32, device=a.device)
        return _map(q_all, spec.joint_names, active_names), _map(qd_all, spec.joint_names, active_names)

    def set_air_start():
        env.reset()
        env.d.qpos[2] = float(a.air_height)
        mujoco.mj_forward(env.m, env.d)

    if a.air_start:
        set_air_start()

    viewer = None
    if not a.headless:
        viewer = mujoco.viewer.launch_passive(env.m, env.d)
        viewer.cam.type = 1
        viewer.cam.trackbodyid = env.base_id
        viewer.cam.distance = 1.8
        viewer.cam.azimuth = 120.0
        viewer.cam.elevation = -18.0

    a_prev = torch.zeros(1, 6, device=a.device)
    n = 0
    t0 = time.perf_counter()
    try:
        while True:
            t = n * CONTROL_DT
            if a.auto:
                vx, wz, h = _auto_cmd(t)
            else:
                vx, wz, h = a.cmd
            q, qd = current_active()
            R = torch.tensor(np.array(env.d.xmat[env.base_id], dtype=np.float64).reshape(3, 3), dtype=torch.float32)
            gravity_b = R.T @ torch.tensor([0.0, 0.0, -1.0], dtype=torch.float32)
            root_ang_vel_b = torch.tensor(env.d.qvel[3:6], dtype=torch.float32)
            joint_pos = q - default_active
            joint_pos[4:] = 0.0  # training mutes wheel position observations
            mode = torch.zeros(7, dtype=torch.float32)
            mode[0] = 1.0
            obs = torch.cat((
                torch.tensor([vx, 0.0, wz], dtype=torch.float32),
                torch.tensor([h * 5.0], dtype=torch.float32),  # training obs scale
                root_ang_vel_b * 0.5,
                gravity_b,
                joint_pos,
                qd[:4] * 0.1,
                qd[4:] * 0.1,
                a_prev[0],
                mode * torch.tensor([1, 1, 1, 1, 1, 5, 1], dtype=torch.float32),
            ), 0).unsqueeze(0).to(a.device)
            with torch.no_grad():
                a_ppo = actor(obs).clamp(-ACTION_CLIP, ACTION_CLIP)
            a_env = a_ppo[:, ppo_to_env]
            env.step(a_env)
            a_prev = a_ppo.detach()
            n += 1
            z, cos_t = env.z, env.cos_tilt
            if z < a.term_height or cos_t < 0.766 or not np.isfinite(z):
                print(f"[term] step={n} z={z:.3f} cos={cos_t:.3f}; reset")
                if a.air_start:
                    set_air_start()
                else:
                    env.reset()
                a_prev.zero_()
            if n % a.log_every == 0:
                print(f"step={n:5d} z={z:.3f} cos={cos_t:.3f} vx={env.vx:+.2f} cmd={vx:+.2f}/{wz:+.2f} h={h:.2f} act_max={float(a_ppo.abs().max()):.2f}")
            if viewer is not None:
                try:
                    viewer.set_texts((f"z={z:.3f} cos={cos_t:.2f} vx={env.vx:+.2f} cmd={vx:+.2f}/{wz:+.2f} h={h:.2f}",))
                except Exception:
                    pass
                viewer.sync()
            if a.steps and n >= a.steps:
                break
            target = t0 + n * CONTROL_DT
            delay = target - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
    except KeyboardInterrupt:
        print("interrupted")
    finally:
        if viewer is not None:
            viewer.close()
    print(f"[done] steps={n} wall={time.perf_counter()-t0:.2f}s")


if __name__ == "__main__":
    main()

