"""Record the mjlab-side settled standing state as the reference for the deployment
handover diff (docs/HOWTO.md section 21.2).  Uses the same construction path as
train/verify_skills.py so the policy, observation group and gains are identical."""
import json, os, sys
from dataclasses import asdict
import numpy as np, torch

ROOT = r"D:/claude2/fangzhen"
sys.path.insert(0, os.path.join(ROOT, "train/rmvehicle/src"))
import rmvehicle  # noqa: F401
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls

TASK = "RMVehicle-CC-Skills-v0"
CKPT = os.path.join(ROOT, "train/logs/rsl_rl/rm_cc_v12/2026-09-05_10-10-37/model_8696.pt")
DEV = "cuda:0"

cfg = load_env_cfg(TASK, play=True)
cfg.scene.num_envs = 16
cfg.observations["actor"].enable_corruption = False
for dead in ("push_robot", "jump_schedule", "reset_height"):
    cfg.events.pop(dead, None)
if "reset_base" in cfg.events:                      # deterministic, exactly qpos0
    cfg.events["reset_base"].params["pose_range"] = {"x": (0.0, 0.0), "y": (0.0, 0.0),
                                                     "yaw": (0.0, 0.0)}
    cfg.events["reset_base"].params["velocity_range"] = {
        k: (0.0, 0.0) for k in ("x", "y", "z", "roll", "pitch", "yaw")}

agent_cfg = load_rl_cfg(TASK)
env = ManagerBasedRlEnv(cfg=cfg, device=DEV)
runner_cls = load_runner_cls(TASK) or MjlabOnPolicyRunner
runner = runner_cls(RslRlVecEnvWrapper(env), asdict(agent_cfg), device=DEV)
runner.load(CKPT, load_cfg={"actor": True}, strict=True, map_location=DEV)
policy = runner.get_inference_policy(device=DEV)
E = env.unwrapped
robot = E.scene["robot"]
KEY = "policy" if "policy" in E.obs_buf else "actor"
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
la = {n: robot.joint_names.index(n) for n in LEG + WHL}

E.command_manager.get_term("twist").command[:] = 0.0
if hasattr(E, "_rm_height_cmd"):
    E._rm_height_cmd[:] = 0.22
env.reset()
for _ in range(300):                                # settle into the standing solution
    env.step(policy(E.obs_buf))
    if hasattr(E, "_rm_height_cmd"):
        E._rm_height_cmd[:] = 0.22
    if "twist" in E.command_manager.active_terms:
        E.command_manager.get_term("twist").command[:] = 0.0

rows = []
for _ in range(20):
    o = E.obs_buf[KEY][0].detach().cpu().numpy()
    a = policy(E.obs_buf)[0].detach().cpu().numpy()
    jp = robot.data.joint_pos[0].detach().cpu().numpy()
    jv = robot.data.joint_vel[0].detach().cpu().numpy()
    rows.append(dict(obs=o.tolist(), action=a.tolist(),
                     base_z=float(robot.data.root_link_pos_w[0, 2].cpu()),
                     leg_pos=[float(jp[la[n]]) for n in LEG],
                     wheel_vel=[float(jv[la[n]]) for n in WHL]))
    env.step(policy(E.obs_buf))
    if hasattr(E, "_rm_height_cmd"):
        E._rm_height_cmd[:] = 0.22
    E.command_manager.get_term("twist").command[:] = 0.0

out = os.path.join(ROOT, "docs/audit/mjlab_handover.json")
json.dump(rows, open(out, "w"), indent=1)
A = np.array([r["obs"] for r in rows]); B = np.array([r["action"] for r in rows])
z = np.array([r["base_z"] for r in rows])
print("mjlab settled standing (16 envs, env0, commands all zero, height cmd 0.22)")
print("  base_z            mean %.4f  [%.4f, %.4f]" % (z.mean(), z.min(), z.max()))
print("  true leg pos      mean %s" % np.round(np.mean([r["leg_pos"] for r in rows], 0), 4).tolist())
print("  obs[0:4]  cmd     mean %s" % np.round(A[:, 0:4].mean(0), 4).tolist())
print("  obs[4:7]  gyro*0.5 mean %s" % np.round(A[:, 4:7].mean(0), 4).tolist())
print("  obs[7:10] proj g  mean %s" % np.round(A[:, 7:10].mean(0), 4).tolist())
print("  obs[10:14] legpos mean %s" % np.round(A[:, 10:14].mean(0), 4).tolist())
print("  obs[16:20] legvel mean %s" % np.round(A[:, 16:20].mean(0), 4).tolist())
print("  obs[20:22] whlvel mean %s" % np.round(A[:, 20:22].mean(0), 4).tolist())
print("  obs[22:28] lastact mean %s" % np.round(A[:, 22:28].mean(0), 4).tolist())
print("  obs[28:35] onehot  mean %s" % np.round(A[:, 28:35].mean(0), 3).tolist())
print("  action      mean %s" % np.round(B.mean(0), 4).tolist())
print("  leg targets = a*0.5 -> %s rad ; wheel targets = a*10 -> %s rad/s" %
      (np.round(B.mean(0)[:4] * 0.5, 4).tolist(), np.round(B.mean(0)[4:6] * 10.0, 3).tolist()))
print("wrote", out)