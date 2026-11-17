"""Detailed 400Hz trace diagnostic of crouch -> push -> tuck -> landing on MOD4v3 + c874."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import mujoco
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sweep_high_jump import LEG_DELTA_BOUNDS, ProbeSim, neutral_mean  # noqa: E402


def trace_signs_and_jump():
    sim = ProbeSim()
    env, m, d = sim.env, sim.env.m, sim.env.d

    # 1. Verify exact sign conventions of pitch, wy, mean, and wheel torque!
    env.reset()
    d.qpos[:3] = [0.0, 0.0, 0.60]
    # Rotate nose UP vs nose DOWN (+0.1 rad around body y axis)
    quat = np.zeros(4)
    mujoco.mju_euler2Quat(quat, np.array([0.0, 0.10, 0.0]), "xyz")
    d.qpos[3:7] = quat
    mujoco.mj_forward(m, d)
    R = d.xmat[env.base_id].reshape(3, 3)
    pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
    # Check front bumper z vs rear bumper z!
    # Wait: in scene.xml: chassis_front pos="-0.268 0 -0.043" or "+0.244"? Let's check which way +x is!
    print(f"Base R[:,0] (body +x axis in world) at euler=(0, +0.1, 0): {R[:, 0].round(4)}, computed pitch={pitch:+.4f} rad")
    # Also check env.vx when moving in +world_x!
    d.qpos[3:7] = [1, 0, 0, 0]
    d.qvel[0] = 1.0
    mujoco.mj_forward(m, d)
    print(f"When world vx=+1.0 at identity quat, env.vx = {env.vx:+.4f}")

    # Check airborne response to +leg_mean and +wheel_vel!
    env.reset()
    d.qpos[:3] = [0.0, 0.0, 0.80]
    d.qpos[3:7] = [1, 0, 0, 0]
    mujoco.mj_forward(m, d)
    default = sim.default_active.numpy()
    a = torch.zeros(1, 6)
    # Increase mean by +0.3
    for f_i, r_i in ((0, 1), (2, 3)):
        a[0, f_i] = +0.6
        a[0, r_i] = +0.6
    for _ in range(8):
        d.ctrl[env.act_ids] = env._torque(a[:, sim.ppo_to_env]).detach().numpy().ravel()
        mujoco.mj_step(m, d)
    R = d.xmat[env.base_id].reshape(3, 3)
    p_after_leg = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
    print(f"Airborne +0.6 action on all 4 leg joints -> pitch={math.degrees(p_after_leg):+.3f} deg, wy={d.qvel[4]:+.3f} rad/s")

    env.reset()
    d.qpos[:3] = [0.0, 0.0, 0.80]
    d.qpos[3:7] = [1, 0, 0, 0]
    mujoco.mj_forward(m, d)
    a = torch.zeros(1, 6)
    a[0, 4:] = +2.0  # positive wheel velocity command
    for _ in range(8):
        d.ctrl[env.act_ids] = env._torque(a[:, sim.ppo_to_env]).detach().numpy().ravel()
        mujoco.mj_step(m, d)
    R = d.xmat[env.base_id].reshape(3, 3)
    p_after_wheel = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
    print(f"Airborne +2.0 action on wheels -> pitch={math.degrees(p_after_wheel):+.3f} deg, wy={d.qvel[4]:+.3f} rad/s, wheel_qd={d.qvel[sim.wheel_dofs].round(2)}")

    # Now inspect what torque legs produce during push and how high root/wheel get!
    env.reset()
    a_prev = torch.zeros(1, 6)
    for step_idx in range(220):
        now = float(d.time)
        obs = sim.build_obs(0.0, 0.0, 0.20 if 1.5 <= now < 1.85 else 0.36, a_prev)
        with torch.no_grad():
            raw = sim.actor(obs).clamp(-6.0, 6.0)
        act = raw.clone()
        q_legs = d.qpos[sim.leg_qadr]
        cur_delta = 0.5 * ((q_legs[0] - q_legs[1]) + (q_legs[2] - q_legs[3]))
        R = d.xmat[env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        wy = float(d.qvel[4])
        raw_np = raw[0].numpy()
        raw_mean = np.array([
            0.5 * (default[0] + 0.5 * raw_np[0] + default[1] + 0.5 * raw_np[1]),
            0.5 * (default[2] + 0.5 * raw_np[2] + default[3] + 0.5 * raw_np[3]),
        ])

        if 1.50 <= now < 1.82:
            # Crouch safely to delta=0.28
            alpha = min(1.0, (now - 1.50) / 0.18)
            td = 1.0 + (0.28 - 1.0) * alpha
            tm = raw_mean
            for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                act[0, f_i] = float(2.0 * (tm[i] + 0.5 * td - default[f_i]))
                act[0, r_i] = float(2.0 * (tm[i] - 0.5 * td - default[r_i]))
        elif 1.82 <= now < 2.00:
            # Explosive push!
            td = 1.75089
            tm = np.full(2, 0.24)
            for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                act[0, f_i] = float(2.0 * (tm[i] + 0.5 * td - default[f_i]))
                act[0, r_i] = float(2.0 * (tm[i] - 0.5 * td - default[r_i]))
        elif 2.00 <= now < 2.26:
            # Tuck!
            td = 0.1727
            tm = np.full(2, 0.30 + 2.0 * pitch + 0.20 * wy)
            for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                act[0, f_i] = float(2.0 * (tm[i] + 0.5 * td - default[f_i]))
                act[0, r_i] = float(2.0 * (tm[i] - 0.5 * td - default[r_i]))
            qd_w = d.qvel[sim.wheel_dofs]
            w_tau = 0.5 * (8.0 * pitch + 1.0 * wy)
            act[0, 4:] = torch.as_tensor((qd_w + w_tau / 0.6) / 10.0, dtype=act.dtype)
        elif 2.26 <= now < 2.50:
            # Pre-land extend
            td = 1.45
            tm = np.full(2, 0.25 + 2.0 * pitch + 0.20 * wy)
            for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                act[0, f_i] = float(2.0 * (tm[i] + 0.5 * td - default[f_i]))
                act[0, r_i] = float(2.0 * (tm[i] - 0.5 * td - default[r_i]))

        act = act.clamp(-6.0, 6.0)
        a_env = act[:, sim.ppo_to_env]
        for j in range(env.decim):
            tau = env._torque(a_env).detach().numpy().reshape(-1)
            if j % 4 == 0:
                d.ctrl[env.act_ids[:4]] = tau[:4]
            d.ctrl[env.act_ids[4:]] = tau[4:]
            mujoco.mj_step(m, d)
        a_prev = act.detach()

        if 1.76 <= now <= 2.56:
            wz_rim = float((d.xpos[sim.wheels, 2] - 0.0625).min()) * 100.0
            q_l = d.qpos[sim.leg_qadr]
            qd_l = d.qvel[sim.leg_dadr]
            R = d.xmat[env.base_id].reshape(3, 3)
            p_deg = math.degrees(math.asin(float(np.clip(-R[2, 0], -1.0, 1.0))))
            print(f"t={d.time:.3f}s z={d.qpos[2]:.3f} vz={d.qvel[2]:+.2f} delta={q_l[0]-q_l[1]:.3f} "
                  f"qd=({qd_l[0]:+.1f},{qd_l[1]:+.1f}) tau=({d.ctrl[0]:+.1f},{d.ctrl[2]:+.1f}) "
                  f"rim={wz_rim:5.1f}cm pitch={p_deg:+5.1f}deg")


if __name__ == "__main__":
    trace_signs_and_jump()
