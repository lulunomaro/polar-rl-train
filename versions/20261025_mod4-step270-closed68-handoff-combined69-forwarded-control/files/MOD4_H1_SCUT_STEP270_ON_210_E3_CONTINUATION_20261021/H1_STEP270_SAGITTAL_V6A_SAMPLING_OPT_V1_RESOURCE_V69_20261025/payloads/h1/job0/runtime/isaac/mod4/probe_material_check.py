"""Does the runtime stage really carry the idler materials we wrote into the derived USD?

Prints: (1) mod4_task.USD_PATH, (2) the USD references on the spawned robot prim,
(3) for every guide_wheel_* collider, the material bound for physics and its friction
values + combine mode.  No GPU work beyond a 1-env scene, ~40 s.

  RM_MOD4_USD=<usd> python isaac/mod4/probe_material_check.py --num_envs 1
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=1)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402
from pxr import Usd, UsdPhysics, UsdShade  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def bound(prim):
    out = []
    rel = prim.GetRelationship("material:binding:physics")
    if rel:
        out += [str(t) for t in rel.GetTargets()]
    try:
        res = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial("physics")
        mat = res[0] if isinstance(res, (tuple, list)) else res
        if mat is not None and mat.GetPrim().IsValid():
            out.append(str(mat.GetPath()))
    except Exception as exc:
        out.append("ERR %r" % (exc,))
    return out


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    mod4_task.attach_rmuc2026_terrain(cfg)
    env = Mod4Env(cfg=cfg)
    env.reset()
    print("[mat] mod4_task.USD_PATH =", mod4_task.USD_PATH, flush=True)
    stage = env.sim.stage
    root = stage.GetPrimAtPath("/World/envs/env_0/Robot")
    for p in (root, root.GetParent()):
        if p and p.IsValid():
            for a in p.GetMetadata("references").GetAddedOrExplicitItems() if False else []:
                pass
            refs = p.GetMetadata("references")
            print("[mat] %s references=%s" % (p.GetPath(), refs), flush=True)
    n = 0
    for prim in stage.Traverse():
        if "guide_wheel_" not in prim.GetPath().pathString:
            continue
        n += 1
        if n > 2:
            break
        mats = bound(prim)
        print("[mat] %s -> %s" % (prim.GetPath().pathString, mats), flush=True)
        for mp in mats:
            m = stage.GetPrimAtPath(mp)
            if not m or not m.IsValid():
                continue
            fa = m.GetAttribute("physics:staticFriction")
            fd = m.GetAttribute("physics:dynamicFriction")
            cm = m.GetAttribute("physxMaterial:frictionCombineMode")
            print("[mat]    %s static=%s dynamic=%s combine=%s" % (
                mp, fa.Get() if fa else None, fd.Get() if fd else None, cm.Get() if cm else None),
                flush=True)
    print("[mat] guide colliders seen=%d" % min(n, 3), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()