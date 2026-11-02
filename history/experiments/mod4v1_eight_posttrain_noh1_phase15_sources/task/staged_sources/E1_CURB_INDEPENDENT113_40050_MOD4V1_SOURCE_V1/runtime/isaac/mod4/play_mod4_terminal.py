#!/usr/bin/env python3
"""Terminal keyboard teleop for a trained MOD4 policy -- works over SSH, no GUI window.

Why this exists
---------------
`play_mod4.py` drives the policy inside Isaac Lab with Isaac's own `Se2Keyboard`, which requires a
focused GUI window.  Measured 2026-09-13: the operator is connected over SSH
(`who` -> "egde pts/3 ... (10.24.4.31)"), so a window opened on the physical display `:0` is
invisible to them -- there is nothing to click and nothing to focus.  This script instead reads
keystrokes from the TERMINAL (raw mode, no echo) and prints the robot's state as text, so it works
in the session the operator actually has.

Same plant as training (the Isaac USD + the same physics), so what it reports is the policy, not an
approximation of the model.

Keys (press and hold; keys repeat while held)
---------------------------------------------
    w / s   forward / backward          a / d   strafe left / right
    q / e   yaw left / right            z / x   lower / raise the height target
    space   all commands to zero        r       reset the key state
    Ctrl-C or `k`  quit

    # headless: no window, prints a status line a few times a second
    /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python isaac/mod4/play_mod4_terminal.py \
        --checkpoint logs/isaac_mod4/2026-09-13_01-17-30_mod4_fixed_mixed/model_16295.pt \
        --num_envs 1

Add `--seconds N` to stop after N seconds (default: run until you press k / Ctrl-C).
"""
from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from pathlib import Path

parser = argparse.ArgumentParser(description="terminal keyboard teleop for a MOD4 policy")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--manifest", default="")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--seconds", type=float, default=0.0, help="0 = run until quit")
parser.add_argument("--vx", type=float, default=1.0)
parser.add_argument("--vy", type=float, default=0.5)
parser.add_argument("--yaw", type=float, default=1.0)
parser.add_argument("--height_cmd", type=float, default=0.2989)
parser.add_argument("--status_hz", type=float, default=2.0)
# (no --headless here: AppLauncher owns that flag; we force it after parsing)
from isaaclab.app import AppLauncher  # noqa: E402

AppLauncher.add_app_launcher_args(parser)
args_cli, _ = parser.parse_known_args()
args_cli.headless = True


def _find_manifest(hint: str, ckpt: str):
    import json
    cands = [Path(hint)] if hint else []
    ck = Path(ckpt)
    cands += [ck.parent / "run_manifest.json", ck.parent.parent / "run_manifest.json"]
    for c in cands:
        if c.is_file():
            try:
                return json.loads(c.read_text()), str(c)
            except Exception:
                pass
    return {}, ""


MANIFEST, MANIFEST_PATH = _find_manifest(args_cli.manifest, args_cli.checkpoint)
for _k, _v in (MANIFEST.get("env") or {}).items():
    if isinstance(_v, (int, float, str, bool)):
        os.environ.setdefault(_k, str(_v))

launcher = AppLauncher(args_cli)
app = launcher.app

import torch  # noqa: E402
from importlib import metadata  # noqa: E402
from isaaclab_rl.rsl_rl import (RslRlOnPolicyRunnerCfg, RslRlMLPModelCfg,  # noqa: E402
                                RslRlPpoAlgorithmCfg, RslRlVecEnvWrapper,
                                handle_deprecated_rsl_rl_cfg)
from rsl_rl.runners import OnPolicyRunner  # noqa: E402
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def _actor_class_from_manifest() -> str:
    keys = {}
    for src in ((MANIFEST or {}).get("env") or {}, os.environ):
        for k, v in src.items():
            keys.setdefault(k, v)
    return ("mod4_sequence_model:LatentEncoderModel"
            if str(keys.get("RM_SEQ_ENCODER", "0")).strip() == "1" else "MLPModel")


_ACTOR_CLASS = _actor_class_from_manifest()


def build_runner(vecenv, ckpt):
    rcfg = RslRlOnPolicyRunnerCfg(
        seed=0, device="cuda:0", num_steps_per_env=24, max_iterations=1, save_interval=1,
        experiment_name="play", run_name="play", clip_actions=6.0, check_for_nan=True,
        obs_groups={"actor": ["policy"], "critic": ["critic"]},
        actor=RslRlMLPModelCfg(class_name=_ACTOR_CLASS, hidden_dims=[256, 128, 64],
                               activation="elu", obs_normalization=False,
                               distribution_cfg=RslRlMLPModelCfg.GaussianDistributionCfg(
                                   init_std=0.3, std_type="scalar")),
        critic=RslRlMLPModelCfg(class_name="MLPModel", hidden_dims=[256, 128, 64],
                                activation="elu", obs_normalization=False),
        algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=1.0, use_clipped_value_loss=True,
                                       clip_param=0.2, entropy_coef=0.005, num_learning_epochs=5,
                                       num_mini_batches=4, learning_rate=1e-4, schedule="fixed",
                                       gamma=0.99, lam=0.95, desired_kl=0.01, max_grad_norm=1.0))
    rcfg = handle_deprecated_rsl_rl_cfg(rcfg, metadata.version("rsl-rl-lib"))
    runner = OnPolicyRunner(vecenv, rcfg.to_dict(), log_dir=None, device=rcfg.device)
    runner.load(ckpt)
    return runner.get_inference_policy(device=vecenv.unwrapped.device)


