"""Prove the three skills of the closed-chain vehicle: 跑 / 跳 / 小陀螺.

Runs a trained RMVehicle-CC-Skills-v0 policy with scripted command sequences and reports
measured, not claimed, numbers:

  run   : commanded vx ladder up to 2.8 m/s -> achieved speed, error, distance, attitude
  gyro  : commanded yaw-rate ladder up to +-6 rad/s -> achieved rate, revolutions, attitude
  jump  : the contract's jump flag (observation slot 32) raised on demand -> peak body
          rise, air time, landing recovery

Usage:  python verify_skills.py --checkpoint logs/rsl_rl/rm_cc_v4/<run>/model_2000.pt
"""
import argparse, json, math, os, sys, time
from dataclasses import asdict

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "rmvehicle", "src"))
import rmvehicle  # noqa: F401  (registers the tasks)
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls

ap = argparse.ArgumentParser()
ap.add_argument("--task", default="RMVehicle-CC-Skills-v0")
ap.add_argument("--model", choices=("cc", "later"), default="cc")
ap.add_argument("--checkpoint", required=True)
ap.add_argument("--num-envs", type=int, default=64)
ap.add_argument("--device", default="cuda:0")
ap.add_argument("--out", default="deploy/skills_report.json")
ap.add_argument("--jump-hold", type=float, default=1.6)
ap.add_argument("--only", default="all",
                help="run|gyro|jump|all -- skip the other sections")
# The ladders used to be hard-coded, and the gyro ladder stopped at +-6 rad/s - which is the
# OLD action-unit ceiling (docs/HOWTO.md section 25): a verification that cannot ask for more
# than the thing it is meant to disprove would keep reporting "6 rad/s is fine" forever.  All
# three ladders are now overridable, and the gyro default reaches the trained window (+-14).
ap.add_argument("--run-ladder", default=os.environ.get("RM_RUN_LADDER",
                                                      "0.5,1.0,1.5,2.0,2.5,2.8"))
ap.add_argument("--gyro-ladder", default=os.environ.get(
    "RM_GYRO_LADDER", "2,4,6,8,10,12,14,-14"))
ap.add_argument("--jump-ladder", default=os.environ.get(
    "RM_JUMP_LADDER", "0.04,0.06,0.08,0.10,0.12,0.16"))
a = ap.parse_args()

from rmvehicle.names import CC as _CCN, RM2025_LATER as _LATER
from rmvehicle.robot_cfg import contract as _contract, wheel_effort_for as _wheel_effort
_names = _LATER if a.model == "later" else _CCN
_ct = _contract(_names)

env_cfg = load_env_cfg(a.task, play=True)
agent_cfg = load_rl_cfg(a.task)
env_cfg.scene.num_envs = a.num_envs
env_cfg.observations["actor"].enable_corruption = False
env_cfg.episode_length_s = 1e9
# we drive the jump scheduler and the commands ourselves
for dead in ("push_robot", "jump_schedule", "reset_height"):
    env_cfg.events.pop(dead, None)
env_cfg.commands["twist"].resampling_time_range = (1e9, 1e9)

env = ManagerBasedRlEnv(cfg=env_cfg, device=a.device)
env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
runner_cls = load_runner_cls(a.task) or MjlabOnPolicyRunner
runner = runner_cls(env, asdict(agent_cfg), device=a.device)
runner.load(a.checkpoint, load_cfg={"actor": True}, strict=True, map_location=a.device)
policy = runner.get_inference_policy(device=a.device)
print("loaded", a.checkpoint)

E = env.unwrapped
robot = E.scene["robot"]
_jn = list(robot.joint_names)
# JOINT indices (for joint_vel) and ACTUATOR indices (for actuator_force) are NOT the same
# space: the closed-chain model has 19 joints but 6 actuators, and feeding joint ids into a
# width-6 tensor is an out-of-bounds CUDA index - which is exactly the
# "Warp CUDA error 710: device-side assert" that killed the first v14 verification.
import re as _re
_wheel_pats = [p.strip("^$") for p in _names.wheel_joints]
WHEEL_ID = [i for i, n in enumerate(_jn)
            if any(_re.fullmatch(p, n) for p in _wheel_pats)]
assert len(WHEEL_ID) == 2, _jn
_an = list(robot.actuator_names)
WHEEL_ACT = [i for i, n in enumerate(_an) if "wheel" in n]
assert len(WHEEL_ACT) == 2, _an
WHEEL_TORQUE = _wheel_effort(_names)   # N*m, the cap training and the plant both enforce
WHEEL_PER_YAW = _ct["half_track"] / _ct["wheel_radius"]
twist = E.command_manager.get_term("twist")
DEV = E.device
N = E.num_envs
DT = E.step_dt


