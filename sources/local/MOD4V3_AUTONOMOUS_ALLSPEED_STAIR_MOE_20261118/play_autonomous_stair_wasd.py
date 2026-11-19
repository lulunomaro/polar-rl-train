# SPDX-License-Identifier: MIT
"""Interactive Pure-WASD MuJoCo Playground for `AutonomousStairMoE` (ZERO Manual Stair Key Needed!).

Controls:
  - W / S : Increase / Decrease forward speed command (`[-0.5, +1.65] m/s`)
  - SPACE : Instant brake (`cmd_vx = 0.0`)
  - A / D : Yaw turn left / right
  - Q / E : Adjust normal cruising height (`[0.24, 0.38] m`, default `0.28m`)
  - R     : Reset at X = 0.0 m (faces `15cm -> 20cm -> 40cm` stair course)
"""
from __future__ import annotations

import os
from pathlib import Path
import time

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import mujoco as mj
import mujoco.viewer
import numpy as np
import torch

from autonomous_stair_env import Mod4v3AutonomousStairEnv, PPO_TO_NATIVE
from autonomous_stair_moe_model import HERE, AutonomousStairMoE


def main() -> None:
    torch.set_num_threads(2)
    ckpt = HERE / "weights/model_autonomous_stair_moe_best.pt"
    moe = AutonomousStairMoE.load_from_checkpoint(ckpt, device="cpu")

    env = Mod4v3AutonomousStairEnv(seed=0)
    env.reset_scenario(
        kind="stair_2step",
        dr_scale=0.0,
        step_heights=(0.20, 0.40),
        step_x1=1.60,
        tread_len=1.50,
        cmd_vx=0.0,
        height_cmd=0.28,
        max_steps=100000,
    )
    m, d = env.m, env.d

    st = {"v": 0.0, "wz": 0.0, "h": 0.28, "reset": True}

    def on_key(keycode: int) -> None:
        if keycode == 32:
            st["v"] = 0.0
        ch = chr(keycode).upper() if 32 < keycode < 127 else ""
        if ch == "W":
            st["v"] = min(1.65, round(st["v"] + 0.25, 2))
        elif ch == "S":
            st["v"] = max(-0.50, round(st["v"] - 0.25, 2))
        elif ch == "A":
            st["wz"] = 0.75
        elif ch == "D":
            st["wz"] = -0.75
        elif ch == "Q":
            st["h"] = max(0.24, round(st["h"] - 0.02, 2))
        elif ch == "E":
            st["h"] = min(0.38, round(st["h"] + 0.02, 2))
        elif ch == "R":
            st["reset"] = True

    with mujoco.viewer.launch_passive(m, d, key_callback=on_key) as viewer:
        viewer.cam.azimuth = 95.0
        viewer.cam.elevation = -15.0
        viewer.cam.distance = 2.6
        while viewer.is_running():
            t0 = time.perf_counter()
            if st["reset"]:
                st["reset"] = False
                st["v"] = 0.0
                st["wz"] = 0.0
                env.reset_scenario(
                    kind="stair_2step",
                    dr_scale=0.0,
                    step_heights=(0.20, 0.40),
                    step_x1=1.60,
                    tread_len=1.50,
                    cmd_vx=0.0,
                    height_cmd=st["h"],
                    max_steps=100000,
                )
                moe.reset_history()
                moe.history.reset(torch.from_numpy(env._get_obs()).unsqueeze(0))

            rot = d.xmat[env.env.base_id].reshape(3, 3)
            q = (d.qpos[env.qa] - env.baseline).astype(np.float32)
            q[4:] = 0.0
            obs = np.concatenate(
                (
                    np.array([st["v"], 0.0, st["wz"], st["h"] * 5.0], dtype=np.float32),
                    (d.qvel[3:6] * 0.5).astype(np.float32),
                    (rot.T @ np.array([0.0, 0.0, -1.0])).astype(np.float32),
                    q,
                    (d.qvel[env.va] * 0.1).astype(np.float32),
                    env.prev_act,
                    np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32),
                )
            )
            st["wz"] *= 0.85
            with torch.inference_mode():
                act_t, gp_t = moe.forward_with_gate(torch.from_numpy(obs))
            act = act_t.numpy()
            a_nat = torch.from_numpy(act[PPO_TO_NATIVE]).reshape(1, 6)
            for j in range(8):
                tau = env.env._torque(a_nat).numpy().reshape(-1)
                if j % 4 == 0:
                    d.ctrl[env.env.act_ids[:4]] = tau[:4]
                d.ctrl[env.env.act_ids[4:]] = tau[4:]
                mj.mj_step(m, d)
            env.prev_act = act
            viewer.cam.lookat[:] = [float(d.qpos[0]) + 0.2, float(d.qpos[1]), max(0.28, float(d.qpos[2]))]
            try:
                viewer.set_texts(
                    (
                        f"cmd_vx={st['v']:+.2f} h_cmd={st['h']:.2f} | vx={env.body_vx:+.2f} z={d.qpos[2]:.3f} | g_stair={float(gp_t):.3f}",
                    )
                )
            except Exception:
                pass
            viewer.sync()
            rem = 0.02 - (time.perf_counter() - t0)
            if rem > 0:
                time.sleep(rem)


if __name__ == "__main__":
    main()
