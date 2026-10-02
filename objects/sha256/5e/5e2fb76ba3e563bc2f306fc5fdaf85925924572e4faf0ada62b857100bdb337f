"""Regenerate import_contract.json for the rolling-idler asset, reading the NEW USD."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

from pxr import Usd, UsdPhysics, UsdGeom

DELIVERED = Path("incoming/mod4_fixed_20260912/chassis_mod4/isaac")
DEFAULT_USD = Path("incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd")
DST = Path("incoming/mod4_rolling_20260913/chassis_mod4/isaac/import_contract.json")
BEARING_DAMPING = 1.0e-4      # TO BE CALIBRATED - no bench data
ROLLER_MASS = 0.0025


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--usd", default=str(DEFAULT_USD))
    ap.add_argument("--dst", default=str(DST))
    args = ap.parse_args()
    usd = Path(args.usd)

    base = json.loads((DELIVERED / "import_contract.json").read_text(encoding="utf8"))
    st = Usd.Stage.Open(str(usd), Usd.Stage.LoadAll)

    bodies, mass_of = [], {}
    for prim in st.Traverse():
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            m = prim.GetAttribute("physics:mass")
            mv = float(m.Get()) if m and m.Get() is not None else None
            bodies.append(prim.GetName())
            mass_of[prim.GetName()] = mv
    # body entries must keep every field the task reads (neutral_quat_wxyz is used by the
    # mimic error term), so start from the delivered entry and only refresh what moved.
    def body_entry(name):
        e = dict(base["bodies"].get(name, {}))
        e["mass_kg"] = mass_of.get(name)
        if name.startswith("guide_roller_"):
            idx = name.rsplit("_", 1)[-1]
            pos = [float(v) for v in base["geometry"]["guide_wheel_%s" % idx]["position_m"]]
            e.update({"com_m": [0.0, 0.0, 0.0],
                      "diagonal_inertia_kg_m2": [1.9396e-07, 2.8125e-07, 1.9396e-07],
                      "principal_axes_wxyz": [1.0, 0.0, 0.0, 0.0],
                      "neutral_position_m": pos,
                      "neutral_quat_wxyz": [1.0, 0.0, 0.0, 0.0],
                      "note": "idler roller on a passive revolute joint; mass/inertia derived "
                              "from the delivered body mass and the CAD cylinder, NOT measured"})
        if "neutral_quat_wxyz" not in e:
            e["neutral_quat_wxyz"] = [1.0, 0.0, 0.0, 0.0]
        return e

    def geom_new(key):
        for prim in st.Traverse():
            if prim.GetName() == key:
                xf = UsdGeom.Xformable(prim)
                for op in xf.GetOrderedXformOps():
                    if op.GetOpName() == "xformOp:translate":
                        return [float(v) for v in op.Get()]
        return [0.0, 0.0, 0.0]

    tree, closures, fixed = {}, {}, {}
    for prim in st.Traverse():
        tn = prim.GetTypeName()
        rel0 = prim.GetRelationship("physics:body0")
        rel1 = prim.GetRelationship("physics:body1")
        b0 = [str(t).split("/")[-1] for t in rel0.GetTargets()] if rel0 and rel0.GetTargets() else []
        b1 = [str(t).split("/")[-1] for t in rel1.GetTargets()] if rel1 and rel1.GetTargets() else []
        if not (b0 and b1):
            continue
        name = prim.GetName()
        if tn == "PhysicsSphericalJoint":
            # keep the delivered entry verbatim (anchors + any extra field the task reads) and
            # only refresh the anchors from the USD when the prim moved
            entry = dict(base["closures"].get(name, {}))
            entry.update({"body0": b0[0], "body1": b1[0],
                          "anchor0_m": [float(v) for v in prim.GetAttribute("physics:localPos0").Get()],
                          "anchor1_m": [float(v) for v in prim.GetAttribute("physics:localPos1").Get()]})
            closures[name] = entry
        elif tn == "PhysicsFixedJoint":
            fixed[name] = {"body0": b0[0], "body1": b1[0]}
        elif tn in ("PhysicsRevoluteJoint", "PhysicsPrismaticJoint"):
            lp0 = prim.GetAttribute("physics:localPos0").Get()
            lp1 = prim.GetAttribute("physics:localPos1").Get()
            def _q(q):
                if q is None:
                    return None
                try:
                    return [float(v) for v in q]
                except TypeError:
                    im = q.GetImaginary()
                    return [float(q.GetReal()), float(im[0]), float(im[1]), float(im[2])]
            lr0 = _q(prim.GetAttribute("physics:localRot0").Get())
            lr1 = _q(prim.GetAttribute("physics:localRot1").Get())
            entry = {"parent": b0[0], "child": b1[0],
                     "type": "hinge" if tn == "PhysicsRevoluteJoint" else "slide",
                     "local_pos0": [float(v) for v in lp0],
                     "local_pos1": [float(v) for v in lp1],
                     "local_rot0": lr0,
                     "local_rot1": lr1}
            if name.startswith("guide_roller_"):
                drv = UsdPhysics.DriveAPI.Get(prim, "angular")
                damping = float(drv.GetDampingAttr().Get()) if drv else None
                entry.update({"limits_si": None, "armature": 0.0,
                              "damping_si": damping, "passive": True, "driven": False,
                              "note": "idler roller on bearings; damping is the rolling loss and is "
                                      "TO BE CALIBRATED (no bench measurement exists)"})
            else:
                old = base["joints"].get(name, {})
                entry.update({k: old[k] for k in ("limits_si", "armature", "damping_si") if k in old})
            tree[name] = entry

    geom = dict(base["geometry"])
    for i in range(8):
        key = "guide_wheel_%02d" % i
        if key in geom:
            g = dict(geom[key])
            g["body"] = "guide_roller_%02d" % i
            geom[key] = g

    meshes = [p for p in st.Traverse() if p.GetTypeName() == "Mesh"]
    cols = [p for p in st.Traverse() if p.GetTypeName() in ("Cylinder", "Cube", "Sphere", "Capsule")]

    out = dict(base)
    out["format_version"] = base.get("format_version")
    out["model_kind"] = "mod4_rolling_idlers"
    out["source_usd_sha256"] = sha256(usd)
    out["source_usd_path"] = str(usd)
    out["derived_from"] = {"usd": str(DELIVERED / "robot.usd"),
                           "usd_sha256": sha256(DELIVERED / "robot.usd"),
                           "builder": "incoming/mod4_rolling_20260913/tools/build_rolling_rollers_usd.py"}
    out["bodies"] = {b: body_entry(b) for b in sorted(bodies)}
    out["joints"] = tree
    out["closures"] = closures
    out["fixed_joints"] = fixed
    out["geometry"] = geom
    out["articulation_joint_count"] = len(tree)
    out["visual_instance_count"] = len(meshes)
    out["collision_primitive_count"] = len(cols)
    out["roller_joints"] = {k: v for k, v in sorted(tree.items()) if k.startswith("guide_roller_")}
    out["roller_parameters"] = {
        "mass_kg_each": ROLLER_MASS,
        "mass_source": "delivered guide_rollers body mass 0.02 kg / 8 (derived, NOT measured)",
        "inertia_kg_m2": {"spin_about_vehicle_y": 2.8125e-07, "transverse": 1.9396e-07},
        "inertia_source": "solid cylinder r=0.015 m, h=0.016 m (derived, NOT measured)",
        "bearing_damping_n_m_s_per_rad": BEARING_DAMPING,
        "bearing_damping_source": "TO BE CALIBRATED - no bench data",
        "collision_friction": 0.9,
    }
    out["mechanical_stop"] = base["mechanical_stop"]
    out["training_window"] = base["training_window"]
    out["spawn_height_m"] = base["spawn_height_m"]
    out["runtime_tested"] = False

    Path(args.dst).write_text(json.dumps(out, indent=1), encoding="utf8")
    print("[contract] usd=%s sha=%s" % (usd, out["source_usd_sha256"][:16]))
    print("[contract] bodies=%d tree_joints=%d closures=%d fixed=%d colliders=%d meshes=%d"
          % (len(bodies), len(tree), len(closures), len(fixed), len(cols), len(meshes)))
    print("[contract] actuated=%s" % out["actuated_joint_names"])
    print("[contract] roller joints=%d -> %s" % (len(out["roller_joints"]),
                                                 sorted(out["roller_joints"])[:3]))
    print("[contract] wrote %s sha256=%s" % (args.dst, sha256(Path(args.dst))[:16]))
    ok = (len(bodies) == 31 and len(tree) == 30 and len(closures) == 6 and not fixed
          and len(cols) == 34 and len(out["roller_joints"]) == 8)
    print("[contract] %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())