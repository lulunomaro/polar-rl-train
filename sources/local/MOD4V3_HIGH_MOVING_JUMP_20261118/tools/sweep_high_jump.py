"""Systematic MuJoCo parameter sweep for MOD4v3 Deep-Crouch High Jump & Moving Jump on exact c874 + Mod4v3Mujoco."""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
TASK_DIR = HERE.parent
REPO = TASK_DIR.parents[2]

OLD_DELIVERY = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
LOW_PITCH_DELIVERY = REPO / "deliveries/MOD4V3_LOW_PITCH_20261116"

XML_PATH = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/mjcf/scene.xml"
RUNTIME_PATH = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/runtime_config.json"
SEMANTICS_PATH = OLD_DELIVERY / "plant/MOD4v3_HW300N60_R3/semantics.json"
BANK_PATH = OLD_DELIVERY / "plant/reset_bank.json"
TEMPLATE_PATH = OLD_DELIVERY / "runtime/core/template_spec.json"
CKPT_PATH = LOW_PITCH_DELIVERY / "model_full_ppo.pt"

sys.path.insert(0, str(OLD_DELIVERY / "runtime/core"))
from play_mod4v3 import LEG_DELTA_BOUNDS, Mod4v3Mujoco, RobotSpec, _q_from_bank, _q_from_runtime  # noqa: E402
from play_ppo_flatv1 import ActorMLP, _map  # noqa: E402

# Empirical neutral 4-bar curve from map_4bar_kinematics (actual_delta -> neutral_mean where wheel_x == com_x at pitch=0)
DELTA_GRID = np.array([0.348, 0.503, 0.659, 0.809, 0.952, 1.086, 1.210, 1.325, 1.432, 1.532, 1.625, 1.712, 1.752])
MEAN_GRID = np.array([0.4674, 0.4217, 0.3800, 0.3451, 0.3172, 0.2953, 0.2780, 0.2645, 0.2538, 0.2454, 0.2386, 0.2332, 0.2317])


def neutral_mean(delta: float) -> float:
    return float(np.interp(delta, DELTA_GRID, MEAN_GRID))


