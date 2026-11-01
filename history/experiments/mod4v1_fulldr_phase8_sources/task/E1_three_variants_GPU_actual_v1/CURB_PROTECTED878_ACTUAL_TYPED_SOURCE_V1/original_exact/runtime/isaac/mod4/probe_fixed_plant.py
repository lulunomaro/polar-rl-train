"""Verify the asset the TRAINING pipeline loads: fixed MOD4 USD limits + guide rollers.

Read-only probe.  Prints the resolved USD path, the PhysX DOF limits of the joints the
2026-09-12 fix extended (knee / rocker_pin / gas_slide), the guide-roller prim count and the
closure/mimic residuals after a short zero-action rollout on the delivered arena.

    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_fixed_plant.py --headless --num_envs 4 --steps 60
"""
import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

ap = argparse.ArgumentParser()
ap.add_argument("--num_envs", type=int, default=4)
ap.add_argument("--steps", type=int, default=60)
AppLauncher.add_app_launcher_args(ap)
args = ap.parse_args()
app = AppLauncher(args).app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402

WATCH = ("left_knee", "left_rocker_pin", "left_gas_slide",
         "right_knee", "right_rocker_pin", "right_gas_slide")


def main() -> None:
    print("[plant] USD in use      : %s" % mod4_task.USD_PATH, flush=True)
    print("[plant] contract joints : %d | mimics %d | filters %d"
          % (len(mod4_task.CONTRACT["joints"]), len(mod4_task.CONTRACT["mimics"]),
             len(mod4_task.CONTRACT["filters"])), flush=True)
    stop = mod4_task.CONTRACT.get("mechanical_stop", {})
    print("[plant] contract stop   : hip %s crank %s diff %s | %s"
          % (round(float(stop.get("hip_rad", float("nan"))), 6),
             round(float(stop.get("crank_rad", float("nan"))), 6),
             round(float(stop.get("input_difference_rad", float("nan"))), 6),
             "ABSENT" if not stop else "present"), flush=True)
    win = mod4_task.CONTRACT.get("training_window", {})
    print("[plant] training window : %s" % (win or "ABSENT"), flush=True)
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    env.reset()
    robot = env.scene["robot"]
    raw = robot.root_physx_view.get_dof_limits()
    if hasattr(raw, "cpu"):
        raw = raw.cpu()
    import numpy as np
    limits = np.asarray(raw, dtype=float)[0]
    names = list(robot.joint_names)
    for j in WATCH:
        i = names.index(j)
        print("[plant] %-18s physx limits [%+.5f, %+.5f] rad" % (j, float(limits[i, 0]),
                                                                 float(limits[i, 1])), flush=True)
    try:
        import omni.usd
        st = omni.usd.get_context().get_stage()
        guide = sum(1 for p in st.Traverse() if p.GetName().startswith("guide_wheel"))
        print("[plant] guide_wheel prims in stage: %d" % guide, flush=True)
    except Exception as exc:                                     # pragma: no cover
        print("[plant] guide-wheel scan failed: %r" % (exc,), flush=True)
    act = torch.zeros((env.num_envs, 6), device=env.device)
    worst_c = worst_m = 0.0
    for _ in range(args.steps):
        env.step(act)
        ce = mod4_task.closure_errors(env)
        me = mod4_task.mimic_errors(env)
        worst_c = max(worst_c, float(torch.stack(list(ce.values())).max()))
        worst_m = max(worst_m, float(torch.stack(list(me.values())).max()))
    print("[plant] %d steps: closure_max=%.5f m  mimic_max=%.5f rad"
          % (args.steps, worst_c, worst_m), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
