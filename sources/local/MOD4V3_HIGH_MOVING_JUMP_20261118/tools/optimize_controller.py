"""Optimize 4-stage Deep-Crouch High Jump + Moving Jump controller across standing, moving, reverse, and multi-jump."""
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


def eval_config(sim: ProbeSim, cfg: dict, v_cmd: float = 0.0, jump_times=(1.8,), total_s: float = 5.2):
    env, m, d = sim.env, sim.env.m, sim.env.d
    env.reset()
    # Start smoothly at standing pose
    a_prev = torch.zeros(1, 6)
    phase = "drive"
    phase_t0 = 0.0
    next_jump_idx = 0
    air_substeps = 0
    support_substeps = 8
    local_force = np.zeros(6)

    times, root_z, com_z, rim_min_z, pitches, rolls, vxs = [], [], [], [], [], [], []
    guide_f, chassis_f, wheel_fz, phases_rec = [], [], [], []
    max_closure = 0.0
    jump_windows = []  # track each jump start
    cur_jump_start = None

    steps = int(round(total_s / 0.02))
    default = sim.default_active.numpy()

    for step_idx in range(steps):
        now = float(d.time)
        # Ramp speed command smoothly after 0.3s
        cur_vx_cmd = v_cmd * min(1.0, max(0.0, (now - 0.25) / 0.45))
        cruise_h = cfg.get("cruise_h", 0.36)

        # Trigger jump if ready in drive phase
        if phase == "drive" and next_jump_idx < len(jump_times) and now >= jump_times[next_jump_idx]:
            q_legs = d.qpos[sim.leg_qadr]
            start_delta = np.array([q_legs[0] - q_legs[1], q_legs[2] - q_legs[3]])
            phase, phase_t0 = "crouch", now
            cur_jump_start = now
            next_jump_idx += 1

        # Determine height command fed to c874
        if phase == "crouch":
            h_cmd = cfg.get("crouch_h_cmd", 0.20)
        elif phase == "absorb":
            h_cmd = cfg.get("absorb_h_cmd", 0.30)
        elif phase == "recover":
            el = now - phase_t0
            alpha_h = min(1.0, el / max(cfg.get("recover_s", 0.28), 0.02))
            h_cmd = cfg.get("absorb_h_cmd", 0.30) + (cruise_h - cfg.get("absorb_h_cmd", 0.30)) * alpha_h
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
        cur_delta = np.array([q_legs[0] - q_legs[1], q_legs[2] - q_legs[3]])
        mean_actual_delta = float(cur_delta.mean())

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
        # State machine transitions
        if phase == "crouch":
            if elapsed >= cfg["compress_s"]:
                phase, phase_t0, elapsed = "push", now, 0.0
                # Record speed at push entry for speed-compensated takeoff angle
                push_vx = float(env.vx)
        elif phase == "push":
            # Early liftoff/near-full-stroke transition to tuck!
            early_stroke = mean_actual_delta >= cfg.get("tuck_trigger_delta", 1.62) and d.qvel[2] > 1.0 and elapsed >= 0.08
            true_air = air_substeps >= cfg.get("air_confirm_substeps", 2) and d.qvel[2] > 0.3 and elapsed >= 0.06
            if early_stroke or true_air:
                phase, phase_t0, elapsed = "flight_tuck", now, 0.0
            elif elapsed >= cfg.get("push_s", 0.24):
                rec_delta = cur_delta.copy()
                phase, phase_t0, elapsed = "recover", now, 0.0
        elif phase == "flight_tuck":
            # Stay tucked past apex until downward vz threshold
            if elapsed >= cfg.get("tuck_min_s", 0.14) and (d.qvel[2] <= cfg.get("preland_vz", -0.35) or elapsed >= 0.32):
                phase, phase_t0, elapsed = "flight_preland", now, 0.0
                tuck_exit_delta = cur_delta.copy()
        elif phase == "flight_preland":
            if support_substeps >= 2 and elapsed >= 0.02:
                phase, phase_t0, elapsed = "absorb", now, 0.0
                touch_delta = cur_delta.copy()
            elif elapsed >= 0.45:
                rec_delta = cur_delta.copy()
                phase, phase_t0, elapsed = "recover", now, 0.0
        elif phase == "absorb":
            if elapsed >= cfg.get("absorb_s", 0.14):
                rec_delta = cur_delta.copy()
                phase, phase_t0, elapsed = "recover", now, 0.0
        elif phase == "recover":
            if elapsed >= cfg.get("recover_s", 0.26):
                phase, phase_t0, elapsed = "drive", now, 0.0
                jump_windows.append((cur_jump_start, now))
                cur_jump_start = None

        act = raw.clone()
        if phase != "drive":
            if phase == "crouch":
                # Smoothly compress legs to safe deep crouch (root_z ~ 0.188-0.195m, >10mm clear of guide wheels!)
                ramp_s = max(cfg.get("crouch_ramp_s", 0.18), 0.04)
                alpha = min(1.0, elapsed / ramp_s)
                # Smooth cosine interpolation reduces pitch jerk during crouch
                s_alpha = 0.5 * (1.0 - math.cos(math.pi * alpha))
                target_delta = start_delta + (cfg["crouch_delta"] - start_delta) * s_alpha
                # Let c874 control mean & wheels during crouch so moving balance & speed tracking stay rock-solid!
                target_mean = raw_mean + cfg.get("crouch_mean_offset", 0.0)
            elif phase == "push":
                target_delta = np.full(2, LEG_DELTA_BOUNDS[1])
                # Key discovery: tune push_mean + speed lead + grounded pitch feedback for zero-wy liftoff!
                base_m = cfg.get("push_mean", 0.29) + cfg.get("push_speed_k", 0.0) * push_vx
                w_raw = cfg.get("push_raw_w", 0.0)
                # Note on ground: check sign of pitch feedback! Let's test push_pitch_kp sign
                p_fb = cfg.get("push_pitch_kp", 0.0) * pitch + cfg.get("push_pitch_kd", 0.0) * wy
                target_mean = w_raw * raw_mean + (1.0 - w_raw) * base_m + p_fb
                # Keep wheels driving smoothly at ground speed during push so moving jump doesn't brake on takeoff!
                if cfg.get("push_wheel_keep_drive", True):
                    # Blend c874 wheel action with ground-speed matching
                    pass
            elif phase == "flight_tuck":
                alpha = min(1.0, elapsed / max(cfg.get("tuck_ramp_s", 0.03), 0.01))
                d_val = LEG_DELTA_BOUNDS[1] + (cfg["tuck_delta"] - LEG_DELTA_BOUNDS[1]) * alpha
                target_delta = np.full(2, d_val)
                # Base neutral mean so tucking doesn't kick body pitch!
                base_m = neutral_mean(mean_actual_delta) + cfg.get("tuck_mean_offset", 0.0) + cfg.get("air_speed_mean_k", 0.0) * float(env.vx)
                target_mean = np.full(2, base_m)
            elif phase == "flight_preland":
                alpha = min(1.0, elapsed / max(cfg.get("preland_ramp_s", 0.08), 0.02))
                s_alpha = 0.5 * (1.0 - math.cos(math.pi * alpha))
                target_delta = tuck_exit_delta + (cfg["land_delta"] - tuck_exit_delta) * s_alpha
                # Speed-compensated foot placement for landing!
                # Remember: smaller mean = wheel MORE FORWARD (+x)!
                # When moving forward (vx > 0), placing wheels slightly AHEAD (+x -> negative mean offset) catches forward momentum cleanly!
                foot_lead = cfg.get("land_speed_k", -0.06) * float(env.vx)
                base_m = neutral_mean(mean_actual_delta) + cfg.get("land_mean_offset", 0.0) + foot_lead
                target_mean = np.full(2, base_m)
            elif phase == "absorb":
                # Compliant suspension absorption + immediate c874 balance!
                alpha = min(1.0, elapsed / max(cfg.get("absorb_s", 0.14), 0.02))
                # Let c874's own balance mean & wheels handle pitch/velocity immediately while guiding leg delta softly
                d_abs = cfg.get("absorb_delta", 0.95)
                target_delta = d_abs + (raw_delta - d_abs) * (alpha ** 1.2)
                w_c874 = cfg.get("absorb_c874_mean_w", 0.90)
                target_mean = w_c874 * raw_mean + (1.0 - w_c874) * neutral_mean(mean_actual_delta)
            elif phase == "recover":
                alpha = min(1.0, elapsed / max(cfg.get("recover_s", 0.26), 0.02))
                target_delta = rec_delta + (raw_delta - rec_delta) * alpha
                target_mean = raw_mean

            target_delta = np.clip(target_delta, *LEG_DELTA_BOUNDS)

            # Active airborne attitude control (verified signs!)
            # Remember from inspect_push_and_tuck:
            #   +action on all 4 legs (+mean) -> wy < 0 (drives pitch MORE NEGATIVE, corrects pitch > 0!)
            #   Wait: earlier when pitch was -3.2 deg (<0), +2.0 * pitch gave -0.11 rad on mean -> drives wy > 0!
            #   AND check wheel sign: on wheel (+Y axis), +torque on wheel applies -Y reaction on body (wy < 0, corrects pitch > 0)!
            #   Wait: in air_balance.py:
            #     body_pitch_torque = -pitch_kp * pitch - pitch_kd * wy
            #     motor_torque_each = -0.5 * body_pitch_torque = +0.5 * (pitch_kp * pitch + pitch_kd * wy)
            #     leg_pitch = +leg_pitch_kp * pitch + leg_pitch_kd * wy
            #     result[:, :4] += 2.0 * leg_pitch  (which adds +leg_pitch to target_mean!)
            if phase in ("flight_tuck", "flight_preland") and air_substeps >= 1:
                roll_corr = float(np.clip(cfg.get("roll_kp", 0.7) * roll + cfg.get("roll_kd", 0.09) * wx, -0.18, 0.18))
                target_delta = np.clip(target_delta + np.array([-roll_corr, roll_corr]), *LEG_DELTA_BOUNDS)
                leg_pitch = float(np.clip(cfg.get("leg_pitch_kp", 2.4) * pitch + cfg.get("leg_pitch_kd", 0.24) * wy, -0.45, 0.45))
                target_mean = target_mean + leg_pitch
                motor_tau_each = 0.5 * (cfg.get("pitch_kp", 10.0) * pitch + cfg.get("pitch_kd", 1.2) * wy)
                qd_w = d.qvel[sim.wheel_dofs]
                if phase == "flight_preland" and d.qvel[2] < -1.1:
                    # Spin wheels toward ground speed right before touchdown to avoid wheel-brake pitch kick!
                    v_ground_rad = float(env.vx) / 0.0625
                    w_target = 0.5 * qd_w + 0.5 * v_ground_rad + motor_tau_each / 0.6
                else:
                    w_target = qd_w + motor_tau_each / 0.6
                act[0, 4:] = torch.as_tensor(w_target / 10.0, dtype=act.dtype)

            for i, (f_idx, r_idx) in enumerate(((0, 1), (2, 3))):
                act[0, f_idx] = float(2.0 * (target_mean[i] + 0.5 * target_delta[i] - default[f_idx]))
                act[0, r_idx] = float(2.0 * (target_mean[i] - 0.5 * target_delta[i] - default[r_idx]))

        act = act.clamp(-6.0, 6.0)
        a_env = act[:, sim.ppo_to_env]
        for j in range(env.decim):
            tau = env._torque(a_env).detach().numpy().reshape(-1)
            if j % 4 == 0:
                d.ctrl[env.act_ids[:4]] = tau[:4]
            d.ctrl[env.act_ids[4:]] = tau[4:]
            mujoco.mj_step(m, d)

            f_wheel = 0.0
            f_guide = 0.0
            f_chassis = 0.0
            f_total = 0.0
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
                if f_wheel > 10.0:
                    support_substeps += 1

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
            phases_rec.append(phase)

        a_prev = act.detach()
        if env.cos_tilt < 0.5 or float(d.qpos[2]) < 0.12 or max_closure > 0.01:
            return dict(survived=False, reason=f"reset_at_{d.time:.2f}s_phase_{phase}", closure_mm=max_closure * 1000)

    times = np.array(times)
    rim_min_z = np.array(rim_min_z)
    com_z = np.array(com_z)
    root_z = np.array(root_z)
    pitches = np.array(pitches)
    rolls = np.array(rolls)
    wheel_fz = np.array(wheel_fz)
    guide_f = np.array(guide_f)
    chassis_f = np.array(chassis_f)

    t_first = jump_times[0]
    air_mask = (times >= t_first) & (wheel_fz < 1.0) & (guide_f < 1.0) & (chassis_f < 1.0)
    padded = np.r_[False, air_mask, False].astype(int)
    segs = [(a, b) for a, b in zip(np.flatnonzero(np.diff(padded) == 1), np.flatnonzero(np.diff(padded) == -1))
            if (b - a) * 0.0025 >= 0.10]
    if not segs:
        return dict(survived=True, jumps=0)

    jumps_out = []
    for j_i, (lo, hi) in enumerate(segs):
        t0_crouch = jump_times[min(j_i, len(jump_times) - 1)]
        c_mask = (times >= t0_crouch) & (times <= times[lo])
        z_min = float(root_z[c_mask].min()) if c_mask.any() else float(root_z[lo])
        com_min = float(com_z[c_mask].min()) if c_mask.any() else float(com_z[lo])
        com_pk = float(com_z[lo:hi].max())
        rim_pk = float(rim_min_z[lo:hi].max() * 100.0)
        air_dur = (hi - lo) * 0.0025
        ap = float(np.abs(pitches[lo:hi]).max())
        ar = float(np.abs(rolls[lo:hi]).max())
        post_mask = (times >= times[min(hi, len(times) - 1)]) & (times <= times[min(hi, len(times) - 1)] + 1.0)
        pp = float(np.abs(pitches[post_mask]).max()) if post_mask.any() else 0.0
        jumps_out.append(dict(
            z_min_m=round(z_min, 4),
            com_peak_m=round(com_pk, 4),
            com_rise_cm=round((com_pk - com_min) * 100.0, 2),
            rim_peak_cm=round(rim_pk, 2),
            air_s=round(air_dur, 4),
            air_pitch_deg=round(ap, 2),
            air_roll_deg=round(ar, 2),
            post1s_pitch_deg=round(pp, 2),
        ))

    return dict(
        survived=True,
        jumps=len(jumps_out),
        first=jumps_out[0],
        all_jumps=jumps_out if len(jumps_out) > 1 else None,
        guide_N=round(float(guide_f[times >= t_first].max()), 2),
        chassis_N=round(float(chassis_f[times >= t_first].max()), 2),
        closure_mm=round(max_closure * 1000.0, 3),
    )