class ProbeSim:
    def __init__(self):
        ck = torch.load(CKPT_PATH, map_location="cpu", weights_only=False)
        template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
        self.spec = RobotSpec(**template["spec"])
        runtime = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
        semantics = json.loads(SEMANTICS_PATH.read_text(encoding="utf-8"))
        bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
        self.default_q = _q_from_runtime(runtime, self.spec.joint_names)
        self.bank_q, self.bank_z = _q_from_bank(bank, semantics, self.spec.joint_names)
        self.order = list(ck["action_order"])
        self.actor = ActorMLP()
        self.actor.load_state_dict(ck["actor_state_dict"], strict=False)
        self.actor.eval()
        self.env = Mod4v3Mujoco(str(XML_PATH), self.spec, self.default_q, self.bank_q, self.bank_z, device="cpu", action_clip=6.0)
        self.ppo_to_env = torch.tensor([0, 2, 1, 3, 4, 5], dtype=torch.long)
        self.default_active = _map(self.default_q, self.spec.joint_names, self.order)
        m = self.env.m
        self.pairs = [(m.site(e.get("site1")).id, m.site(e.get("site2")).id)
                      for e in ET.parse(XML_PATH).getroot().findall("equality/connect")]
        self.wheels = [m.body("left_wheel_link").id, m.body("right_wheel_link").id]
        self.guides = sorted({int(m.geom_bodyid[i]) for i in range(m.ngeom) if m.geom(i).name.startswith("guide_wheel_")})
        self.wheel_dofs = [int(m.joint("left_wheel_joint").dofadr[0]), int(m.joint("right_wheel_joint").dofadr[0])]
        self.leg_qadr = [int(m.joint(n).qposadr[0]) for n in self.order[:4]]
        self.leg_dadr = [int(m.joint(n).dofadr[0]) for n in self.order[:4]]

    def current_active(self):
        q_all = torch.tensor(self.env.d.qpos[self.env.qadr_all], dtype=torch.float32)
        qd_all = torch.tensor(self.env.d.qvel[self.env.dadr_all], dtype=torch.float32)
        return _map(q_all, self.spec.joint_names, self.order), _map(qd_all, self.spec.joint_names, self.order)

    def build_obs(self, cmd_vx: float, cmd_wz: float, height: float, a_prev: torch.Tensor):
        q, qd = self.current_active()
        R = torch.tensor(np.array(self.env.d.xmat[self.env.base_id], dtype=np.float64).reshape(3, 3), dtype=torch.float32)
        gravity_b = R.T @ torch.tensor([0.0, 0.0, -1.0], dtype=torch.float32)
        root_ang_vel_b = torch.tensor(self.env.d.qvel[3:6], dtype=torch.float32)
        joint_pos = q - self.default_active
        joint_pos[4:] = 0.0
        mode = torch.zeros(7, dtype=torch.float32)
        mode[0] = 1.0
        return torch.cat((
            torch.tensor([cmd_vx, 0.0, cmd_wz], dtype=torch.float32),
            torch.tensor([height * 5.0], dtype=torch.float32),
            root_ang_vel_b * 0.5,
            gravity_b,
            joint_pos,
            qd[:4] * 0.1,
            qd[4:] * 0.1,
            a_prev[0],
            mode,
        ), 0).unsqueeze(0)

    def run_trial(self, cfg: dict, v_cmd: float = 0.0, total_s: float = 5.5):
        env, m, d = self.env, self.env.m, self.env.d
        env.reset()
        a_prev = torch.zeros(1, 6)
        phase = "approach"
        phase_t0 = 0.0
        jump_trigger_s = 1.8
        air_substeps = 0
        local_force = np.zeros(6)

        times, root_z, com_z, rim_min_z, pitches, rolls = [], [], [], [], [], []
        guide_f, chassis_f, wheel_fz, phases_rec = [], [], [], []
        max_closure = 0.0
        crouch_min_z = 999.0
        landed_time = None
        touchdown_vz = 0.0

        steps = int(round(total_s / 0.02))
        for step_idx in range(steps):
            now = float(d.time)
            # Ramp command speed after 0.4s
            cur_vx = v_cmd * min(1.0, max(0.0, (now - 0.3) / 0.4))
            base_h = cfg.get("approach_h", 0.32)
            # Determine height command to base policy
            if phase == "crouch":
                h_cmd = cfg.get("crouch_h_cmd", 0.20)
            elif phase in ("absorb", "recover"):
                h_cmd = cfg.get("land_h_cmd", 0.28)
            else:
                h_cmd = base_h

            obs = self.build_obs(cur_vx, 0.0, h_cmd, a_prev)
            with torch.no_grad():
                raw = self.actor(obs).clamp(-6.0, 6.0)

            # Read current state
            R = d.xmat[env.base_id].reshape(3, 3)
            pitch = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
            roll = math.atan2(float(R[2, 1]), float(R[2, 2]))
            wx, wy = float(d.qvel[3]), float(d.qvel[4])
            q_legs = d.qpos[self.leg_qadr]
            qd_legs = d.qvel[self.leg_dadr]
            cur_delta = np.array([q_legs[0] - q_legs[1], q_legs[2] - q_legs[3]])
            cur_mean = np.array([0.5 * (q_legs[0] + q_legs[1]), 0.5 * (q_legs[2] + q_legs[3])])
            default = self.default_active.numpy()
            raw_np = raw[0].numpy()
            raw_mean = np.array([
                0.5 * (default[0] + 0.5 * raw_np[0] + default[1] + 0.5 * raw_np[1]),
                0.5 * (default[2] + 0.5 * raw_np[2] + default[3] + 0.5 * raw_np[3]),
            ])
            raw_delta = np.clip([
                (default[0] + 0.5 * raw_np[0]) - (default[1] + 0.5 * raw_np[1]),
                (default[2] + 0.5 * raw_np[2]) - (default[3] + 0.5 * raw_np[3]),
            ], *LEG_DELTA_BOUNDS)

            # Phase transitions
            elapsed = now - phase_t0
            if phase == "approach" and now >= jump_trigger_s:
                phase, phase_t0, elapsed = "crouch", now, 0.0
                self._start_delta = cur_delta.copy()
                self._start_mean = cur_mean.copy()
            elif phase == "crouch":
                crouch_min_z = min(crouch_min_z, float(d.qpos[2]))
                # Trigger push either on compress_s or countermovement bottom
                if elapsed >= cfg["compress_s"]:
                    phase, phase_t0, elapsed = "push", now, 0.0
            elif phase == "push":
                if air_substeps >= cfg.get("air_confirm_substeps", 4) and d.qvel[2] > 0.2:
                    phase, phase_t0, elapsed = "flight_tuck", now, 0.0
                elif elapsed >= cfg["push_s"]:
                    phase, phase_t0, elapsed = "recover", now, 0.0
                    self._rec_delta = cur_delta.copy()
            elif phase == "flight_tuck":
                if elapsed >= cfg["tuck_hold_s"] and (d.qvel[2] <= cfg.get("preland_vz", -0.15) or elapsed >= 0.36):
                    phase, phase_t0, elapsed = "flight_preland", now, 0.0
            elif phase == "flight_preland":
                if air_substeps == 0 and elapsed >= 0.02:
                    phase, phase_t0, elapsed = "absorb", now, 0.0
                    landed_time = now
                    touchdown_vz = float(d.qvel[2])
                elif elapsed >= 0.5:
                    phase, phase_t0, elapsed = "recover", now, 0.0
                    self._rec_delta = cur_delta.copy()
            elif phase == "absorb":
                if elapsed >= cfg.get("absorb_s", 0.12):
                    phase, phase_t0, elapsed = "recover", now, 0.0
                    self._rec_delta = cur_delta.copy()
            elif phase == "recover":
                if elapsed >= cfg.get("blend_s", 0.26):
                    phase, phase_t0, elapsed = "done", now, 0.0

            act = raw.clone()
            if phase not in ("approach", "done"):
                if phase == "crouch":
                    alpha = min(1.0, elapsed / max(cfg["compress_s"] * cfg.get("crouch_ramp_frac", 0.65), 0.04))
                    target_delta = self._start_delta + (cfg["crouch_delta"] - self._start_delta) * alpha
                    # Blend mean between raw_mean (keeps c874 balance!) and neutral crouch mean + speed pitch lead
                    use_c874_mean = cfg.get("crouch_c874_mean_w", 0.7)
                    n_mean = neutral_mean(float(cur_delta.mean())) + cfg.get("crouch_mean_bias", 0.0) - cfg.get("speed_mean_k", 0.0) * env.vx
                    target_mean = use_c874_mean * raw_mean + (1.0 - use_c874_mean) * n_mean
                elif phase == "push":
                    target_delta = np.full(2, cfg.get("push_delta", LEG_DELTA_BOUNDS[1]))
                    w_raw = cfg.get("push_c874_mean_w", 0.35)
                    n_mean = neutral_mean(float(cur_delta.mean())) + cfg.get("push_mean_bias", 0.0) - cfg.get("push_speed_k", 0.04) * env.vx
                    # Pitch stabilization during push!
                    pitch_corr = cfg.get("push_pitch_kp", 1.2) * pitch + cfg.get("push_pitch_kd", 0.12) * wy
                    target_mean = w_raw * raw_mean + (1.0 - w_raw) * n_mean + pitch_corr
                    # Wheel assist during push to keep pitch=0 and maintain speed
                    if cfg.get("push_wheel_kp", 0.0) != 0.0:
                        w_tau = 0.5 * (cfg["push_wheel_kp"] * pitch + cfg.get("push_wheel_kd", 0.5) * wy)
                        qd_w = d.qvel[self.wheel_dofs]
                        v_w = qd_w + w_tau / 0.6 + cfg.get("push_wheel_v_boost", 0.0) * np.sign(v_cmd if abs(v_cmd) > 0.05 else 0.0)
                        act[0, 4:] = torch.as_tensor(v_w / 10.0, dtype=act.dtype)
                elif phase == "flight_tuck":
                    alpha = min(1.0, elapsed / max(cfg.get("tuck_ramp_s", 0.04), 0.01))
                    d_val = LEG_DELTA_BOUNDS[1] + (cfg["tuck_delta"] - LEG_DELTA_BOUNDS[1]) * alpha
                    target_delta = np.full(2, d_val)
                    target_mean = np.full(2, neutral_mean(float(cur_delta.mean())) + cfg.get("tuck_mean_bias", 0.0))
                elif phase == "flight_preland":
                    alpha = min(1.0, elapsed / max(cfg.get("preland_ramp_s", 0.08), 0.02))
                    d_val = cfg["tuck_delta"] + (cfg["land_delta"] - cfg["tuck_delta"]) * alpha
                    target_delta = np.full(2, d_val)
                    # Lead foot slightly forward proportional to horizontal speed for clean moving landing!
                    # Wait: check sign of mean vs wheel_x! Earlier: if wx > cx: lo = mid!
                    # Let's check: when mean increases, does wheel move forward (+x) or backward (-x)?
                    speed_lead = cfg.get("land_speed_lead_k", 0.0) * env.vx
                    target_mean = np.full(2, neutral_mean(d_val) + speed_lead)
                elif phase == "absorb":
                    # Compliant knee absorption + blend c874 balance!
                    alpha = min(1.0, elapsed / max(cfg.get("absorb_s", 0.12), 0.02))
                    d_absorb = cfg.get("absorb_delta", 0.85)
                    d_end = cfg.get("recover_start_delta", 1.05)
                    target_delta = np.full(2, d_absorb + (d_end - d_absorb) * alpha)
                    w_c874 = cfg.get("absorb_c874_w", 0.85)
                    pitch_damp = cfg.get("absorb_pitch_kp", 0.8) * pitch + cfg.get("absorb_pitch_kd", 0.15) * wy
                    target_mean = w_c874 * raw_mean + (1.0 - w_c874) * neutral_mean(float(cur_delta.mean())) + pitch_damp
                    # Also let c874 wheels work + extra pitch rate damping on wheels!
                    if cfg.get("absorb_wheel_kd", 0.0) != 0.0:
                        qd_w = d.qvel[self.wheel_dofs]
                        v_c874 = raw_np[4:] * 10.0
                        v_damp = v_c874 + (cfg.get("absorb_wheel_kp", 4.0) * pitch + cfg["absorb_wheel_kd"] * wy) / 0.6
                        act[0, 4:] = torch.as_tensor(v_damp / 10.0, dtype=act.dtype)
                elif phase == "recover":
                    alpha = min(1.0, elapsed / max(cfg.get("blend_s", 0.26), 0.02))
                    target_delta = self._rec_delta + (raw_delta - self._rec_delta) * alpha
                    target_mean = raw_mean

                target_delta = np.clip(target_delta, *LEG_DELTA_BOUNDS)

                # Airborne active balance (wheel reaction + leg common pitch + differential roll)
                if phase in ("flight_tuck", "flight_preland") and air_substeps >= 2:
                    roll_corr = float(np.clip(cfg.get("roll_kp", 0.6) * roll + cfg.get("roll_kd", 0.08) * wx, -0.15, 0.15))
                    target_delta = np.clip(target_delta + np.array([-roll_corr, roll_corr]), *LEG_DELTA_BOUNDS)
                    leg_pitch = float(np.clip(cfg.get("leg_pitch_kp", 2.0) * pitch + cfg.get("leg_pitch_kd", 0.20) * wy, -0.35, 0.35))
                    target_mean = target_mean + leg_pitch
                    body_pitch_tau = -cfg.get("pitch_kp", 8.0) * pitch - cfg.get("pitch_kd", 1.0) * wy
                    motor_tau_each = -0.5 * body_pitch_tau
                    qd_w = d.qvel[self.wheel_dofs]
                    # Keep wheel speed spun near ground speed just before landing if preland, else reaction control
                    w_target = qd_w + motor_tau_each / 0.6
                    act[0, 4:] = torch.as_tensor(w_target / 10.0, dtype=act.dtype)

                for i, (f_idx, r_idx) in enumerate(((0, 1), (2, 3))):
                    act[0, f_idx] = 2.0 * (target_mean[i] + 0.5 * target_delta[i] - default[f_idx])
                    act[0, r_idx] = 2.0 * (target_mean[i] - 0.5 * target_delta[i] - default[r_idx])

            act = act.clamp(-6.0, 6.0)
            a_env = act[:, self.ppo_to_env]
            for j in range(env.decim):
                tau = env._torque(a_env).detach().numpy().reshape(-1)
                if j % 4 == 0:
                    d.ctrl[env.act_ids[:4]] = tau[:4]
                d.ctrl[env.act_ids[4:]] = tau[4:]
                mujoco.mj_step(m, d)

                # Measure contacts & geometry at 400Hz
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
                    if rb in self.wheels:
                        f_wheel += abs(float(local_force[0]))
                    elif rb in self.guides:
                        f_guide += fnorm
                    elif rb == env.base_id:
                        f_chassis += fnorm
                if f_total < 1.0:
                    air_substeps += 1
                else:
                    air_substeps = 0

                cl = max(float(np.linalg.norm(d.site_xpos[u] - d.site_xpos[v])) for u, v in self.pairs)
                max_closure = max(max_closure, cl)
                R_sub = d.xmat[env.base_id].reshape(3, 3)
                p_deg = math.degrees(math.asin(float(np.clip(-R_sub[2, 0], -1.0, 1.0))))
                r_deg = math.degrees(math.atan2(float(R_sub[2, 1]), float(R_sub[2, 2])))
                wz_rim = float((d.xpos[self.wheels, 2] - 0.0625).min())

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
                return dict(survived=False, reason="fell_or_closure", max_closure_mm=max_closure * 1000)

        times = np.array(times)
        rim_min_z = np.array(rim_min_z)
        com_z = np.array(com_z)
        root_z = np.array(root_z)
        pitches = np.array(pitches)
        rolls = np.array(rolls)
        wheel_fz = np.array(wheel_fz)
        guide_f = np.array(guide_f)
        chassis_f = np.array(chassis_f)

        # Find contiguous airborne window after jump_trigger_s
        air_mask = (times >= jump_trigger_s) & (wheel_fz < 1.0) & (guide_f < 1.0) & (chassis_f < 1.0)
        padded = np.r_[False, air_mask, False].astype(int)
        segs = list(zip(np.flatnonzero(np.diff(padded) == 1), np.flatnonzero(np.diff(padded) == -1)))
        segs = [(a, b) for a, b in segs if (b - a) * 0.0025 >= 0.05]
        if not segs:
            return dict(survived=True, airborne=False, peak_rim_cm=0.0)
        lo, hi = max(segs, key=lambda x: x[1] - x[0])
        air_s = (hi - lo) * 0.0025
        peak_rim_cm = float(rim_min_z[lo:hi].max() * 100.0)
        com_peak_m = float(com_z[lo:hi].max())
        com_crouch_m = float(com_z[(times >= jump_trigger_s) & (times <= times[lo])].min())
        com_liftoff_m = float(com_z[lo])
        air_pitch_max = float(np.abs(pitches[lo:hi]).max())
        air_roll_max = float(np.abs(rolls[lo:hi]).max())
        post_1s = (times >= times[min(hi, len(times) - 1)]) & (times <= times[min(hi, len(times) - 1)] + 1.0)
        post_pitch_max = float(np.abs(pitches[post_1s]).max()) if post_1s.any() else 999.0
        max_guide_N = float(guide_f[times >= jump_trigger_s].max())
        max_chassis_N = float(chassis_f[times >= jump_trigger_s].max())

        return dict(
            survived=True,
            airborne=True,
            crouch_min_z_m=round(crouch_min_z, 4),
            com_crouch_m=round(com_crouch_m, 4),
            com_liftoff_m=round(com_liftoff_m, 4),
            com_peak_m=round(com_peak_m, 4),
            com_rise_from_crouch_cm=round((com_peak_m - com_crouch_m) * 100.0, 2),
            com_rise_air_cm=round((com_peak_m - com_liftoff_m) * 100.0, 2),
            peak_rim_cm=round(peak_rim_cm, 2),
            air_s=round(air_s, 4),
            air_pitch_deg=round(air_pitch_max, 2),
            air_roll_deg=round(air_roll_max, 2),
            post1s_pitch_deg=round(post_pitch_max, 2),
            guide_N=round(max_guide_N, 2),
            chassis_N=round(max_chassis_N, 2),
            closure_mm=round(max_closure * 1000.0, 3),
        )


