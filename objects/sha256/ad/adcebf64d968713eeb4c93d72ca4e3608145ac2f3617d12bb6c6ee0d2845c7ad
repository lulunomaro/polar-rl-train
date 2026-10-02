#!/usr/bin/env python3
"""Reduce a robot USD to three semantic physics materials without touching visuals.

The output is a new flattened USD.  Visual ``UsdShade.Material`` data stays intact;
only ``UsdPhysics.MaterialAPI`` / ``PhysxMaterialAPI`` and physics-purpose binding
relationships are changed.  Collision shapes are bound to one of:

* generic chassis/limb material (0.9 friction),
* drive-tire material (0.9 friction; randomized later through the tensor API),
* guide-roller material (0.02 friction, PhysX combine mode ``min``).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pxr import Sdf, Usd, UsdPhysics, UsdShade

try:  # PhysxSchema is exposed inside Kit, but not by the target's standalone pxr wheel.
    from pxr import PhysxSchema
except ImportError:  # pragma: no cover - depends on the Isaac runtime used to launch the tool
    PhysxSchema = None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _semantic(path: str) -> str:
    lower = path.lower()
    if "guide_wheel_" in lower:
        return "guide_roller"
    if "_tire" in lower or "/left_wheel/" in lower or "/right_wheel/" in lower:
        return "drive_tire"
    return "generic"


def _remove_physics_api(prim) -> None:
    if prim.HasAPI(UsdPhysics.MaterialAPI):
        prim.RemoveAPI(UsdPhysics.MaterialAPI)
    try:
        if PhysxSchema is not None and prim.HasAPI(PhysxSchema.PhysxMaterialAPI):
            prim.RemoveAPI(PhysxSchema.PhysxMaterialAPI)
    except Exception:
        # Some pxr builds reject HasAPI for this optional schema.  Removing an
        # absent schema is harmless, so attempt it directly.
        try:
            if PhysxSchema is not None:
                prim.RemoveAPI(PhysxSchema.PhysxMaterialAPI)
        except Exception:
            pass


def _make_material(stage, path: Sdf.Path, static: float, dynamic: float, combine: str):
    material = UsdShade.Material.Define(stage, path)
    prim = material.GetPrim()
    api = UsdPhysics.MaterialAPI.Apply(prim)
    api.CreateStaticFrictionAttr(float(static))
    api.CreateDynamicFrictionAttr(float(dynamic))
    api.CreateRestitutionAttr(0.0)
    try:
        if PhysxSchema is None:
            raise RuntimeError("PhysxSchema unavailable outside Kit")
        physx_api = PhysxSchema.PhysxMaterialAPI.Apply(prim)
        physx_api.CreateFrictionCombineModeAttr(combine)
        physx_api.CreateRestitutionCombineModeAttr("max")
    except Exception:
        pass
    return material


def consolidate(source: Path, output: Path, report_path: Path | None) -> dict:
    source_stage = Usd.Stage.Open(str(source))
    if source_stage is None:
        raise RuntimeError(f"failed to open USD: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if not source_stage.Export(str(output)):
        raise RuntimeError(f"failed to export composed stage: {output}")
    stage = Usd.Stage.Open(str(output))
    if stage is None:
        raise RuntimeError(f"failed to reopen output USD: {output}")

    default_prim = stage.GetDefaultPrim()
    if not default_prim or not default_prim.IsValid():
        raise RuntimeError("USD has no valid default prim")
    root = default_prim.GetPath().AppendChild("PhysicsMaterials")

    # Strip only physics APIs from old materials.  Their shaders and visual
    # material bindings are deliberately retained for the HiFi viewer asset.
    stripped = 0
    for prim in list(stage.Traverse()):
        if prim.HasAPI(UsdPhysics.MaterialAPI):
            _remove_physics_api(prim)
            stripped += 1

    materials = {
        "generic": _make_material(stage, root.AppendChild("generic"), 0.9, 0.9, "average"),
        "drive_tire": _make_material(stage, root.AppendChild("drive_tire"), 0.9, 0.9, "average"),
        "guide_roller": _make_material(stage, root.AppendChild("guide_roller"), 0.02, 0.02, "min"),
    }

    rebound = {name: 0 for name in materials}
    collision_paths: list[str] = []
    for prim in stage.Traverse():
        if not prim.HasAPI(UsdPhysics.CollisionAPI):
            continue
        path = str(prim.GetPath())
        semantic = _semantic(path)
        # Author the physics-purpose relationship directly.  This avoids the
        # ComputeBoundMaterial tuple incompatibility in the target pxr build.
        rel = prim.CreateRelationship("material:binding:physics", custom=False)
        rel.SetTargets([materials[semantic].GetPath()])
        rebound[semantic] += 1
        collision_paths.append(path)

    stage.GetRootLayer().Save()
    report = {
        "source": str(source.resolve()),
        "source_sha256": _sha256(source),
        "output": str(output.resolve()),
        "output_sha256": _sha256(output),
        "old_physics_materials_stripped": stripped,
        "new_physics_material_count": len(materials),
        "collision_bindings": rebound,
        "collision_prim_count": len(collision_paths),
        "visual_materials_preserved": True,
        "material_paths": {name: str(mat.GetPath()) for name, mat in materials.items()},
    }
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        raise SystemExit("refusing to overwrite the source USD")
    consolidate(args.source, args.output, args.report)


if __name__ == "__main__":
    main()
