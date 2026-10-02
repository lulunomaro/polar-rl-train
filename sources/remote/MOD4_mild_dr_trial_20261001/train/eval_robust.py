"""Sim2real readiness check for the exported RMVehicle policy.

Re-runs the trained policy in mjlab with the deployment-realistic perturbations turned on
and reports survival / tracking / height error per condition:

  nominal   : trained distribution, corruption on
  noise     : doubled sensor noise
  delay     : 2 physical steps (4 ms) of actuator lag
  grip      : wheel friction x0.6 (wet / worn tyre)
  payload   : +6 kg on the chassis, CoM moved 3 cm forward
  push      : 0.8 m/s body-velocity impulses every 4 s
  rough_cmd : commands saturated at the deployment limits (|vx|<=1.8, |wz|<=1.0)
"""
import argparse
from copy import deepcopy
from dataclasses import asdict

import numpy as np
import torch

import rmvehicle
from mjlab.envs import ManagerBasedRlEnv
from mjlab.envs.mdp import dr
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

ap = argparse.ArgumentParser()
ap.add_argument("--task", default="RMVehicle-Flat-v0")
ap.add_argument("--checkpoint", required=True)
ap.add_argument("--num-envs", type=int, default=256)
ap.add_argument("--steps", type=int, default=1000, help="policy steps (50 Hz)")
args = ap.parse_args()

import mjlab.rl  # noqa: F401
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper

base_cfg = load_env_cfg(args.task, play=True)
agent_cfg = load_rl_cfg(args.task)


def make(cond):
    cfg = deepcopy(base_cfg)
    cfg.scene.num_envs = args.num_envs
    cfg.episode_length_s = args.steps / 50.0
    cfg.events.pop("reset_height", None)
    o = cfg.observations["actor"]
    o.enable_corruption = True
    for t in o.terms.values():
        if t.noise is not None:
            t.noise = type(t.noise)(n_min=t.noise.n_min * 2.0, n_max=t.noise.n_max * 2.0)
    if cond != "push":
        cfg.events.pop("push_robot", None)
    if cond == "nominal":
        pass
    elif cond == "noise":
        for t in o.terms.values():
            if t.noise is not None:
                t.noise = type(t.noise)(n_min=t.noise.n_min * 3.0, n_max=t.noise.n_max * 3.0)
    elif cond == "delay":
        for a in cfg.scene.entities["robot"].articulation.actuators:
            a.delay_min_lag, a.delay_max_lag, a.delay_hold_prob = 1, 2, 0.3
    elif cond == "grip":
        cfg.events["wheel_friction"].params["ranges"] = (0.45, 0.75)
    elif cond == "payload":
        cfg.events["base_mass"].params["ranges"] = (5.0, 8.0)
        cfg.events["base_com"].params["ranges"] = {0: (0.02, 0.05), 1: (-0.02, 0.02),
                                                   2: (-0.02, 0.02)}
    elif cond == "push":
        from mjlab.envs import mdp as em
        from mjlab.managers.event_manager import EventTermCfg
        from mjlab.managers.scene_entity_config import SceneEntityCfg
        cfg.events["push_robot"] = EventTermCfg(
            func=em.push_by_setting_velocity, mode="interval",
            interval_range_s=(3.0, 6.0),
            params={"velocity_range": {"x": (-0.8, 0.8), "y": (-0.4, 0.4),
                                       "roll": (-0.5, 0.5), "pitch": (-0.5, 0.5)},
                    "asset_cfg": SceneEntityCfg("robot")})
    elif cond == "rough_cmd":
        r = cfg.commands["twist"].ranges
        r.lin_vel_x, r.ang_vel_z = (-1.8, 1.8), (-1.0, 1.0)
    else:
        raise SystemExit("unknown condition " + cond)
    return cfg


conds = ["nominal", "noise", "delay", "grip", "payload", "push", "rough_cmd"]
print("%-10s %8s %8s %9s %9s %9s" % ("cond", "survive", "err_vx", "err_wz",
                                     "err_h", "|pitch|"))
for cond in conds:
    env = ManagerBasedRlEnv(cfg=make(cond), device="cuda:0")
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    acfg = asdict(agent_cfg)
    acfg["experiment_name"] = "eval"
    acfg["logger"] = "tensorboard"
    runner = MjlabOnPolicyRunner(env, acfg, log_dir=None, device="cuda:0")
    runner.load(args.checkpoint)
    policy = runner.get_inference_policy()
    obs = env.reset()[0]
    alive = torch.zeros(env.num_envs, device="cuda:0")
    ev = ew = eh = ep = 0.0
    n = 0
    for _ in range(args.steps):
        with torch.no_grad():
            action = policy(obs)
        obs, rew, dones, extras = env.step(action)
        alive += (torch.as_tensor(dones) == 0).float().flatten()
        cmd = env.unwrapped.command_manager.get_command("twist")
        v = env.unwrapped.scene["robot"].data.root_link_lin_vel_b
        w = env.unwrapped.scene["robot"].data.root_link_ang_vel_b
        from rmvehicle.mdp import measured_height, height_command
        h_err = (measured_height(env.unwrapped)
                 - height_command(env.unwrapped).squeeze(-1)).abs()
        g = env.unwrapped.scene["robot"].data.projected_gravity_b
        pitch = torch.asin(g[:, 0].clamp(-1, 1)).abs()
        ev += (v[:, 0] - cmd[:, 0]).abs().mean().item()
        ew += (w[:, 2] - cmd[:, 2]).abs().mean().item()
        eh += h_err.mean().item()
        ep += pitch.mean().item()
        n += 1
    print("%-10s %7.1f%% %8.3f %9.3f %9.3f %9.2f"
          % (cond, 100.0 * alive.sum().item() / (env.num_envs * n), ev / n, ew / n,
             eh / n, np.degrees(ep / n)))
    env.close()
