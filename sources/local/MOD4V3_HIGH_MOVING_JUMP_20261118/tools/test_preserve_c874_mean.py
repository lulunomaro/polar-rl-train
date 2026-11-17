"""Test preserving c874's learned Raibert raw_mean across all jump stages while modulating delta + active air/landing damping."""
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


def run_c874_layered(sim: ProbeSim, cfg: dict, v_cmd: float = 0.0, jump_times=(1.8,), total_s: float = 5.5):
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
    guide_f, chassis_f, wheel_fz, phases_rec = [], [], [], []
    guide_by_phase = {}
    max_closure = 0.0

    steps = int(round(total_s / 0.02))
    for _ in range(steps):
        now = float(d.time)
        cur_vx_cmd = v_cmd * min(1.0, max(0.0, (now - 0.25) / 0.35))
        cruise_h = cfg.get("cruise_h", 0.38)

        if phase == "drive" and next_jump_idx < len(jump_times) and now >= jump_times[next_jump_idx]:
            q_legs = d.qpos[sim.leg_qadr]
            start_delta = np.array([default[0] + 0.5 * float(a_prev[0, 0]) - default[1] - 0.5 * float(a_prev[0, 1]),
                                    default[2] + 0.5 * float(a_prev[0, 2]) - default[3] - 0.5 * float(a_prev[0, 3])]).clip(*LEG_DELTA_BOUNDS)
            phase, phase_t0 = "crouch", now
            next_jump_idx += 1

        # Keep height command smooth for c874 observation so c874 doesn't panic!
        if phase == "crouch":
            el = now - phase_t0
            h_cmd = cruise_h + (cfg.get("crouch_h_cmd", 0.24) - cruise_h) * min(1.0, el / 0.20)
        elif phase in ("absorb", "recover"):
            h_cmd = cfg.get("land_h_cmd", 0.34)
        else:
            h_cmd = cruise_h

        obs = sim.build_obs(cur_vx_cmd, 0.0, h_cmd, a_prev)
        with torch.no_grad():
            raw = sim.actor(obs).clamp(-6.0, 6.0)

        R = d.xmat[env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
        wx, wy = float(d.qvel[3]), float(d.qvel[4])
        q_legs = d.qpos[sim.leg_qadr]
        actual_delta = np.array([q_legs[0] - q_legs[1], q_legs[2] - q_legs[3]])

        raw_np = raw[0].numpy()
        raw_mean = np.array([
            0.5 * (default[0] + 0.5 * raw_np[0] + default[1] + 0.5 * raw_np[1]),
            0.5 * (default[2] + 0.5 * raw_np[2] + default[3] + 0.5 * raw_np[3]),
        ])
        raw_delta = np.clip([
            (default[0] + 0.5 * raw_np[0]) - (default[1] + 0.5 * raw_np[1]),
            (default[2] + 0.5 * raw_np[2]) - (default[3] + 0.5 * raw_np[3]),
        ], *LEG_DELTA_BOUNDS)

        elapsed = now - phase_t0
        if phase == "crouch" and elapsed >= cfg["compress_s"]:
            phase, phase_t0, elapsed = "push", now, 0.0
        elif phase == "push":
            if air_substeps >= cfg.get("air_confirm", 6) and d.qvel[2] > 0.15 and elapsed >= 0.04:
                phase, phase_t0, elapsed = "flight_extend", now, 0.0
            elif elapsed >= cfg.get("push_s", 0.30):
                rec_delta = last_cmd_delta.copy()
                phase, phase_t0, elapsed = "recover", now, 0.0
        elif phase == "flight_extend" and elapsed >= cfg.get("extend_air_s", 0.0):
            phase, phase_t0, elapsed = "flight_tuck", now, 0.0
        elif phase == "flight_tuck":
            if elapsed >= cfg.get("tuck_s", 0.12) and (d.qvel[2] <= cfg.get("preland_vz", -0.15) or elapsed >= 0.28):
                phase, phase_t0, elapsed = "landing_extend", now, 0.0
        elif phase == "landing_extend":
            if support_substeps >= 2 and elapsed >= 0.02:
                if cfg.get("absorb_s", 0.0) > 0.0:
                    phase, phase_t0, elapsed = "absorb", now, 0.0
                else:
                    rec_delta = last_cmd_delta.copy()
                    phase, phase_t0, elapsed = "recover", now, 0.0
            elif elapsed > 0.6:
                rec_delta = last_cmd_delta.copy()
                phase, phase_t0, elapsed = "recover", now, 0.0
        elif phase == "absorb":
            if elapsed >= cfg["absorb_s"]:
                rec_delta = last_cmd_delta.copy()
                phase, phase_t0, elapsed = "recover", now, 0.0
        elif phase == "recover":
            if elapsed >= cfg.get("recover_s", 0.20):
                phase, phase_t0, elapsed = "drive", now, 0.0

        act = raw.clone()
        if phase != "drive":
            if phase == "crouch":
                alpha = min(1.0, elapsed / max(cfg.get("crouch_ramp_s", cfg["compress_s"]), 0.04))
                delta = start_delta + (cfg["crouch_delta"] - start_delta) * alpha
            elif phase in ("push", "flight_extend"):
                delta = np.full(2, LEG_DELTA_BOUNDS[1])
            elif phase == "flight_tuck":
                alpha = min(1.0, elapsed / max(cfg.get("tuck_ramp_s", 0.04), 0.01))
                delta = np.full(2, LEG_DELTA_BOUNDS[1] + (cfg["tuck_delta"] - LEG_DELTA_BOUNDS[1]) * alpha)
            elif phase == "landing_extend":
                alpha = min(1.0, elapsed / max(cfg.get("land_ramp_s", 0.08), 0.02))
                delta = np.full(2, cfg["tuck_delta"] + (cfg["land_delta"] - cfg["tuck_delta"]) * alpha)
            elif phase == "absorb":
                alpha = min(1.0, elapsed / max(cfg["absorb_s"], 0.02))
                # Compliant knee compression on impact before returning to raw_delta
                d_abs = cfg.get("absorb_delta", 1.05)
                delta = d_abs + (raw_delta - d_abs) * alpha
            else:  # recover
                if cfg.get("instant_exit", False):
                    delta = raw_delta
                else:
                    alpha = min(1.0, elapsed / max(cfg.get("recover_s", 0.20), 0.02))
                    delta = rec_delta + (raw_delta - rec_delta) * alpha

            delta = np.asarray(delta, dtype=np.float64).clip(*LEG_DELTA_BOUNDS)
            last_cmd_delta = delta.copy()

            # Preserve c874's raw_mean!
            mean = raw_mean + cfg.get("mean_offset", 0.0)
            if phase == "push":
                mean = mean + cfg.get("push_mean_offset", 0.0) + cfg.get("push_speed_k", 0.0) * float(env.vx)

            for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                act[0, f_i] = float(2.0 * (mean[i] + 0.5 * delta[i] - default[f_i]))
                act[0, r_i] = float(2.0 * (mean[i] - 0.5 * delta[i] - default[r_i]))

            # Airborne active balance (exact verified structure from air_balance.py!)
            if phase in ("flight_extend", "flight_tuck", "landing_extend") and air_substeps >= 1:
                body_pitch_tau = -cfg.get("pitch_kp", 8.0) * pitch - cfg.get("pitch_kd", 1.0) * wy
                motor_tau_each = -0.5 * body_pitch_tau
                qd_w = d.qvel[sim.wheel_dofs]
                w_target = qd_w + motor_tau_each / 0.6
                act[0, 4:] = torch.as_tensor(w_target / 10.0, dtype=act.dtype)

                roll_corr = float(np.clip(cfg.get("roll_kp", 0.6) * roll + cfg.get("roll_kd", 0.08) * wx, -0.15, 0.15))
                new_delta = np.clip(delta + np.array([-roll_corr, roll_corr]), *LEG_DELTA_BOUNDS)
                for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                    chg = float(new_delta[i] - delta[i])
                    act[0, f_i] += chg
                    act[0, r_i] -= chg
                leg_pitch = float(np.clip(cfg.get("leg_pitch_kp", 2.0) * pitch + cfg.get("leg_pitch_kd", 0.20) * wy, -0.35, 0.35))
                act[:, :4] += 2.0 * leg_pitch

            # Post-touchdown pitch brake damping during absorb/recover!
            if phase in ("absorb", "recover") and cfg.get("land_pitch_kd", 0.0) != 0.0:
                p_damp = float(np.clip(cfg.get("land_pitch_kp", 0.0) * pitch + cfg["land_pitch_kd"] * wy, -0.30, 0.30))
                act[:, :4] += 2.0 * p_damp
                if cfg.get("land_wheel_kd", 0.0) != 0.0:
                    act[0, 4:] += float(np.clip((cfg.get("land_wheel_kp", 0.0) * pitch + cfg["land_wheel_kd"] * wy) / 6.0, -1.5, 1.5))
        else:
            last_cmd_delta = raw_delta.copy()

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
            phases_rec.append(phase)

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
        z_min=round(float(root_z[c_mask].min()), 4),
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
        dict(name="ref_air_bal_c050", cruise_h=0.36, crouch_h_cmd=0.36, crouch_delta=0.50, compress_s=0.30,
             tuck_delta=0.20, extend_air_s=0.02, tuck_s=0.10, land_delta=1.35, instant_exit=True),
        dict(name="c036_tuck017_fast", cruise_h=0.40, crouch_h_cmd=0.26, crouch_delta=0.36, crouch_ramp_s=0.18, compress_s=0.28,
             air_confirm=2, extend_air_s=0.0, tuck_ramp_s=0.025, tuck_delta=0.173, tuck_s=0.14, preland_vz=-0.30,
             land_delta=1.42, instant_exit=True, leg_pitch_kp=2.4, leg_pitch_kd=0.24, pitch_kp=10.0, pitch_kd=1.2),
        dict(name="c032_tuck017_fast", cruise_h=0.40, crouch_h_cmd=0.24, crouch_delta=0.32, crouch_ramp_s=0.18, compress_s=0.28,
             air_confirm=2, extend_air_s=0.0, tuck_ramp_s=0.025, tuck_delta=0.173, tuck_s=0.14, preland_vz=-0.30,
             land_delta=1.45, instant_exit=True, leg_pitch_kp=2.4, leg_pitch_kd=0.24, pitch_kp=10.0, pitch_kd=1.2),
        dict(name="c034_absorb_damp", cruise_h=0.40, crouch_h_cmd=0.25, crouch_delta=0.34, crouch_ramp_s=0.18, compress_s=0.28,
             air_confirm=2, extend_air_s=0.0, tuck_ramp_s=0.025, tuck_delta=0.173, tuck_s=0.14, preland_vz=-0.30,
             land_delta=1.48, absorb_s=0.08, absorb_delta=1.18, recover_s=0.12,
             leg_pitch_kp=2.5, leg_pitch_kd=0.25, pitch_kp=10.0, pitch_kd=1.2,
             land_pitch_kp=-0.5, land_pitch_kd=-0.08, land_wheel_kp=-3.0, land_wheel_kd=-0.6),
    ]
    for v in [0.0, 0.8, 1.2, -0.5]:
        print(f"\n=== SPEED v_cmd = {v:+.1f} m/s ===")
        for c in configs:
            r = run_c874_layered(sim, c, v_cmd=v)
            print(f"{c['name']:20s} -> {json.dumps(r)}")


if __name__ == "__main__":
    main()
