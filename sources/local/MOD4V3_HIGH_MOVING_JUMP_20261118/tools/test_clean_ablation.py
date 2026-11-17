"""Clean ablation: Constant h_cmd + Deep Crouch + Full Tuck + Active Air Balance + Clean c874 Touchdown Handoff."""
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
from sweep_high_jump import LEG_DELTA_BOUNDS, ProbeSim  # noqa: E402


def run_clean(sim: ProbeSim, cfg: dict, v_cmd: float = 0.0, jump_times=(1.8,), total_s: float = 5.6):
    env, m, d = sim.env, sim.env.m, sim.env.d
    env.reset()
    a_prev = torch.zeros(1, 6)
    phase = "drive"
    phase_t0 = 0.0
    next_jump_idx = 0
    air_substeps = 0
    support_substeps = 8
    local_force = np.zeros(6)
    default = sim.default_active.numpy()

    times, root_z, com_z, rim_min_z, pitches, rolls = [], [], [], [], [], []
    guide_f, chassis_f, wheel_fz = [], [], []
    guide_by_phase = {}
    max_closure = 0.0
    cruise_h = cfg.get("cruise_h", 0.36)

    steps = int(round(total_s / 0.02))
    for _ in range(steps):
        now = float(d.time)
        cur_h = 0.28 + (cruise_h - 0.28) * min(1.0, now / 0.8)
        cur_vx_cmd = v_cmd * min(1.0, max(0.0, (now - 0.3) / 0.4))

        obs = sim.build_obs(cur_vx_cmd, 0.0, cur_h, a_prev)
        with torch.no_grad():
            raw = sim.actor(obs).clamp(-6.0, 6.0)

        R = d.xmat[env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
        wx, wy = float(d.qvel[3]), float(d.qvel[4])

        raw_np = raw[0].numpy()
        raw_mean = np.array([
            0.5 * (default[0] + 0.5 * raw_np[0] + default[1] + 0.5 * raw_np[1]),
            0.5 * (default[2] + 0.5 * raw_np[2] + default[3] + 0.5 * raw_np[3]),
        ])
        raw_delta = np.clip([
            (default[0] + 0.5 * raw_np[0]) - (default[1] + 0.5 * raw_np[1]),
            (default[2] + 0.5 * raw_np[2]) - (default[3] + 0.5 * raw_np[3]),
        ], *LEG_DELTA_BOUNDS)

        if phase == "drive" and next_jump_idx < len(jump_times) and now >= jump_times[next_jump_idx]:
            start_delta = raw_delta.copy()
            phase, phase_t0 = "crouch", now
            next_jump_idx += 1

        elapsed = now - phase_t0
        if phase == "crouch" and elapsed >= cfg["compress_s"]:
            phase, phase_t0, elapsed = "push", now, 0.0
        elif phase == "push":
            if air_substeps >= cfg.get("air_confirm", 4) and d.qvel[2] > 0.15 and elapsed >= 0.04:
                phase, phase_t0, elapsed = "flight_extend", now, 0.0
            elif elapsed >= cfg.get("push_s", 0.32):
                phase, phase_t0, elapsed = "drive", now, 0.0
        elif phase == "flight_extend" and elapsed >= cfg.get("extend_air_s", 0.0):
            phase, phase_t0, elapsed = "flight_tuck", now, 0.0
        elif phase == "flight_tuck":
            if elapsed >= cfg.get("tuck_s", 0.12) and (d.qvel[2] <= cfg.get("preland_vz", -0.15) or elapsed >= 0.28):
                phase, phase_t0, elapsed = "landing_extend", now, 0.0
        elif phase == "landing_extend":
            if support_substeps >= 1 and elapsed >= 0.02:
                # Touchdown! Hand back cleanly to c874 (or brief soft cushion)
                if cfg.get("cushion_s", 0.0) > 0.0:
                    phase, phase_t0, elapsed = "cushion", now, 0.0
                else:
                    phase, phase_t0, elapsed = "drive", now, 0.0
            elif elapsed > 0.6:
                phase, phase_t0, elapsed = "drive", now, 0.0
        elif phase == "cushion":
            if elapsed >= cfg["cushion_s"]:
                phase, phase_t0, elapsed = "drive", now, 0.0

        act = raw.clone()
        if phase != "drive":
            if phase == "crouch":
                alpha = min(1.0, elapsed / max(cfg.get("crouch_ramp_s", cfg["compress_s"]), 0.04))
                s_alpha = 0.5 * (1.0 - math.cos(math.pi * alpha))
                delta = start_delta + (cfg["crouch_delta"] - start_delta) * s_alpha
            elif phase in ("push", "flight_extend"):
                delta = np.full(2, LEG_DELTA_BOUNDS[1])
            elif phase == "flight_tuck":
                alpha = min(1.0, elapsed / max(cfg.get("tuck_ramp_s", 0.03), 0.01))
                delta = np.full(2, LEG_DELTA_BOUNDS[1] + (cfg["tuck_delta"] - LEG_DELTA_BOUNDS[1]) * alpha)
            elif phase == "landing_extend":
                alpha = min(1.0, elapsed / max(cfg.get("land_ramp_s", 0.08), 0.02))
                delta = np.full(2, cfg["tuck_delta"] + (cfg["land_delta"] - cfg["tuck_delta"]) * alpha)
            elif phase == "cushion":
                # Keep c874's exact balance action, only prevent raw_delta from collapsing below cushion_min_delta!
                alpha = min(1.0, elapsed / max(cfg["cushion_s"], 0.02))
                min_d = cfg.get("cushion_min_delta", 1.05) * (1.0 - alpha) + raw_delta * alpha
                delta = np.maximum(raw_delta, min_d)

            delta = np.asarray(delta, dtype=np.float64).clip(*LEG_DELTA_BOUNDS)
            mean = raw_mean.copy()
            if phase == "push":
                mean = mean + cfg.get("push_mean_bias", 0.0) + cfg.get("push_speed_k", 0.0) * float(env.vx)

            for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                act[0, f_i] = float(2.0 * (mean[i] + 0.5 * delta[i] - default[f_i]))
                act[0, r_i] = float(2.0 * (mean[i] - 0.5 * delta[i] - default[r_i]))

            if phase in ("flight_extend", "flight_tuck", "landing_extend") and air_substeps >= 1:
                body_pitch_tau = -cfg.get("pitch_kp", 9.0) * pitch - cfg.get("pitch_kd", 1.1) * wy
                motor_tau_each = -0.5 * body_pitch_tau
                qd_w = d.qvel[sim.wheel_dofs]
                if phase == "landing_extend" and cfg.get("match_wheel_speed_land", False) and d.qvel[2] < -1.0:
                    # Match wheel tangential speed to horizontal ground speed right before touchdown!
                    w_ground = float(env.vx) / 0.0625
                    w_target = 0.35 * qd_w + 0.65 * w_ground + motor_tau_each / 0.6
                else:
                    w_target = qd_w + motor_tau_each / 0.6
                act[0, 4:] = torch.as_tensor(w_target / 10.0, dtype=act.dtype)

                roll_corr = float(np.clip(cfg.get("roll_kp", 0.65) * roll + cfg.get("roll_kd", 0.08) * wx, -0.15, 0.15))
                new_delta = np.clip(delta + np.array([-roll_corr, roll_corr]), *LEG_DELTA_BOUNDS)
                for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                    chg = float(new_delta[i] - delta[i])
                    act[0, f_i] += chg
                    act[0, r_i] -= chg
                leg_pitch = float(np.clip(cfg.get("leg_pitch_kp", 2.2) * pitch + cfg.get("leg_pitch_kd", 0.22) * wy, -0.38, 0.38))
                act[:, :4] += 2.0 * leg_pitch

        act = act.clamp(-6.0, 6.0)
        a_env = act[:, sim.ppo_to_env]
        for j in range(env.decim):
            tau = env._torque(a_env).detach().numpy().reshape(-1)
            if j % 4 == 0:
                d.ctrl[env.act_ids[:4]] = tau[:4]
            d.ctrl[env.act_ids[4:]] = tau[4:]
            mujoco.mj_step(m, d)

            f_wheel = f_guide = f_chassis = f_total = 0.0
            for ci in range(d.ncon):
                c = d.contact[ci]
                b1, b2 = int(m.geom_bodyid[c.geom1]), int(m.geom_bodyid[c.geom2])
                if (b1 == 0) == (b2 == 0):
                    continue
                rb = b2 if b1 == 0 else b1
                mujoco.mj_contactForce(m, d, ci, local_force)
                fnorm = float(np.linalg.norm(local_force[:3]))
                f_total += fnorm
                if rb in sim.wheels:
                    f_wheel += abs(float(local_force[0]))
                elif rb in sim.guides:
                    f_guide += fnorm
                elif rb == env.base_id:
                    f_chassis += fnorm
            if f_total < 1.0:
                air_substeps += 1
                support_substeps = 0
            else:
                air_substeps = 0
                if f_wheel > 5.0:
                    support_substeps += 1

            guide_by_phase[phase] = max(guide_by_phase.get(phase, 0.0), round(f_guide, 1))
            cl = max(float(np.linalg.norm(d.site_xpos[u] - d.site_xpos[v])) for u, v in sim.pairs)
            max_closure = max(max_closure, cl)
            R_sub = d.xmat[env.base_id].reshape(3, 3)
            p_deg = math.degrees(math.asin(float(np.clip(-R_sub[2, 0], -1.0, 1.0))))
            r_deg = math.degrees(math.atan2(float(R_sub[2, 1]), float(R_sub[2, 2])))
            wz_rim = float((d.xpos[sim.wheels, 2] - 0.0625).min())

            times.append(float(d.time))
            root_z.append(float(d.qpos[2]))
            com_z.append(float(d.subtree_com[env.base_id, 2]))
            rim_min_z.append(wz_rim)
            pitches.append(p_deg)
            rolls.append(r_deg)
            guide_f.append(f_guide)
            chassis_f.append(f_chassis)
            wheel_fz.append(f_wheel)

        a_prev = act.detach()
        if env.cos_tilt < 0.5 or float(d.qpos[2]) < 0.12 or max_closure > 0.01:
            return dict(survived=False, reason=f"reset_at_{d.time:.2f}s_{phase}", guide_by_phase=guide_by_phase)

    times = np.array(times)
    rim_min_z = np.array(rim_min_z)
    com_z = np.array(com_z)
    root_z = np.array(root_z)
    pitches = np.array(pitches)
    rolls = np.array(rolls)
    wheel_fz = np.array(wheel_fz)
    guide_f = np.array(guide_f)
    chassis_f = np.array(chassis_f)

    t0 = jump_times[0]
    air_mask = (times >= t0) & (wheel_fz < 1.0) & (guide_f < 1.0) & (chassis_f < 1.0)
    padded = np.r_[False, air_mask, False].astype(int)
    segs = [(a, b) for a, b in zip(np.flatnonzero(np.diff(padded) == 1), np.flatnonzero(np.diff(padded) == -1))
            if (b - a) * 0.0025 >= 0.08]
    if not segs:
        return dict(survived=True, jumps=0, guide_by_phase=guide_by_phase)
    lo, hi = max(segs, key=lambda x: x[1] - x[0])
    c_mask = (times >= t0) & (times <= times[lo])
    post_mask = (times >= times[min(hi, len(times) - 1)]) & (times <= times[min(hi, len(times) - 1)] + 1.0)
    return dict(
        survived=True,
        jumps=len(segs),
        z_min=round(float(root_z[c_mask].min()), 4),
        z_min_land=round(float(root_z[post_mask].min()), 4),
        com_rise_cm=round(float((com_z[lo:hi].max() - com_z[c_mask].min()) * 100.0), 2),
        rim_cm=round(float(rim_min_z[lo:hi].max() * 100.0), 2),
        air_s=round((hi - lo) * 0.0025, 4),
        air_p=round(float(np.abs(pitches[lo:hi]).max()), 2),
        air_r=round(float(np.abs(rolls[lo:hi]).max()), 2),
        post1s_p=round(float(np.abs(pitches[post_mask]).max()), 2),
        guide_N=round(float(guide_f[times >= t0].max()), 2),
        guide_by_phase={k: v for k, v in guide_by_phase.items() if v > 0},
        closure_mm=round(max_closure * 1000.0, 3),
    )


def main():
    sim = ProbeSim()
    configs = [
        dict(name="clean_c032_h36", cruise_h=0.36, crouch_delta=0.32, compress_s=0.30,
             tuck_delta=0.173, tuck_ramp_s=0.03, tuck_s=0.12, land_delta=1.45, match_wheel_speed_land=True),
        dict(name="clean_c026_h38", cruise_h=0.38, crouch_delta=0.26, compress_s=0.30,
             tuck_delta=0.173, tuck_ramp_s=0.025, tuck_s=0.14, land_delta=1.50, match_wheel_speed_land=True),
        dict(name="clean_c022_h40", cruise_h=0.40, crouch_delta=0.22, compress_s=0.30,
             tuck_delta=0.173, tuck_ramp_s=0.025, tuck_s=0.14, land_delta=1.55, match_wheel_speed_land=True,
             cushion_s=0.10, cushion_min_delta=0.95),
        dict(name="clean_c018_h40_cush", cruise_h=0.40, crouch_delta=0.18, crouch_ramp_s=0.22, compress_s=0.28,
             tuck_delta=0.173, tuck_ramp_s=0.025, tuck_s=0.14, land_delta=1.58, match_wheel_speed_land=True,
             cushion_s=0.12, cushion_min_delta=1.02),
    ]
    for v in [0.0, 0.4, 0.8, 1.2, -0.5]:
        print(f"\n=== SPEED v_cmd = {v:+.1f} m/s ===")
        for c in configs:
            r = run_clean(sim, c, v_cmd=v)
            print(f"{c['name']:18s} -> {json.dumps(r)}")


if __name__ == "__main__":
    main()