def set_cmd(vx=0.0, wz=0.0, height=None):
    c = twist.command
    c[:, 0] = vx
    c[:, 2] = wz
    if height is not None and hasattr(E, "_rm_height_cmd"):
        E._rm_height_cmd[:] = height


def set_jump(flag, rise=0.0):
    if not hasattr(E, "_rm_jump_flag"):
        E._rm_jump_flag = torch.zeros(N, 1, device=DEV)
        E._rm_jump_target = torch.zeros(N, 1, device=DEV)
    E._rm_jump_flag[:] = float(flag)
    E._rm_jump_target[:] = float(rise) if flag else 0.0


def roll_pitch():
    g = robot.data.projected_gravity_b
    pitch = torch.asin(g[:, 0].clamp(-1, 1))          # nose-down positive
    roll = torch.asin((-g[:, 1]).clamp(-1, 1))
    return torch.rad2deg(roll.abs()).max().item(), torch.rad2deg(pitch.abs()).max().item()


def measure(seconds, fn=None, every=0.25):
    """Run the policy for `seconds`, sampling `fn` every `every` seconds."""
    steps = int(seconds / DT)
    rec = []
    alive = torch.ones(N, device=DEV)
    for k in range(steps):
        if fn is not None and k % max(1, int(every / DT)) == 0:
            rec.append(fn())
        env.step(act())
        dead = E.termination_manager.terminated.clone()
        alive[dead] = 0.0
    return np.array(rec, dtype=float), float(alive.mean().item())


KEY = "policy" if "policy" in E.obs_buf else "actor"
print("obs group key:", KEY, "groups:", list(E.obs_buf))


def act() -> torch.Tensor:
    # rsl_rl 5 selects its own observation group(s) from the dict.
    #
    # 2026-09-10: evaluation must not carry an autograd graph.  With the actuator delay
    # buffer enabled (RM_DELAY_MAX_LAG > 0, which the later-plant launcher sets to 20) a
    # grad-requiring action reaches `torch.where(cond, data, self._buffer, out=self._buffer)`
    # inside DelayBuffer.append and raises
    #   RuntimeError: where(): functions with out=... arguments don't support automatic
    #   differentiation, but one of the arguments requires grad.
    # which aborted the run ladder after 1.2 s of ramp and produced no numbers at all.
    with torch.no_grad():
        return policy(E.obs_buf)


def step_n(n: int = 1) -> None:
    for _ in range(int(n)):
        env.step(act())


E.reset()
report = {"checkpoint": os.path.abspath(a.checkpoint), "num_envs": N}

# ------------------------------------------------------------------ 1. RUN
print("\n=== 跑 / run: vx ladder ===")
print("  cmd vx | achieved | err  | distance | max|roll| max|pitch| | alive")
run_rows = []
for vx in ([float(x) for x in a.run_ladder.split(',')]
             if a.only in ('all', 'run') else []):
    set_cmd(vx=vx, wz=0.0, height=0.22); set_jump(0)
    step_n(1.2 / DT)                                    # ramp
    x0 = robot.data.root_link_pos_w[:, 0].mean().item()

    def f():
        return [robot.data.root_link_lin_vel_b[:, 0].mean().item()]
    rec, alive = measure(3.0, f)
    x1 = robot.data.root_link_pos_w[:, 0].mean().item()
    r, p = roll_pitch()
    v = float(rec.mean())
    run_rows.append(dict(cmd=vx, achieved=v, err=abs(v - vx), dist=x1 - x0,
                         roll=r, pitch=p, alive=alive))
    print("   %5.2f  |  %6.2f  | %5.2f |  %6.2f m |   %5.1f      %5.1f     | %3.0f%%"
          % (vx, v, abs(v - vx), x1 - x0, r, p, 100 * alive))
report["run"] = run_rows

# ------------------------------------------------------------------ 2. GYRO
print("\n=== 小陀螺 / gyro spin: yaw-rate ladder ===")
print("  cmd wz | achieved | rev/s | revs  | wheel rad/s | slip rad/s | tau Nm sat% |"
      "  roll  pitch | leg diff | alive")
