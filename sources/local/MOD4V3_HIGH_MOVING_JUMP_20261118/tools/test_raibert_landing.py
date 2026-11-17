"""Test exact Raibert world-frame foot placement on landing_extend + skyhook_absorb across all speeds and 3x multi-jump!"""
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
from verify_locked_design import full_reset  # noqa: E402


def eval_raibert(sim: ProbeSim, cfg: dict, v_cmd: float = 0.0, jump_times=(2.4,), total_s: float = 6.6):
    env, m, d = sim.env, sim.env.m, sim.env.d
    full_reset(sim)
    a_prev = torch.zeros(1, 6)
    phase = "drive"
    phase_t0 = 0.0
    next_jump_idx = 0
    air_substeps = 0
    support_substeps = 8
    local_force = np.zeros(6)
    default = sim.default_active.numpy()

    times, root_z, com_z, rim_min_z, pitches, rolls, vxs = [], [], [], [], [], [], []
    guide_f, chassis_f, wheel_fz = [], [], []
    guide_by_phase = {}
    max_closure = 0.0
    cruise_h = cfg.get("cruise_h", 0.365)
    cmd_vx_slewed = 0.0

    steps = int(round(total_s / 0.02))
    for _ in range(steps):
        now = float(d.time)
        cur_h = min(cruise_h, 0.28 + 0.05 * now)
        target_vx = v_cmd if now >= 1.0 else 0.0
        cmd_vx_slewed += (target_vx - cmd_vx_slewed) * min(1.0, 0.02 / 0.24)

        obs = sim.build_obs(cmd_vx_slewed, 0.0, cur_h, a_prev)
        with torch.no_grad():
            raw = sim.actor(obs).clamp(-6.0, 6.0)

        R = d.xmat[env.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
        roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
        wx, wy = float(d.qvel[3]), float(d.qvel[4])
        q_legs = d.qpos[sim.leg_qadr]
        cur_actual_delta = 0.5 * ((q_legs[0] - q_legs[1]) + (q_legs[2] - q_legs[3]))

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
            crouch_cmd_delta = raw_delta.copy()
            phase, phase_t0 = "crouch", now
            next_jump_idx += 1

        elapsed = now - phase_t0
        if phase == "crouch":
            if (elapsed >= cfg["compress_s"] and support_substeps >= 4) or elapsed >= cfg["compress_s"] + 0.16:
                phase, phase_t0, elapsed = "push", now, 0.0
                push_vx = float(env.vx)
        elif phase == "push":
            if air_substeps >= cfg.get("air_confirm", 4) and d.qvel[2] > 0.20 and elapsed >= 0.04:
                phase, phase_t0, elapsed = "flight_extend", now, 0.0
            elif elapsed >= cfg.get("push_s", 0.30):
                phase, phase_t0, elapsed = "drive", now, 0.0
        elif phase == "flight_extend" and elapsed >= cfg.get("extend_air_s", 0.0):
            phase, phase_t0, elapsed = "flight_tuck", now, 0.0
        elif phase == "flight_tuck":
            if elapsed >= cfg.get("tuck_s", 0.14) and (d.qvel[2] <= cfg.get("preland_vz", -0.20) or elapsed >= 0.28):
                phase, phase_t0, elapsed = "landing_extend", now, 0.0
        elif phase == "landing_extend":
            if support_substeps >= 1 and elapsed >= 0.02:
                phase, phase_t0, elapsed = "skyhook_absorb", now, 0.0
            elif elapsed > 0.65:
                phase, phase_t0, elapsed = "drive", now, 0.0
        elif phase == "skyhook_absorb":
            if elapsed >= cfg.get("skyhook_s", 0.32):
                phase, phase_t0, elapsed = "drive", now, 0.0

        act = raw.clone()
        if phase != "drive":
            if phase == "crouch":
                c_target = cfg["crouch_delta"] + cfg.get("crouch_speed_k", 0.03) * abs(float(env.vx))
                max_step = cfg.get("crouch_rate_rad_s", 1.80) * 0.02
                crouch_cmd_delta = crouch_cmd_delta + np.clip(c_target - crouch_cmd_delta, -max_step, max_step)
                delta = crouch_cmd_delta.copy()
            elif phase in ("push", "flight_extend"):
                delta = np.full(2, LEG_DELTA_BOUNDS[1])
            elif phase == "flight_tuck":
                alpha = min(1.0, elapsed / max(cfg.get("tuck_ramp_s", 0.025), 0.01))
                delta = np.full(2, LEG_DELTA_BOUNDS[1] + (cfg["tuck_delta"] - LEG_DELTA_BOUNDS[1]) * alpha)
            elif phase == "landing_extend":
                alpha = min(1.0, elapsed / max(cfg.get("land_ramp_s", 0.08), 0.02))
                delta = np.full(2, cfg["tuck_delta"] + (cfg["land_delta"] - cfg["tuck_delta"]) * alpha)
            elif phase == "skyhook_absorb":
                fade = max(0.0, 1.0 - elapsed / max(cfg.get("skyhook_s", 0.32), 0.02))
                down_vz = max(0.0, -float(d.qvel[2]))
                skyhook_add = cfg.get("skyhook_kd", 0.42) * down_vz
                z_guard = fade * cfg.get("z_guard_kp", 12.0) * max(0.0, cfg.get("z_guard_ref", 0.285) - float(d.qpos[2]))
                delta = raw_delta + skyhook_add + z_guard

            delta = np.asarray(delta, dtype=np.float64).clip(*LEG_DELTA_BOUNDS)

            # Compute exact Raibert world-frame mean for landing & absorption!
            # Remember: +mean moves wheel REARWARD (-x), -mean moves wheel FORWARD (+x)!
            # To keep wheel at world offset dx_des = raibert_kv * vx + raibert_kerr * (vx - cmd_vx):
            #   if dx_des > 0 (want wheel ahead of COM when moving forward fast), we SUBTRACT from neutral_mean!
            #   if pitch < 0 (nose-up tilts leg forward +x), we ADD (-pitch_comp * pitch > 0) to move leg back under COM!
            raibert_mean = (
                neutral_mean(cur_actual_delta)
                - cfg.get("raibert_pitch_k", 1.15) * pitch
                - cfg.get("raibert_vx_k", 0.14) * float(env.vx)
                - cfg.get("raibert_err_k", 0.10) * (float(env.vx) - cmd_vx_slewed)
                + cfg.get("raibert_bias", 0.04)
            )

            mean = raw_mean.copy()
            if phase == "push":
                mean = mean + cfg.get("push_mean_bias", -0.15) + cfg.get("push_speed_mean_k", -0.01) * push_vx
            elif phase == "flight_tuck":
                mean = mean + cfg.get("tuck_mean_bias", -0.08)
            elif phase == "landing_extend":
                mean = mean + cfg.get("land_mean_bias", +0.06)
            elif phase == "skyhook_absorb":
                # Apply Raibert world-frame foot/hip torque ONLY once wheels touch the ground!
                w_raibert = max(0.0, 1.0 - elapsed / max(cfg.get("raibert_blend_s", 0.26), 0.02))
                mean = (1.0 - w_raibert) * raw_mean + w_raibert * np.full(2, raibert_mean)

            for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                act[0, f_i] = float(2.0 * (mean[i] + 0.5 * delta[i] - default[f_i]))
                act[0, r_i] = float(2.0 * (mean[i] - 0.5 * delta[i] - default[r_i]))

            if phase in ("flight_extend", "flight_tuck", "landing_extend") and air_substeps >= 1:
                body_pitch_tau = -cfg.get("pitch_kp", 9.0) * pitch - cfg.get("pitch_kd", 1.05) * wy
                motor_tau_each = -0.5 * body_pitch_tau
                qd_w = d.qvel[sim.wheel_dofs]
                w_target = qd_w + motor_tau_each / 0.6
                act[0, 4:] = torch.as_tensor(w_target / 10.0, dtype=act.dtype)

                roll_corr = float(np.clip(cfg.get("roll_kp", 0.65) * roll + cfg.get("roll_kd", 0.08) * wx, -0.15, 0.15))
                new_delta = np.clip(delta + np.array([-roll_corr, roll_corr]), *LEG_DELTA_BOUNDS)
                for i, (f_i, r_i) in enumerate(((0, 1), (2, 3))):
                    chg = float(new_delta[i] - delta[i])
                    act[0, f_i] += chg
                    act[0, r_i] -= chg
                leg_pitch = float(np.clip(
                    cfg.get("leg_pitch_kp", 2.5) * pitch + cfg.get("leg_pitch_kd", 0.20) * wy,
                    -0.42, 0.42
                ))
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

            if float(d.time) >= jump_times[0]:
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
            vxs.append(float(env.vx))
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

    per_jump = []
    for j_i, (lo, hi) in enumerate(segs):
        tj0 = jump_times[min(j_i, len(jump_times) - 1)]
        c_mask = (times >= tj0) & (times <= times[lo])
        post_mask = (times >= times[min(hi, len(times) - 1)]) & (times <= times[min(hi, len(times) - 1)] + 1.0)
        per_jump.append(dict(
            z_min=round(float(root_z[c_mask].min()), 4),
            z_min_land=round(float(root_z[post_mask].min()), 4),
            com_rise_cm=round(float((com_z[lo:hi].max() - com_z[c_mask].min()) * 100.0), 2),
            rim_cm=round(float(rim_min_z[lo:hi].max() * 100.0), 2),
            air_s=round((hi - lo) * 0.0025, 4),
            air_p_min=round(float(pitches[lo:hi].min()), 2),
            air_p_max=round(float(pitches[lo:hi].max()), 2),
            air_p=round(float(np.abs(pitches[lo:hi]).max()), 2),
            air_r=round(float(np.abs(rolls[lo:hi]).max()), 2),
            post1s_p=round(float(np.abs(pitches[post_mask]).max()), 2),
        ))
    j0 = per_jump[0]
    return dict(
        survived=True,
        jumps=len(per_jump),
        **j0,
        all_rims=[x["rim_cm"] for x in per_jump] if len(per_jump) > 1 else None,
        all_air_p=[x["air_p"] for x in per_jump] if len(per_jump) > 1 else None,
        all_post_p=[x["post1s_p"] for x in per_jump] if len(per_jump) > 1 else None,
        guide_N=round(float(guide_f[times >= t0].max()), 2),
        chassis_N=round(float(chassis_f[times >= t0].max()), 2),
        guide_by_phase={k: v for k, v in guide_by_phase.items() if v > 0},
        closure_mm=round(max_closure * 1000.0, 3),
    )


def main():
    sim = ProbeSim()
    variants = [
        dict(name="g1_pm15_b04", crouch_delta=0.20, compress_s=0.50, push_mean_bias=-0.15, tuck_delta=0.173, land_delta=1.54,
             raibert_pitch_k=1.20, raibert_vx_k=0.15, raibert_err_k=0.10, raibert_bias=0.04),
        dict(name="g2_pm15_b12", crouch_delta=0.20, compress_s=0.50, push_mean_bias=-0.15, tuck_delta=0.173, land_delta=1.54,
             raibert_pitch_k=1.50, raibert_vx_k=0.18, raibert_err_k=0.12, raibert_bias=0.12),
        dict(name="g3_pm16_b18", crouch_delta=0.20, compress_s=0.50, push_mean_bias=-0.16, tuck_delta=0.173, land_delta=1.54,
             raibert_pitch_k=1.80, raibert_vx_k=0.20, raibert_err_k=0.15, raibert_bias=0.18),
        dict(name="g4_c22_pm16_b15", crouch_delta=0.22, compress_s=0.48, push_mean_bias=-0.16, tuck_delta=0.173, land_delta=1.54,
             raibert_pitch_k=1.60, raibert_vx_k=0.18, raibert_err_k=0.12, raibert_bias=0.15),
    ]
    for v in [0.0, 0.4, 0.8, 1.2, -0.5]:
        print(f"\n=== SPEED v_cmd = {v:+.1f} m/s ===")
        for c in variants:
            r = eval_raibert(sim, c, v_cmd=v)
            if not r.get("survived") or not r.get("jumps"):
                print(f"{c['name']:14s} -> FAILED: {r}")
                continue
            print(f"{c['name']:14s} -> rim={r['rim_cm']:5.2f} dz={r['com_rise_cm']:5.2f} zMin={r['z_min']:.3f} zL={r['z_min_land']:.3f} "
                  f"airP=[{r['air_p_min']:+5.1f},{r['air_p_max']:+5.1f}]({r['air_p']:4.1f}) airR={r['air_r']:4.2f} postP={r['post1s_p']:5.2f} gN={r['guide_N']}")

    print("\n=== MULTI-JUMP 3x AT v_cmd = +0.8 m/s ===")
    for c in variants:
        r = eval_raibert(sim, c, v_cmd=0.8, jump_times=(1.8, 3.8, 5.8), total_s=8.0)
        if not r.get("survived") or not r.get("jumps"):
            print(f"{c['name']:14s} -> FAILED: {r}")
            continue
        print(f"{c['name']:14s} -> jumps={r['jumps']} rims={r['all_rims']} airP={r['all_air_p']} postP={r['all_post_p']} gN={r['guide_N']} cl={r['closure_mm']}mm")


if __name__ == "__main__":
    main()