def main():
    sim = ProbeSim()
    # First check sign of mean vs wheel_x!
    configs = [
        dict(name="old_style_c050", approach_h=0.36, crouch_delta=0.50, compress_s=0.30, push_s=0.32,
             tuck_delta=0.20, tuck_hold_s=0.10, land_delta=1.35, absorb_s=0.01),
        dict(name="deep_c018_t26", approach_h=0.38, crouch_delta=0.173, compress_s=0.26, push_s=0.32,
             tuck_delta=0.173, tuck_hold_s=0.14, land_delta=1.30, absorb_s=0.12, absorb_delta=0.80),
        dict(name="deep_c018_t34", approach_h=0.40, crouch_delta=0.173, compress_s=0.34, push_s=0.32,
             tuck_delta=0.173, tuck_hold_s=0.15, land_delta=1.30, absorb_s=0.14, absorb_delta=0.75),
        dict(name="deep_c018_t42", approach_h=0.40, crouch_delta=0.173, compress_s=0.42, push_s=0.32,
             tuck_delta=0.173, tuck_hold_s=0.15, land_delta=1.30, absorb_s=0.14, absorb_delta=0.75),
        dict(name="countermove_h42_t22", approach_h=0.42, crouch_delta=0.173, crouch_ramp_frac=0.45, compress_s=0.24, push_s=0.32,
             tuck_delta=0.173, tuck_hold_s=0.16, land_delta=1.30, absorb_s=0.14, absorb_delta=0.75),
        dict(name="countermove_h42_t28", approach_h=0.42, crouch_delta=0.173, crouch_ramp_frac=0.50, compress_s=0.28, push_s=0.32,
             tuck_delta=0.173, tuck_hold_s=0.16, land_delta=1.30, absorb_s=0.14, absorb_delta=0.75),
    ]
    for v_cmd in [0.0, 0.8]:
        print(f"\n=== SWEEP AT v_cmd = {v_cmd:.1f} m/s ===")
        for cfg in configs:
            res = sim.run_trial(cfg, v_cmd=v_cmd)
            print(f"{cfg['name']:22s} -> {json.dumps(res)}")


if __name__ == "__main__":
    main()
