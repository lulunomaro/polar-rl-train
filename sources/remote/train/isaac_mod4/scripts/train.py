"""Train the MOD4 Isaac Lab task with rsl_rl.

Run (Windows, from the workspace root):
  .venv-isaaclab\\Scripts\\python.exe train\\isaac_mod4\\scripts\\train.py --num_envs 4096 --headless

Run (target machine, 4090):
  /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python train/isaac_mod4/scripts/train.py --num_envs 4096 --headless
"""
from __future__ import annotations

import argparse
import importlib.metadata
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from isaaclab.app import AppLauncher  # noqa: E402

parser = argparse.ArgumentParser(description="Train the MOD4 chassis in Isaac Lab.")
parser.add_argument("--task", type=str, default="Mod4-Isaac-Flat-v0")
parser.add_argument("--num_envs", type=int, default=4096)
parser.add_argument("--max_iterations", type=int, default=None)
parser.add_argument("--seed", type=int, default=None)
parser.add_argument("--run_name", type=str, default="mod4_flat")
parser.add_argument("--log_root", type=str, default=str(WORKSPACE / "train" / "logs_isaac"))
parser.add_argument("--resume", action="store_true", default=False)
parser.add_argument("--checkpoint", type=str, default=None)
parser.add_argument("--video", action="store_true", default=False)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = args.headless or not args.video

launcher = AppLauncher(args)
app = launcher.app

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402

import mod4_isaac  # noqa: E402,F401  (registers Mod4-Isaac-Flat-v0)
from isaaclab.envs import ManagerBasedRLEnv  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg  # noqa: E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

from mod4_isaac.env_cfg import Mod4FlatEnvCfg  # noqa: E402
from mod4_isaac.rl_cfg import Mod4FlatPPORunnerCfg  # noqa: E402


def main() -> None:
    env_cfg = Mod4FlatEnvCfg()
    env_cfg.scene.num_envs = args.num_envs
    env_cfg.sim.device = args.device

    agent_cfg = Mod4FlatPPORunnerCfg()
    agent_cfg.device = args.device
    if args.max_iterations is not None:
        agent_cfg.max_iterations = args.max_iterations
    if args.seed is not None:
        agent_cfg.seed = args.seed
    agent_cfg.experiment_name = args.run_name
    # rsl_rl >= 5 wants MLPModel cfgs; this migrates the legacy stochastic fields away.
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, importlib.metadata.version("rsl-rl-lib"))

    torch.manual_seed(agent_cfg.seed)

    log_dir = Path(args.log_root) / args.run_name / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir.mkdir(parents=True, exist_ok=True)
    print("[mod4-isaac] log_dir = %s" % log_dir, flush=True)
    print("[mod4-isaac] num_envs = %d  dt = %s  decimation = %d  policy_hz = %.1f" % (
        env_cfg.scene.num_envs, env_cfg.sim.dt, env_cfg.decimation, 1.0 / (env_cfg.sim.dt * env_cfg.decimation)))

    env = ManagerBasedRLEnv(cfg=env_cfg)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=str(log_dir), device=agent_cfg.device)
    if args.checkpoint:
        runner.load(args.checkpoint)
    runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
    env.close()


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        import traceback
        traceback.print_exc()
        raise
    finally:
        app.close()
