"""Does the shaped reward prefer a hop to standing still? (audit item 7)

The 2026-09-11 audit found that no gradient ever reached the jump routes: standing still
out-scored every attempt (wheel_contact +0.8, the 0.18-0.34 m height track and lin_vel_z_l2
-0.6 all pay for staying on the floor, while the route pays its height gate ONCE on success).

This probe plays two SCRIPTED rollouts on the delivered arena, on jump_in_place routes only:

  stand : all six actions zero (the robot balances on the preloaded gas springs)
  jump  : hold --crouch_action on the legs for --hold_steps, snap to the opposite command,
          then settle for --settle_steps

and prints, for every active reward term, the mean per-env per-control-step reward of both
rollouts plus the delta (reward_manager._step_reward is already value*weight per step: the
manager stores `value/dt` where `value` is `raw*weight*dt`, reward_manager.py line 157).
The TOTAL row decides whether PPO can learn the hop at all.

    RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 RM_ROUTE_KINDS=jump_in_place \
        OMNI_KIT_ACCEPT_EULA=YES python isaac/mod4/probe_jump_reward.py \
        --headless --num_envs 16 --steps 200
"""
from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=16)
parser.add_argument("--steps", type=int, default=200)
parser.add_argument("--crouch_action", type=float, default=1.0)
parser.add_argument("--hold_steps", type=int, default=40)
parser.add_argument("--settle_steps", type=int, default=40)
parser.add_argument("--sweep", action="store_true",
                    help="try several crouch amplitudes/signs and report the best one")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def leg_action(env, value: float) -> torch.Tensor:
    act = torch.zeros((env.num_envs, 6), device=env.device)
    act[:, :4] = value
    return act


def step_rewards(env) -> torch.Tensor:
    """Weighted per-term reward of the LAST control step, in reward_manager order."""
    rm = env.reward_manager
    sr = getattr(rm, "_step_reward", None)
    if sr is not None:
        return sr.sum(dim=0)
    sums = getattr(rm, "_episode_sums", None)
    if sums is None:
        return torch.zeros(len(rm.active_terms), device=env.device)
    return torch.stack([sums[name].sum() for name in rm.active_terms])


def wheel_force(env) -> torch.Tensor:
    f = env.scene.sensors["wheel_contact"].data.net_forces_w
    if hasattr(f, "torch"):
        f = f.torch
    return f.norm(dim=-1).max(dim=1).values