# ---- terminal input in raw mode -----------------------------------------------------------------
_DOWN = set()
_QUIT = threading.Event()


def _reader():
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while not _QUIT.is_set():
            ch = sys.stdin.read(1)
            if not ch:
                break
            c = ch.lower()
            if c in ("k", "\x03", "\x04"):          # k / Ctrl-C / Ctrl-D
                _QUIT.set()
                break
            if c == "r":
                _DOWN.clear()
                continue
            if c == " ":
                _DOWN.discard("w"); _DOWN.discard("s")
                _DOWN.discard("a"); _DOWN.discard("d")
                _DOWN.discard("q"); _DOWN.discard("e")
                continue
            if c in "wasdqezx":
                # a lone keypress means "hold for a moment": toggle it on, and clear it on the next
                # status tick unless it repeats -- terminals cannot report key-up.
                _DOWN.add(c)
    except Exception as exc:
        print("[term] input reader stopped (%s)" % exc)
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            pass


def _cmd_from_keys():
    d = _DOWN
    vx = (args_cli.vx if "w" in d else 0.0) - (args_cli.vx if "s" in d else 0.0)
    vy = (args_cli.vy if "a" in d else 0.0) - (args_cli.vy if "d" in d else 0.0)
    yw = (args_cli.yaw if "q" in d else 0.0) - (args_cli.yaw if "e" in d else 0.0)
    dh = (1.0 if "z" in d else 0.0) - (1.0 if "x" in d else 0.0)
    return vx, vy, yw, dh


def main() -> int:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args_cli.num_envs
    env = Mod4Env(cfg)
    env.reset()
    vecenv = RslRlVecEnvWrapper(env)
    policy = build_runner(vecenv, args_cli.checkpoint)
    print("[term] policy loaded. keys: w/s a/d strafe, q/e yaw, z/x height, space stop, k quit")
    print("[term] NOTE: a terminal cannot report key-UP, so each keypress is held for one tick.")
    if sys.stdin.isatty():
        threading.Thread(target=_reader, daemon=True).start()
    else:
        print("[term] stdin is not a tty -- running with zero commands (Ctrl-C to quit)")

    term = None
    try:
        term = env.unwrapped.command_manager.get_term("twist")
    except Exception:
        pass

    obs = vecenv.get_observations()
    height = float(args_cli.height_cmd)
    t0 = time.time()
    n = 0
    dt_status = 1.0 / max(0.1, args_cli.status_hz)
    t_status = 0.0
    try:
        while not _QUIT.is_set():
            tvx, tvy, tyw, tdh = _cmd_from_keys()
            if term is not None and hasattr(term, "command"):
                with torch.no_grad():
                    term.command[:, 0] = tvx
                    term.command[:, 1] = tvy
                    term.command[:, 2] = tyw
            with torch.no_grad():
                actions = policy(obs)
            obs, _, _, _ = vecenv.step(actions)
            _DOWN.clear()                       # see NOTE above: hold for one control tick
            n += 1
            now = time.time()
            if now - t0 >= dt_status:
                t0 = now
                with torch.no_grad():
                    robot = env.unwrapped.scene["robot"]
                    p = robot.data.root_pos_w[0] - env.unwrapped.scene.env_origins[0]
                    q = robot.data.root_quat_w[0]
                    up = robot.data.projected_gravity_b[0]
                    tilt = float(torch.rad2deg(torch.acos(torch.clamp(-up[2], -1.0, 1.0))))
                    vx = float(robot.data.root_lin_vel_b[0, 0])
                print("[term] t=%6.1fs  pos=(%6.2f,%6.2f,%5.2f)  tilt=%5.1f deg  vx=%6.2f  cmd=(%.1f,%.1f,%.1f)"
                      % (now - t0 + (now - t0), p[0], p[1], p[2], tilt, vx, tvx, tvy, tyw), flush=True)
            if args_cli.seconds and n * 0.01 >= args_cli.seconds:
                break
    except KeyboardInterrupt:
        pass
    finally:
        _QUIT.set()
    print("[term] ran %d steps" % n)
    env.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
