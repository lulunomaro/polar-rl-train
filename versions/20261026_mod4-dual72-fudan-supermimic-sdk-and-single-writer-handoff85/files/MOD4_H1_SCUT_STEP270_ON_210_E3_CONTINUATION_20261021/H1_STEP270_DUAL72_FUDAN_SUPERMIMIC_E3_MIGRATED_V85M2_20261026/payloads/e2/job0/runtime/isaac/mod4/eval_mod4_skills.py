r"""Deterministic evaluation of a MOD4 Isaac checkpoint against the three skills.

Loads a PPO checkpoint, runs the policy with NO exploration noise, and measures what the
skill terms were built for:

  小陀螺  yaw-rate tracking error over steps with |cmd| > 1 rad/s, peak |wz| while upright
  过洞    how many tunnel-lane environments actually cross the opening while below the beam
  飞坡    airborne-with-forward-speed samples, peak forward speed in the air, upright landings

    .venv-isaaclab\Scripts\python.exe isaac\mod4\eval_mod4_skills.py ^
        --checkpoint logs\isaac_mod4\<run>\model_500.pt --num_envs 64 --steps 1000 ^
        --report docs\eval_mod4_skills_500.json
"""
from __future__ import annotations

import argparse
import json
import sys
from importlib import metadata
from pathlib import Path

THIS = Path(__file__).resolve().parent
REPO = THIS.parents[1]
sys.path.insert(0, str(THIS))

parser = argparse.ArgumentParser(description="MOD4 Isaac skill evaluation")
parser.add_argument("--checkpoint", type=str, required=True)
parser.add_argument("--num_envs", type=int, default=64)
parser.add_argument("--steps", type=int, default=1000)
parser.add_argument("--seed", type=int, default=1234)
parser.add_argument("--steps_per_env", type=int, default=24)
parser.add_argument("--report", type=str, default="")
from isaaclab.app import AppLauncher  # noqa: E402

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402
from isaaclab.envs import ManagerBasedRLEnv  # noqa: E402
from isaaclab.managers import SceneEntityCfg  # noqa: E402
from isaaclab_rl.rsl_rl import (  # noqa: E402
    RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg,
    RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg)
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

