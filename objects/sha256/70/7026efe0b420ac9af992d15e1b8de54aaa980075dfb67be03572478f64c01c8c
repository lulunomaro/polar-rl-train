"""Why does a policy that survives 19 s in training fall in 0.2 s in the acceptance run?

Same checkpoint, same task, two env builds:
  A) play=False  -> exactly the training configuration (pushes, obs corruption/delay,
                   20 s episodes, DR events)
  B) play=True   -> exactly what train/verify_acceptance_later.py builds

Both roll out deterministically for --seconds and print tilt / height / forward speed /
action stats every 0.5 s, plus the 35-D observation vector once at t=0 so the two builds
can be compared entry by entry.

Usage (on the training host):
    PYTHONPATH=train/rmvehicle/src:third_party/rc_mjlab/mjlab/src \
    third_party/rc_mjlab/.venv/bin/python scripts/diag_policy_env_mismatch.py \
        --checkpoint <model_499.pt> --num-envs 32 --seconds 6
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

import torch

FIX_HEIGHT = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))

import rmvehicle  # noqa: E402,F401
from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper  # noqa: E402
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls  # noqa: E402


def build(task: str, checkpoint: str, num_envs: int, play: bool, device: str):
    cfg = load_env_cfg(task, play=play)
    cfg.scene.num_envs = num_envs
    if FIX_HEIGHT is not None:
        rh = cfg.events.get("reset_height")
        if rh is not None:
            rh.params["range"] = (FIX_HEIGHT, FIX_HEIGHT)
            print("pinned reset_height range to %.3f" % FIX_HEIGHT)
    if play:
        cfg.episode_length_s = 1e9
        cfg.auto_reset = True
    agent_cfg = load_rl_cfg(task)
    env = ManagerBasedRlEnv(cfg=cfg, device=device)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner_cls = load_runner_cls(task) or MjlabOnPolicyRunner
    runner = runner_cls(env, asdict(agent_cfg), device=device)
    runner.load(checkpoint, load_cfg={"actor": True}, strict=True, map_location=device)
    return env, runner, runner.get_inference_policy(device=device)


def policy_action(runner, obs, stochastic: bool):
    """Training samples (stochastic_output=True); the acceptance harness uses the mean."""
    if not stochastic:
        with torch.no_grad():
            return runner.alg.actor(obs)
    with torch.no_grad():
        return runner.alg.actor(obs, stochastic_output=True)


def describe(tag: str, env, runner, policy, steps: int, dt: float, stochastic: bool) -> None:
    E = env.unwrapped
    obs, _ = env.reset()
    print("=" * 70)
    print("[%s] wrapper obs type=%s" % (tag, type(obs).__name__))
    if hasattr(obs, "keys"):
        for key in obs.keys():
            print("    obs[%s].shape=%s" % (key, tuple(obs[key].shape)))
    buf = E.obs_buf
    print("[%s] E.obs_buf type=%s" % (tag, type(buf).__name__))
    if hasattr(buf, "keys"):
        for key in buf.keys():
            try:
                print("    buf[%s].shape=%s" % (key, tuple(buf[key].shape)))
            except Exception as exc:
                print("    buf[%s] -> %s" % (key, exc))
    elif hasattr(buf, "shape"):
        print("    buf.shape=%s" % (tuple(buf.shape),))
    if hasattr(obs, "keys") and hasattr(buf, "keys"):
        same = set(obs.keys()) == set(buf.keys())
        print("    same keys: %s" % same)
        for key in obs.keys():
            if key in buf.keys():
                try:
                    d = float((obs[key] - buf[key]).abs().max())
                    print("    max|wrapper-buf| on %s = %.6g" % (key, d))
                except Exception as exc:
                    print("    diff on %s failed: %s" % (key, exc))
    alive = torch.ones(E.num_envs, dtype=torch.bool, device=E.device)
    first_term_step = torch.full((E.num_envs,), -1, dtype=torch.long, device=E.device)
    cum_term = 0
    term_by_name = {}
    first_events = []
    tilt_at_term = []
    print("=" * 70)
    print(build_tag := f"[{tag}] obs width={E.obs_buf.shape if hasattr(E.obs_buf, 'shape') else '?'}")
    obs0 = E.obs_buf
    if hasattr(obs0, "shape"):
        mean = obs0.float().mean(dim=0)
        std = obs0.float().std(dim=0)
        print("  obs mean[:12]:", [round(float(v), 3) for v in mean[:12]])
        print("  obs std [:12]:", [round(float(v), 3) for v in std[:12]])
    for k in range(steps):
        action = policy_action(runner, obs, stochastic)
        obs, _rew, _dones, _extras = env.step(action)
        term = E.reset_terminated.bool()
        newly = term & alive
        if int(newly.sum().item()):
            cum_term += int(newly.sum().item())
            first_term_step[newly] = k
            g_now = E.scene["robot"].data.projected_gravity_b
            tilt_now = torch.rad2deg(torch.acos((-g_now[:, 2]).clamp(-1, 1)))
            tilt_at_term.extend([round(float(v), 1) for v in tilt_now[newly]])
        for name in E.termination_manager.active_terms:
            hit = E.termination_manager.get_term(name).bool() & alive
            n = int(hit.sum().item())
            if n:
                term_by_name[name] = term_by_name.get(name, 0) + n
                if len(first_events) < 6:
                    first_events.append((round(k * dt, 2), name, n))
        alive &= ~term
        if k % max(1, int(round(0.5 / dt))) == 0:
            g = E.scene["robot"].data.projected_gravity_b
            tilt = torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1, 1)))
            root_z = E.scene["robot"].data.root_link_pos_w[:, 2]
            vx = E.scene["robot"].data.root_link_lin_vel_b[:, 0]
            print(
                "  t=%4.2fs alive=%5.1f%% tilt mean=%5.1f p95=%5.1f | root_z=%5.3f | vx=%6.3f | act|mean|=%5.3f | fallen=%d"
                % (
                    k * dt,
                    100.0 * float(alive.float().mean()),
                    float(tilt.mean()),
                    float(torch.quantile(tilt, 0.95)),
                    float(root_z.mean()),
                    float(vx.mean()),
                    float(action.abs().mean()),
                    cum_term,
                )
            )
    terms = {}
    for name in E.termination_manager.active_terms:
        n = int(E.termination_manager.get_term(name).sum().item())
        if n:
            terms[name] = n
    print("  final terminations:", terms if terms else "none")
    print("  terminations by name:", term_by_name if term_by_name else "none")
    print("  first events (t, term, n):", first_events if first_events else "none")
    print("  tilt at first termination (deg):", tilt_at_term[:20])
    ended = first_term_step[first_term_step >= 0].float() * dt
    if ended.numel():
        print(
            "  first-termination: n=%d min=%.2fs median=%.2fs max=%.2fs | alive at end=%.1f%%"
            % (
                ended.numel(),
                float(ended.min()),
                float(ended.median()),
                float(ended.max()),
                100.0 * float(alive.float().mean()),
            )
        )
    else:
        print("  first-termination: none | alive at end=100.0%%")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="RM2025-Later-CC-Flat-v0")
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--num-envs", type=int, default=32)
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--freeze-vx", type=float, default=None,
                    help="freeze the twist command to vx=<value>, wz=0, stand=0")
    ap.add_argument("--play", type=int, default=1, choices=(0, 1))
    ap.add_argument("--stochastic", type=int, default=0, choices=(0, 1))
    ap.add_argument("--fix-height", type=float, default=None,
                    help="pin the reset_height command range to this single value")
    args = ap.parse_args()
    global FIX_HEIGHT
    FIX_HEIGHT = args.fix_height

    for play in (bool(args.play),):
        env, runner, policy = build(args.task, args.checkpoint, args.num_envs, play, args.device)
        if args.freeze_vx is not None:
            E = env.unwrapped
            term = E.command_manager.get_term("twist")
            term.resampling_time_range = (1e9, 1e9)
            cmd = term.command
            cmd[:] = 0.0
            cmd[:, 0] = float(args.freeze_vx)
            print("frozen twist command: vx=%.2f wz=0" % args.freeze_vx)
        dt = float(getattr(env.unwrapped, "step_dt", 0.01) or 0.01)
        steps = int(round(args.seconds / dt))
        for stochastic in (bool(args.stochastic),):
            env, runner, policy = build(args.task, args.checkpoint, args.num_envs, play, args.device)
            label = "%s %s" % (
                "play=False (training cfg)" if not play else "play=True (acceptance cfg)",
                "STOCHASTIC (training)" if stochastic else "DETERMINISTIC (acceptance)",
            )
            describe(label, env, runner, policy, steps, dt, stochastic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
