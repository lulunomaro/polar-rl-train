#!/usr/bin/env python3
"""Audit collision/physics-material bindings in one composed USD stage.

Run with the Python environment bundled with Isaac Sim so ``pxr`` is available.
The script is read-only and emits both a concise text summary and optional JSON.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from pxr import Usd, UsdPhysics, UsdShade


def _bound_targets(prim) -> list[str]:
    targets: list[str] = []
    for rel_name in ("material:binding:physics", "material:binding"):
        rel = prim.GetRelationship(rel_name)
        if rel:
            targets.extend(str(path) for path in rel.GetTargets())
    return list(dict.fromkeys(targets))


def audit(path: Path) -> dict:
    stage = Usd.Stage.Open(str(path))
    if stage is None:
        raise RuntimeError(f"failed to open USD: {path}")

    material_prims: list[str] = []
    physics_materials: list[dict] = []
    collision_prims: list[str] = []
    bindings: Counter[str] = Counter()
    binding_examples: dict[str, list[str]] = defaultdict(list)
    semantic_colliders: Counter[str] = Counter()

    for prim in stage.Traverse():
        prim_path = str(prim.GetPath())
        if prim.IsA(UsdShade.Material):
            material_prims.append(prim_path)
        if prim.HasAPI(UsdPhysics.MaterialAPI):
            api = UsdPhysics.MaterialAPI(prim)
            physics_materials.append(
                {
                    "path": prim_path,
                    "static_friction": api.GetStaticFrictionAttr().Get(),
                    "dynamic_friction": api.GetDynamicFrictionAttr().Get(),
                    "restitution": api.GetRestitutionAttr().Get(),
                    "schemas": list(prim.GetAppliedSchemas()),
                }
            )
        if not prim.HasAPI(UsdPhysics.CollisionAPI):
            continue
        collision_prims.append(prim_path)
        lower = prim_path.lower()
        if "guide_wheel_" in lower:
            semantic_colliders["guide_roller"] += 1
        elif "_tire" in lower or "/left_wheel/" in lower or "/right_wheel/" in lower:
            semantic_colliders["drive_tire"] += 1
        else:
            semantic_colliders["generic"] += 1
        for target in _bound_targets(prim):
            bindings[target] += 1
            if len(binding_examples[target]) < 5:
                binding_examples[target].append(prim_path)

    return {
        "usd": str(path.resolve()),
        "default_prim": str(stage.GetDefaultPrim().GetPath()) if stage.GetDefaultPrim() else None,
        "material_prim_count": len(material_prims),
        "physics_material_count": len(physics_materials),
        "collision_prim_count": len(collision_prims),
        "physics_binding_count": sum(bindings.values()),
        "unique_bound_material_count": len(bindings),
        "semantic_colliders": dict(semantic_colliders),
        "physics_materials": physics_materials,
        "bound_materials": [
            {"path": target, "binding_count": count, "examples": binding_examples[target]}
            for target, count in bindings.most_common()
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("usd", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = audit(args.usd)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