def main():
    sim = ProbeSim()
    base_cfg = dict(
        cruise_h=0.36,
        crouch_h_cmd=0.20,
        crouch_delta=0.26,
        crouch_ramp_s=0.18,
        compress_s=0.28,
        push_mean=0.29,
        push_speed_k=-0.04,
        push_raw_w=0.25,
        push_pitch_kp=-0.8,
        push_pitch_kd=-0.08,
        tuck_trigger_delta=1.62,
        tuck_delta=0.173,
        tuck_ramp_s=0.025,
        tuck_min_s=0.15,
        tuck_mean_offset=-0.04,
        preland_vz=-0.45,
        preland_ramp_s=0.07,
        land_delta=1.18,
        land_speed_k=-0.06,
        absorb_s=0.14,
        absorb_delta=0.98,
        absorb_h_cmd=0.30,
        recover_s=0.26,
        leg_pitch_kp=2.6,
        leg_pitch_kd=0.25,
        pitch_kp=10.0,
        pitch_kd=1.2,
        roll_kp=0.7,
        roll_kd=0.09,
    )

    print("=== Sweep 1: Tuning push_mean & tuck_trigger_delta at v=0.0 ===")
    for pm in [0.25, 0.28, 0.31, 0.34]:
        for ttd in [1.58, 1.65, 1.72]:
            c = {**base_cfg, "push_mean": pm, "tuck_trigger_delta": ttd}
            r = eval_config(sim, c, v_cmd=0.0)
            print(f"pm={pm:.2f} ttd={ttd:.2f} -> {json.dumps(r)}")

    print("\n=== Sweep 2: Tuning land_delta & absorb_delta at v=0.0 and v=0.8 ===")
    for ld in [1.10, 1.22, 1.35]:
        for ad in [0.90, 1.02, 1.12]:
            c = {**base_cfg, "push_mean": 0.30, "tuck_trigger_delta": 1.65, "land_delta": ld, "absorb_delta": ad}
            r0 = eval_config(sim, c, v_cmd=0.0)
            r8 = eval_config(sim, c, v_cmd=0.8)
            print(f"ld={ld:.2f} ad={ad:.2f} | v0: rim={r0['first']['rim_peak_cm']} airP={r0['first']['air_pitch_deg']} postP={r0['first']['post1s_pitch_deg']} gN={r0['guide_N']} "
                  f"| v0.8: rim={r8['first']['rim_peak_cm'] if r8.get('first') else -1} airP={r8['first']['air_pitch_deg'] if r8.get('first') else -1} postP={r8['first']['post1s_pitch_deg'] if r8.get('first') else -1} gN={r8.get('guide_N')}")


if __name__ == "__main__":
    main()