gyro_rows = []
for wz in ([float(x) for x in a.gyro_ladder.split(',')]
             if a.only in ('all', 'gyro') else []):
    set_cmd(vx=0.0, wz=wz, height=0.22); set_jump(0)
    step_n(1.5 / DT)
    acc = [torch.zeros(N, device=DEV)]

    def f():
        w = robot.data.root_link_ang_vel_b[:, 2]
        acc[0] = acc[0] + w * 0.25          # integrate the yaw rate -> revolutions
        return [w.mean().item()]
    rec, alive = measure(6.0, f)
    revs = float(acc[0].mean().item()) / (2 * math.pi)
    # Wheel-side evidence, because "the gyro will not go faster" has two completely different
    # causes and they need different fixes:
    #   no-slip needs v_wheel = wz * half_track / r_wheel = 3.70 * wz.
    #   slip ~ 0 and the torque pinned at the M3508 ceiling -> TORQUE-limited (motor model,
    #     ground torsion, rolling drag);  slip >> 0 -> the wheels are DRAGGING, i.e. the
    #     contact/traction model, not the policy.
    with torch.no_grad():
        _wv = robot.data.joint_vel[:, WHEEL_ID]
        _af = getattr(robot.data, "actuator_force", None)
        _af = _af[:, WHEEL_ACT] if _af is not None else torch.zeros_like(_wv)
        wheel_v = float(_wv.abs().mean().item())
        tau = float(_af.abs().mean().item())
        sat = float((_af.abs() > 0.985 * WHEEL_TORQUE).float().mean().item()) * 100.0
        slip = wheel_v - WHEEL_PER_YAW * abs(float(rec.mean()))
    z = robot.data.body_link_pos_w
    names = list(robot.body_names)
    hl, hr = names.index(_names.thigh_bodies[0]), names.index(_names.thigh_bodies[1])
    wl, wr = names.index(_names.wheel_bodies[0]), names.index(_names.wheel_bodies[1])
    leg_l = z[:, hl, 2] - z[:, wl, 2]
    leg_r = z[:, hr, 2] - z[:, wr, 2]
    legdiff = float((leg_l - leg_r).abs().mean().item()) * 1000
    r, p = roll_pitch()
    v = float(rec.mean())
    rps = abs(v) / (2 * math.pi)
    gyro_rows.append(dict(cmd=wz, achieved=v, rev_per_s=round(rps, 4), revs=revs,
                          wheel_rad_s=round(wheel_v, 3), slip_rad_s=round(slip, 3),
                          wheel_tau=round(tau, 3), wheel_tau_sat_pct=round(sat, 2),
                          roll=r, pitch=p, leg_diff_mm=legdiff, alive=alive))
    print("   %+5.1f  |  %+6.2f  | %5.2f | %5.2f |     %6.1f    |   %+6.1f    |"
          "  %5.2f %4.1f%% |  %5.1f  %5.1f |  %5.1f mm  | %3.0f%%"
          % (wz, v, rps, revs, wheel_v, slip, tau, sat, r, p, legdiff, 100 * alive))
report["gyro"] = gyro_rows