import mod4_task  # noqa: E402
import skills_isaac as skills  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def runner_config() -> RslRlOnPolicyRunnerCfg:
    """Must mirror train_mod4_ppo.runner_config or the checkpoint will not load."""
    return RslRlOnPolicyRunnerCfg(
        seed=args.seed,
        device=args.device,
        num_steps_per_env=args.steps_per_env,
        max_iterations=1,
        save_interval=1,
        experiment_name="mod4_isaac_eval",
        run_name="eval",
        clip_actions=6.0,
        check_for_nan=True,
        policy=RslRlPpoActorCriticCfg(
            init_noise_std=1.0, actor_hidden_dims=[256, 128, 64],
            critic_hidden_dims=[256, 128, 64], activation="elu"),
        algorithm=RslRlPpoAlgorithmCfg(
            value_loss_coef=1.0, use_clipped_value_loss=True, clip_param=0.2,
            entropy_coef=0.005, num_learning_epochs=5, num_mini_batches=4,
            learning_rate=1.0e-4, schedule="fixed", gamma=0.99,
            lam=0.95, desired_kl=0.01, max_grad_norm=1.0),
    )


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    cfg.seed = args.seed
    env = Mod4Env(cfg=cfg)   # same per-step event mode as training
    info = mod4_task.FIELD_INFO
    tunnel = dict(entry=info["tunnel_entry"], exit=info["tunnel_exit"],
                  lane_y=info["tunnel_spawn"][1], hole_h=info["tunnel_hole_m"][0])
    robot = env.scene["robot"]

    vec_env = RslRlVecEnvWrapper(env, clip_actions=6.0)
    rcfg = runner_config()
    rcfg = handle_deprecated_rsl_rl_cfg(rcfg, metadata.version("rsl-rl-lib"))
    runner = OnPolicyRunner(vec_env, rcfg.to_dict(), log_dir=None, device=rcfg.device)
    runner.load(args.checkpoint)
    print("[eval] loaded %s" % args.checkpoint, flush=True)
    policy = runner.get_inference_policy(device=env.device)
    obs = vec_env.get_observations()

    dev = env.device
    n = env.num_envs
    in_lane_ever = torch.zeros(n, dtype=torch.bool, device=dev)
    tunnel_cross = torch.zeros(n, dtype=torch.bool, device=dev)
    tunnel_enter = torch.zeros(n, dtype=torch.bool, device=dev)
    max_x_lane = torch.full((n,), -10.0, device=dev)
    flight_samples = torch.zeros(n, device=dev)
    max_flight_vx = torch.zeros(n, device=dev)
    landings = torch.zeros(n, device=dev)
    yaw_err_sum = torch.zeros((), device=dev)
    yaw_err_cnt = torch.zeros((), device=dev)
    peak_wz = torch.zeros((), device=dev)
    reward_sum = 0.0
    term_counts: dict[str, float] = {}
    prev_air = torch.zeros(n, device=dev)

    for step in range(args.steps):
        with torch.inference_mode():
            actions = policy(obs)
        obs, rewards, dones, extras = vec_env.step(actions)
        reward_sum += float(rewards.mean().item())
        for key, value in extras.get("log", {}).items():
            if "Episode_Termination" in key:
                term_counts[key] = float(value)
        loc = robot.data.root_pos_w - env.scene.env_origins
        z = loc[:, 2]
        low = z <= (tunnel["hole_h"] + 0.05)
        in_lane = (loc[:, 1] - tunnel["lane_y"]).abs() < 0.45
        in_lane_ever |= in_lane
        tunnel_enter |= in_lane & low & (loc[:, 0] >= tunnel["entry"]) & (loc[:, 0] <= tunnel["exit"])
        tunnel_cross |= in_lane & low & (loc[:, 0] > info["tunnel_success"])
        max_x_lane = torch.where(in_lane, torch.maximum(max_x_lane, loc[:, 0]), max_x_lane)
        forces = env.scene.sensors["wheel_contact"].data.net_forces_w
        if hasattr(forces, "torch"):
            forces = forces.torch
        air = (forces.norm(dim=-1).max(dim=1).values < 1.0)
        vx = robot.data.root_lin_vel_b[:, 0]
        fast_air = air & (vx > 0.8)
        flight_samples += fast_air.float()
        max_flight_vx = torch.maximum(max_flight_vx, torch.where(air, vx, torch.zeros_like(vx)))
        landings += (prev_air > 0.5).float() * (air < 0.5).float() * (skills.tilt_deg(env) < 30.0).float()
        prev_air = air.float()
        cmd_wz = env.command_manager.get_command("twist")[:, 2]
        active = cmd_wz.abs() > 1.0
        if bool(active.any()):
            yaw_err_sum = yaw_err_sum + (robot.data.root_ang_vel_b[active, 2] - cmd_wz[active]).abs().sum()
            yaw_err_cnt = yaw_err_cnt + active.sum()
        peak_wz = torch.maximum(peak_wz, robot.data.root_ang_vel_b[:, 2].abs().max())
        policy.reset(dones)

    report = {
        "checkpoint": args.checkpoint,
        "num_envs": int(n),
        "steps": args.steps,
        "mean_reward": reward_sum / max(1, args.steps),
        "episode_len_steps_mean": float(env.episode_length_buf.float().mean().item()),
        "terminations": term_counts,
        "gyro": {
            "yaw_track_err_mean_rad_s": float(yaw_err_sum / torch.clamp(yaw_err_cnt, min=1.0)),
            "yaw_cmd_active_steps": float(yaw_err_cnt),
            "peak_abs_wz_rad_s": float(peak_wz),
        },
        "tunnel": {
            "envs_in_lane_ever": int(in_lane_ever.sum()),
            "envs_entered_opening": int(tunnel_enter.sum()),
            "envs_crossed_while_low": int(tunnel_cross.sum()),
            "max_local_x_in_lane": float(max_x_lane.max()),
        },
        "flight": {
            "fast_airborne_samples": float(flight_samples.sum()),
            "envs_with_fast_air": int((flight_samples > 0).sum()),
            "max_air_vx": float(max_flight_vx.max()),
            "upright_landings": float(landings.sum()),
        },
    }
    print("[eval] " + json.dumps(report, indent=2), flush=True)
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf8")
    env.close()


if __name__ == "__main__":
    import traceback
    try:
        main()
    except BaseException:
        (REPO / "isaac" / "mod4" / "eval_crash.txt").write_text(traceback.format_exc(), encoding="utf8")
        print(traceback.format_exc(), flush=True)
        raise
    finally:
        app.close()