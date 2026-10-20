#!/usr/bin/env python3
"""Drive a trained MOD4 policy by KEYBOARD, in the SAME plant it was trained in.

Why this and not the MuJoCo path
--------------------------------
`sim_mujoco/onnx_play.py` (now with `--keyboard`) loads the policy into the delivered MJCF, but
that model has **0 actuators** and zeroed armature/damping on the leg joints, so with the default
`--effort-mode ctrl` the robot gets no torque at all and simply lies on its base; with
`--effort-mode qfrc` it moves but tilts over within seconds (measured 2026-09-13: 34 deg -> 40 deg
and growing).  That is a plant-fidelity problem, not a policy problem -- and it is exactly what the
sim2sim gate (checklist item 5) exists to expose.

So for "let me drive it by hand and see", this script uses Isaac Lab itself: the same USD, the same
physics settings, the same observation/command wiring the policy was trained with.  What you see is
the policy, not an approximation of the plant.

Controls (Isaac Lab's Se2Keyboard)
----------------------------------
    W / S   forward / backward        A / D   strafe left / right
    Q / E   yaw left / right          Z / X   raise / lower the height command
    SPACE   all commands to zero

    # a window opens; the camera follows the robot
    /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python isaac/mod4/play_mod4.py \
        --checkpoint logs/isaac_mod4/2026-09-13_01-17-30_mod4_fixed_mixed/model_16295.pt \
        --num_envs 4 --device cuda:0

Add `--headless` to run without a window (then it just reports, and the keyboard does nothing).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# ---- the task switches must be in os.environ BEFORE mod4_task is imported ---------------------
parser = argparse.ArgumentParser(description="keyboard-drive a trained MOD4 policy in Isaac Lab")
parser.add_argument("--checkpoint", required=True, help="model_*.pt produced by train_mod4_ppo.py")
parser.add_argument("--manifest", default="", help="run_manifest.json; default: next to the ckpt")
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--steps", type=int, default=0, help="0 = run until the window is closed")
parser.add_argument("--height_cmd", type=float, default=0.2989)
parser.add_argument("--route", default="",
                    help="put EVERY env on this route kind so one skill can be driven: "
                         "slope_spin (小陀螺), fly_jump (飞坡), tunnel_cross (过洞), "
                         "step_up (上台阶), ramp_up, ramp_down, rough_cross, run")
from isaaclab.app import AppLauncher  # noqa: E402

AppLauncher.add_app_launcher_args(parser)
args_cli, _ = parser.parse_known_args()


def _find_manifest(hint: str, ckpt: str):
    """(manifest dict, path) of the run that produced this checkpoint."""
    import json
    cands = []
    if hint:
        cands.append(Path(hint))
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
for _key, _val in (MANIFEST.get("env") or {}).items():
    if isinstance(_val, (int, float, str, bool)):
        os.environ.setdefault(_key, str(_val))
# the keyboard drives the command, so the route controller must NOT also write it
os.environ["RM_ROUTE_KINDS"] = os.environ.get("RM_ROUTE_KINDS", "")

# --route must be in the environment BEFORE mod4_task is imported (the route weights are
# read at import time); this is the same switch the evaluator uses for its focus runs.
if args_cli.route:
    os.environ["RM_ROUTE_KINDS"] = args_cli.route
    print("[play] route forced to %s (all %d envs)" % (args_cli.route, args_cli.num_envs))

launcher = AppLauncher(args_cli)
app = launcher.app

import torch  # noqa: E402
from isaaclab_rl.rsl_rl import (RslRlOnPolicyRunnerCfg, RslRlMLPModelCfg,  # noqa: E402
                                RslRlPpoAlgorithmCfg, RslRlVecEnvWrapper)
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
        seed=0, device=getattr(args_cli, "device", "cuda:0"), num_steps_per_env=24, max_iterations=1, save_interval=1,
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
    from importlib import metadata
    from isaaclab_rl.rsl_rl import handle_deprecated_rsl_rl_cfg
    rcfg = handle_deprecated_rsl_rl_cfg(rcfg, metadata.version("rsl-rl-lib"))
    runner = OnPolicyRunner(vecenv, rcfg.to_dict(), log_dir=None, device=rcfg.device)
    runner.load(ckpt)
    return runner.get_inference_policy(device=vecenv.unwrapped.device), vecenv


def main() -> int:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args_cli.num_envs
    env = Mod4Env(cfg)
    env.reset()
    vecenv = RslRlVecEnvWrapper(env)
    policy, vecenv = build_runner(vecenv, args_cli.checkpoint)
    env = vecenv

    # ---- the keyboard device -----------------------------------------------------------------
    kb = None
    if not args_cli.headless:
        try:
            from isaaclab.devices.keyboard import Se2Keyboard, Se2KeyboardCfg
            kb = Se2Keyboard(Se2KeyboardCfg(v_x_sensitivity=1.0, v_y_sensitivity=0.5,
                                            omega_z_sensitivity=1.0))
            print("[play] KEYBOARD (Isaac Se2Keyboard): UP/DOWN arrows = forward/back | "
                  "LEFT/RIGHT arrows = strafe | Z / numpad-7 = yaw left | "
                  "numpad-9 = yaw right   (numpad 8/2/4/6 also work)")
        except Exception as exc:                       # no window / no input app
            print("[play] WARNING: keyboard unavailable (%s); the policy will idle" % exc)

    # the route controller must not fight the keyboard: take its command term and overwrite it
    term = None
    try:
        term = env.unwrapped.command_manager.get_term("twist")
    except Exception:
        pass

    height_cmd = float(args_cli.height_cmd)
    obs = env.get_observations() if hasattr(env, "get_observations") else None
    n = 0
    try:
        while True:
            if kb is not None:
                cmd = kb.advance()                     # (vx, vy, wz)
                if term is not None and hasattr(term, "command"):
                    with torch.no_grad():
                        term.command[:, 0] = float(cmd[0])
                        term.command[:, 1] = float(cmd[1])
                        term.command[:, 2] = float(cmd[2])
            if obs is None:
                obs = env.get_observations()
            with torch.no_grad():
                actions = policy(obs)
            obs, _, _, _ = env.step(actions)
            n += 1
            if n % 100 == 0:
                p = env.unwrapped.scene["robot"].data.root_pos_w[0] - env.unwrapped.scene.env_origins[0]
                print("[play] step %5d  pos=(%.2f, %.2f, %.2f)" % (n, p[0], p[1], p[2]), flush=True)
            if args_cli.steps and n >= args_cli.steps:
                break
    except KeyboardInterrupt:
        pass
    print("[play] ran %d steps" % n)
    env.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