# ------------------------------------------------------------------ 3. JUMP
print("\n=== 跳 / jump: rise ladder (flag = observation slot 32) ===")
print("  target rise | peak rise | air time | take-off delay | landed upright | alive")
jump_rows = []
for rise in ([float(x) for x in a.jump_ladder.split(',')]
              if a.only in ('all', 'jump') else []):
    set_cmd(vx=0.0, wz=0.0, height=0.22); set_jump(0)
    step_n(2.0 / DT)                                     # settle first
    z0 = robot.data.root_link_pos_w[:, 2].mean().item()
    set_jump(1, rise)
    peak = -9e9; air = 0.0; delay = None
    steps = int((a.jump_hold + 1.5) / DT)
    air_secs = np.zeros(N)                          # per-env airborne time [s]
    peaks = np.zeros(N)                             # per-env peak rise [m]
    # A two-wheel robot that falls over also loses wheel contact and its root can
    # transiently rise, so "air time" and "peak rise" without an attitude gate measure
    # the TOPPLE, not the hop.  Track uprightness per env and report both metrics.
    UPRIGHT_MAX_DEG = 30.0
    base0 = robot.data.root_link_pos_w[:, 2].clone()
    alive = torch.ones(N, device=DEV)
    upright = torch.ones(N, dtype=torch.bool, device=DEV)
    air_secs_up = np.zeros(N)
    peaks_up = np.zeros(N)
    # apples-to-apples with the deployment: record the RAW policy actions so the
    # armed-minus-idle action delta can be compared with what the ONNX produces in ROS2.
    act_log = np.zeros((steps, 6), np.float32)
    flag_log = np.zeros(steps, np.float32)
    for k in range(steps):
        a_raw = act()
        act_log[k] = a_raw[0].detach().cpu().numpy() if torch.is_tensor(a_raw) \
            else np.asarray(a_raw).reshape(N, -1)[0]
        flag_log[k] = float(E._rm_jump_flag[0, 0].item()) if hasattr(E, "_rm_jump_flag") else 0.0
        env.step(a_raw)
        alive *= (~E.termination_manager.terminated).float()      # drop respawned envs
        dz = (robot.data.root_link_pos_w[:, 2] - base0).cpu().numpy()
        dz = np.where(alive.cpu().numpy() > 0, dz, np.nan)
        peaks = np.fmax(peaks, dz)
        airborne = (1.0 - (E.scene["wheel_contact"].data.found > 0).float()
                    .reshape(N, -1).max(dim=1).values).cpu().numpy()
        air_secs += airborne * DT
        g = robot.data.projected_gravity_b
        tilt = torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1.0, 1.0)))
        upright &= (tilt < UPRIGHT_MAX_DEG)
        up = (upright & (alive > 0)).cpu().numpy()
        peaks_up = np.fmax(peaks_up, np.where(up, dz, 0.0))
        air_secs_up += airborne * up.astype(float) * DT
        if k * DT > a.jump_hold:
            set_jump(0)
    keep = alive.cpu().numpy() > 0
    kup = upright.cpu().numpy() & keep
    n_up = int(kup.sum())
    air = float(np.median(air_secs_up[kup])) if n_up else 0.0
    peak = float(np.median(peaks_up[kup])) if n_up else 0.0
    peak_naive = float(np.nanmedian(peaks[keep])) if keep.any() else 0.0
    air_naive = float(np.median(air_secs[keep])) if keep.any() else 0.0
    report.setdefault("_diag", {})[f"jump_{rise}"] = dict(
        alive_envs=int(keep.sum()), air_ms_max=float(air_secs.max() * 1000))
    delay = None
    r, p = roll_pitch()
    alive = float((~E.termination_manager.terminated).float().mean().item())
    jump_rows.append(dict(target=rise, peak=peak, air_time=air, delay=delay,
                          roll=r, pitch=p, alive=alive,
                          peak_upright=peak, air_upright=air,
                          upright_envs=n_up, upright_frac=(n_up / max(1, N)),
                          peak_topple_inflated=peak_naive, air_topple_inflated=air_naive))
    print("      %.2f m   |  %.3f m  |  %5.2f s |     %5.2f s    |  roll %4.1f pitch %4.1f | %3.0f%%"
          % (rise, peak, air, delay if delay is not None else -1, r, p, 100 * alive))
    print("        UPRIGHT-GATED (<%.0f deg): %d/%d envs stayed upright ->"
          " peak rise %.3f m, airborne %.2f s   [ungated: %.3f m / %.2f s]"
          % (UPRIGHT_MAX_DEG, n_up, N, peak, air, peak_naive, air_naive))
    print("        tilt at end: median %.1f deg, max %.1f deg"
          % (float(torch.median(tilt).item()), float(tilt.max().item())))
    on = flag_log > 0.5
    off = ~on
    if on.sum() > 20 and off.sum() > 20:
        print("        ACTION delta armed-idle (env0, raw policy units):")
        for kk, lb in enumerate(["L_front1", "L_rear1", "R_front1",
                                 "R_rear1", "L_wheel", "R_wheel"]):
            if kk < act_log.shape[1]:
                print("          a[%d] %-9s idle %+7.4f  armed %+7.4f  delta %+7.4f  "
                      "armed span %.4f" % (kk, lb, act_log[off, kk].mean(),
                                           act_log[on, kk].mean(),
                                           act_log[on, kk].mean() - act_log[off, kk].mean(),
                                           act_log[on, kk].max() - act_log[on, kk].min()))
    if on.sum() > 20 and off.sum() > 20:
        jump_rows[-1]["action_delta"] = [float(act_log[on, i].mean() - act_log[off, i].mean())
                                         for i in range(min(6, act_log.shape[1]))]
report["jump"] = jump_rows

os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
json.dump(report, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\nwrote", a.out)
best_run = max((r for r in run_rows if r["alive"] > 0.5), key=lambda r: r["achieved"], default=None)
best_gyro = max((g for g in gyro_rows if g["alive"] > 0.5), key=lambda g: abs(g["achieved"]), default=None)
best_jump = max((j for j in jump_rows if j["peak"] > 0), key=lambda j: j["peak"], default=None)
print("SUMMARY  top speed %.2f m/s | gyro %.2f rad/s = %.2f rev/s (user target 2.0 rev/s)"
      " | jump %.1f cm (%.2f s air)"
      % (best_run["achieved"] if best_run else -1,
         abs(best_gyro["achieved"]) if best_gyro else -1,
         (best_gyro.get("rev_per_s", abs(best_gyro["achieved"]) / (2 * math.pi))
          if best_gyro else -1),
         (100 * best_jump["peak"] if best_jump else -1),
         (best_jump["air_time"] if best_jump else -1)))
E.close()