def rollout(env, mode: str):
    env.reset()
    names = list(env.reward_manager.active_terms)
    totals = torch.zeros(len(names), device=env.device)
    term_names = list(env.termination_manager.active_terms)
    term_hits = {name: 0.0 for name in term_names}
    air_steps = land_steps = hard_steps = 0.0
    h_trace, g_trace, w_trace = [], [], []
    period = args.hold_steps + args.settle_steps
    t0 = time.time()
    for i in range(args.steps):
        if mode == "stand":
            act = leg_action(env, 0.0)
        else:
            k = i % period
            if k < args.hold_steps:                 # load the legs
                act = leg_action(env, args.crouch_action)
            elif k < args.hold_steps + 3:           # release
                act = leg_action(env, -args.crouch_action)
            else:
                act = leg_action(env, 0.0)
        env.step(act)
        totals += step_rewards(env)
        st = getattr(env, "_mod4_jump", None)
        if st is not None:
            air_steps += float(st["air"].sum())
            land_steps += float(st["land"].sum())
            hard_steps += float(st["hard"].sum())
            h_trace.append(float(st["h"].mean()))
        g = getattr(env, "_mod4_ground_z", None)
        if g is not None:
            g_trace.append(float(g.mean()))
        w_trace.append(float(wheel_force(env).mean()))
        for name in term_names:
            term_hits[name] += float(env.termination_manager.get_term(name).sum())
        if (i + 1) % 50 == 0:
            print("[jump-reward] %-8s %4d/%d steps  %.1f s  (%.3f s/step)"
                  % (mode, i + 1, args.steps, time.time() - t0, (time.time() - t0) / (i + 1)),
                  flush=True)
    st = getattr(env, "_mod4_jump", None)
    n = env.num_envs * max(1, args.steps)
    info = {
        "attempts": float(st["n_attempts"].sum()) if st is not None else 0.0,
        "reached": float(st["n_success"].sum()) if st is not None else 0.0,
        "risen_max": float(st["risen"].max()) if st is not None else 0.0,
        "air_frac": air_steps / n, "land_steps": land_steps, "hard_steps": hard_steps,
        "h_mean": statistics.fmean(h_trace) if h_trace else 0.0,
        "h_min": min(h_trace) if h_trace else 0.0,
        "h_max": max(h_trace) if h_trace else 0.0,
        "ground_mean": statistics.fmean(g_trace) if g_trace else 0.0,
        "wheel_force": statistics.fmean(w_trace) if w_trace else 0.0,
        "term_hits": term_hits,
    }
    return names, (totals / max(1, args.steps) / env.num_envs).cpu(), info


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    arena = mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    env.reset()
    kinds = getattr(env, "_mod4_route_kinds", None)
    ids = getattr(env, "_mod4_route_ids", None)
    print("[jump-reward] arena=%s routes=%s"
          % (arena, None if kinds is None else sorted(set(kinds))), flush=True)
    if ids is not None and kinds is not None:
        print("[jump-reward] envs on jump route: %s"
              % [(k, int((ids == i).sum())) for i, k in enumerate(kinds)
                 if int((ids == i).sum()) > 0], flush=True)
    # audit item 8: RM_DR_OFF=1 must be visible in the RUNNING environment, not just in the
    # config source.  Sensor latency, action latency and observation noise are three places it
    # silently stayed on before.
    try:
        obs = env.observation_manager.cfg.policy
        terms = [name for name in obs.__dict__
                 if getattr(getattr(obs, name, None), "noise", None) is not None]
        lags = {name: getattr(env.action_manager.get_term(name), "_max_lag", None)
                for name in env.action_manager.active_terms}
        print("[jump-reward] DR check: obs_terms_with_noise=%s action_delay_max=%s "
              "obs_delay_lag=(%d,%d) eff_noise=(%.3f,%.3f)"
              % (terms, lags, mod4_task.OBS_DELAY_MIN, mod4_task.OBS_DELAY_MAX,
                 mod4_task.EFFORT_NOISE, mod4_task.EFFORT_NOISE_WHEEL), flush=True)
    except Exception as exc:
        print("[jump-reward] DR check failed: %r" % (exc,), flush=True)
    _, stand, i_stand = rollout(env, "stand")
    if args.sweep:
        print("[jump-reward] stand reference: TOTAL=%.4f attempts=%.0f landed=%d"
              % (float(stand.sum()), i_stand["attempts"], i_stand["land_steps"]), flush=True)
        print("[jump-reward] %6s %6s %9s %8s %8s %9s %9s %9s"
              % ("amp", "hold", "risen_m", "attempts", "landed", "hard", "total", "delta"),
              flush=True)
        best = None
        for amp in (0.6, 1.0, -0.6, -1.0, -1.6):
            for hold in (20, 40):
                args.crouch_action, args.hold_steps = amp, hold
                _, jump, info = rollout(env, "jump")
                total = float(jump.sum())
                delta = total - float(stand.sum())
                print("[jump-reward] %+6.2f %6d %9.4f %8.0f %8.0f %9.0f %9.4f %+9.4f"
                      % (amp, hold, info["risen_max"], info["attempts"], info["land_steps"],
                         info["hard_steps"], total, delta), flush=True)
                if info["risen_max"] >= 0.05 and (best is None or total > best[0]):
                    best = (total, amp, hold, info["risen_max"])
        if best is None:
            print("[jump-reward] SWEEP: no configuration reached the 0.05 m gate", flush=True)
        else:
            print("[jump-reward] SWEEP best: amp=%+.2f hold=%d risen=%.4f total=%.4f "
                  "(stand %.4f)" % (best[1], best[2], best[3], best[0], float(stand.sum())),
                  flush=True)
        env.close()
        return
    _, jump, i_jump = rollout(env, "jump")
    names = list(env.reward_manager.active_terms)
    for tag, info in (("stand", i_stand), ("jump", i_jump)):
        print("[jump-reward] %s: attempts=%.0f reached=%.0f risen_max=%.3f m air=%.3f "
              "land=%.0f hard=%.0f | h(mean/min/max)=%.3f/%.3f/%.3f ground=%.3f "
              "wheel_force=%.1f N | terminations=%s"
              % (tag, info["attempts"], info["reached"], info["risen_max"], info["air_frac"],
                 info["land_steps"], info["hard_steps"], info["h_mean"], info["h_min"],
                 info["h_max"], info["ground_mean"], info["wheel_force"],
                 {k: round(v, 1) for k, v in info["term_hits"].items() if v > 0}), flush=True)
    print("[jump-reward] per-env per-step weighted reward", flush=True)
    print("[jump-reward] %-34s %12s %12s %12s" % ("reward term", "stand", "scripted", "delta"),
          flush=True)
    for i, name in enumerate(names):
        print("[jump-reward] %-34s %12.5f %12.5f %+12.5f"
              % (name, float(stand[i]), float(jump[i]), float(jump[i] - stand[i])), flush=True)
    print("[jump-reward] %-34s %12.5f %12.5f %+12.5f"
          % ("TOTAL per step", float(stand.sum()), float(jump.sum()),
             float(jump.sum() - stand.sum())), flush=True)
    print("[jump-reward] verdict: %s (crouch action %+.2f / extend %+.2f)"
          % ("JUMPING SCORES HIGHER -- gradient exists" if float(jump.sum()) > float(stand.sum())
             else "STANDING STILL STILL WINS -- fix the shaping", args.crouch_action,
             -args.crouch_action), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
