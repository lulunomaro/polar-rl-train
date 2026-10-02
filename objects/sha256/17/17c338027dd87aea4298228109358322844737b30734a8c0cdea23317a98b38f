import os, sys, json
sys.path.insert(0, r"D:/claude2/fangzhen/train/rmvehicle/src")
import rmvehicle  # noqa
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg
for task in ("RMVehicle-CC-Field-v0", "RMVehicle-CC-Skills-v0"):
    cfg = load_env_cfg(task, play=False)
    tw = cfg.commands["twist"].ranges
    print("%-24s ang_vel_z=%s  lin_vel_x=%s" % (task, tuple(tw.ang_vel_z), tuple(tw.lin_vel_x)))
    ev = sorted(cfg.events.keys())
    print("   events:", ", ".join(ev))
    w = {k: getattr(t, "weight", None) for k, t in cfg.rewards.items()}
    print("   track_ang_vel weight=%s std=%s" % (w.get("track_ang_vel"),
          cfg.rewards["track_ang_vel"].params.get("std")))
    print("   wheel action scale =", cfg.actions["wheel_joint_vel"].scale)