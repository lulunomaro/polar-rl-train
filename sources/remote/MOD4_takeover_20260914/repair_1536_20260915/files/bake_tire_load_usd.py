"""Create a private USD whose two drive-tyre colliders include static load deflection."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from pxr import Usd

ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True)
ap.add_argument("--output", required=True)
ap.add_argument("--add-mm", type=float, default=1.2)
args = ap.parse_args()

src, dst = Path(args.input).resolve(), Path(args.output).resolve()
if src == dst:
    raise ValueError("output must be a derived asset, not the source USD")
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dst)
stage = Usd.Stage.Open(str(dst))
if stage is None:
    raise RuntimeError(f"cannot open copied USD: {dst}")
changed = []
add_m = args.add_mm / 1000.0
for prim in stage.Traverse():
    if "_tire" not in str(prim.GetPath()) or not prim.HasAPI("PhysicsCollisionAPI"):
        continue
    attr = prim.GetAttribute("radius")
    old = attr.Get() if attr else None
    if old is None:
        raise RuntimeError(f"tyre collider has no radius: {prim.GetPath()}")
    new = float(old) + add_m
    attr.Set(new)
    changed.append((str(prim.GetPath()), float(old), new))
if len(changed) != 2:
    raise RuntimeError(f"expected exactly two drive-tyre colliders, found {len(changed)}")
stage.GetRootLayer().Save()

check = Usd.Stage.Open(str(dst))
verified = []
for prim in check.Traverse():
    if "_tire" in str(prim.GetPath()) and prim.HasAPI("PhysicsCollisionAPI"):
        verified.append((str(prim.GetPath()), float(prim.GetAttribute("radius").Get())))
if len(verified) != 2:
    raise RuntimeError("derived USD verification failed")
for path, old, new in changed:
    print(f"{path}: radius {old:.7f} -> {new:.7f} m")
print(dst)
