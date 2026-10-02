"""Where does the tunnel policy actually go?  Prints per-env x/y/z every N steps.

The fixed-plant tunnel run reaches full-length episodes and tracks its command, yet the route
progress stays ~0.03 m/s, so the reward log alone cannot say whether the robot is stuck, turned
around or creeping.  This probe loads a checkpoint and dumps the trajectory.

    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_tunnel_traj.py --headless \\
        --checkpoint <ckpt> --num_envs 4 --steps 600 --every 50
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--steps", type=int, default=600)
parser.add_argument("--every", type=int, default=50)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402
from importlib import metadata  # noqa: E402
from isaaclab_rl.rsl_rl import (RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg,
                                RslRlPpoAlgorithmCfg, RslRlVecEnvWrapper,
                                handle_deprecated_rsl_rl_cfg)  # noqa: E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    vec = RslRlVecEnvWrapper(env, clip_actions=6.0)
    rcfg = RslRlOnPolicyRunnerCfg(
        seed=0, device="cuda:0", num_steps_per_env=24, max_iterations=1, save_interval=1,
        experiment_name="traj", run_name="traj", clip_actions=6.0, check_for_nan=True,
        obs_groups={"actor": ["policy"], "critic": ["critic"]},
        policy=RslRlPpoActorCriticCfg(init_noise_std=0.3, actor_hidden_dims=[256, 128, 64],
                                      critic_hidden_dims=[256, 128, 64], activation="elu"),
        algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=1.0, use_clipped_value_loss=True,
                                       clip_param=0.2, entropy_coef=0.005, num_learning_epochs=5,
                                       num_mini_batches=4, learning_rate=1e-4, schedule="fixed",
                                       gamma=0.99, lam=0.95, desired_kl=0.01, max_grad_norm=1.0))
    rcfg = handle_deprecated_rsl_rl_cfg(rcfg, metadata.version("rsl-rl-lib"))
    runner = OnPolicyRunner(vec, rcfg.to_dict(), log_dir=None, device=rcfg.device)
    runner.load(args.checkpoint)
    policy = runner.get_inference_policy(device=vec.unwrapped.device)
    robot = env.scene["robot"]
    term = env.command_manager.get_term("twist")
    obs = vec.get_observations()
    print("[traj] step | per-env local x (m) | command vx | height cmd", flush=True)
    for step in range(args.steps + 1):
        if step % args.every == 0:
            loc = robot.data.root_pos_w - env.scene.env_origins
            yaw = robot.data.root_quat_w
            h = getattr(env, "_mod4_height_cmd", None)
            st = getattr(env, "_mod4_tunnel_state", None)
            print("[traj] %4d | x %s | y %s | z %s | cmd %s | h %s | stage %s"
                  % (step,
                     " ".join("%+.2f" % v for v in loc[:, 0]),
                     " ".join("%+.2f" % v for v in loc[:, 1]),
                     " ".join("%+.2f" % v for v in loc[:, 2]),
                     " ".join("%+.2f" % v for v in term.command[:, 0]),
                     " ".join("%.3f" % v for v in (h[:, 0] if h is not None else [])) or "-",
                     " ".join(str(int(v)) for v in st) if st is not None else "-"), flush=True)
        if step == args.steps:
            break
        with torch.inference_mode():
            actions = policy(obs)
        obs, _, dones, _ = vec.step(actions)
        policy.reset(dones)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
