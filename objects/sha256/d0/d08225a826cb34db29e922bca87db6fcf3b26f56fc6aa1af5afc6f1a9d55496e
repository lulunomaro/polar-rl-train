"""Build the ROLLING-IDLER MOD4 asset (2026-09-13).

WHY
---
The delivered USD welds all eight dog-hole guide rollers into ONE rigid body
(`/Robot/links/guide_rollers` + a fixed joint).  PhysX therefore models them as eight
rigid sliders: in the only low pose that fits the 247.2 mm opening they carry the whole
chassis while the drive tyres hang ~1.8 mm above the floor, so the contact drag stops the
robot instead of letting it roll.  The real chassis has eight idler wheels on bearings.

WHAT THIS TOOL WRITES (into a NEW version directory; the delivered asset stays byte-identical)
----------------------------------------------------------------------------------------------
* one rigid body per roller: `/Robot/links/guide_roller_<i>` (PhysicsRigidBodyAPI +
  PhysicsMassAPI; mass 0.0025 kg = delivered body mass 0.02 kg / 8; solid-cylinder inertia
  spin 2.8125e-7, transverse 1.9396e-7 kg m^2 - derived from the CAD cylinder, NOT measured),
* the matching cylinder collider moved into that body (name kept: guide_wheel_<i>), so the
  existing contact-sensor regex can see eight separate bodies,
* one passive revolute joint `/Robot/joints/guide_roller_<i>` (body0 = chassis) whose axis is
  the vehicle Y, using exactly the delivered hinge convention (physics:axis="X" with
  localRot0 = localRot1 = (0.5,0.5,0.5,0.5)),
* a PhysicsDriveAPI:angular with targetVelocity 0, stiffness 0 and damping = the bearing drag
  (BEARING_DAMPING, marked TO BE CALIBRATED - no bench data exists),
* roller material /Robot/materials/contact_164..171 set to 0.9/0.9 with NO friction-combine
  override: the colliders rotate now, so rolling must come from the bearing, not from sliding,
* removal of `/Robot/links/guide_rollers` and `/Robot/joints/chassis_guide_rollers_fixed`.

usage:  python build_rolling_rollers_usd.py [--src USD] [--dst USD] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path
import sys

from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics

SRC_DEFAULT = "incoming/mod4_fixed_20260912/chassis_mod4/isaac/robot.usd"
DST_DEFAULT = "incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd"
OLD_BODY = "/Robot/links/guide_rollers"
OLD_FIXED_JOINT = "/Robot/joints/chassis_guide_rollers_fixed"
CHASSIS = "/Robot/links/chassis"
LINKS = "/Robot/links"
JOINTS = "/Robot/joints"
ROLLER_MASS_KG = 0.0025          # delivered 0.02 kg / 8 -> derived, not measured
ROLLER_R = 0.015
ROLLER_H = 0.016
BEARING_DAMPING = 1.0e-4         # N m s/rad  TODO(calibration): no bench data
ROLLER_HALF_LIMIT_DEG = 1.0e6    # effectively free rotation
ROLLER_MATERIAL_FRICTION = 0.9   # contact must grip; the bearing provides the rolling loss


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def inertia() -> tuple[float, float, float]:
    m, r, h = ROLLER_MASS_KG, ROLLER_R, ROLLER_H
    spin = 0.5 * m * r * r
    trans = m * (3.0 * r * r + h * h) / 12.0
    return trans, spin, trans       # body frame: Y is the spin axis


def translate_of(prim):
    xf = UsdGeom.Xformable(prim)
    for op in xf.GetOrderedXformOps():
        if op.GetOpName() == "xformOp:translate":
            return op.Get()
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC_DEFAULT)
    ap.add_argument("--dst", default=DST_DEFAULT)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    src, dst = Path(args.src), Path(args.dst)
    if not src.is_file():
        print("source USD missing:", src, file=sys.stderr)
        return 2
    src_sha = sha256(src)

    stage = Usd.Stage.Open(str(src), Usd.Stage.LoadAll)
    body = stage.GetPrimAtPath(OLD_BODY)
    if not body or not body.IsValid():
        print("delivered asset already has no", OLD_BODY, "- nothing to do", file=sys.stderr)
        return 3
    rollers = [c for c in body.GetChildren() if c.GetName().startswith("guide_wheel_")]
    if len(rollers) != 8:
        print("expected 8 guide rollers, found", len(rollers), file=sys.stderr)
        return 3

    ixx, iyy, izz = inertia()
    moved = []
    for child in rollers:
        name = child.GetName()
        idx = name.rsplit("_", 1)[-1]
        pos = translate_of(child)
        new_body_path = Sdf.Path("%s/guide_roller_%s" % (LINKS, idx))
        new_prim_path = Sdf.Path("%s/%s" % (new_body_path, name))
        joint_path = Sdf.Path("%s/guide_roller_%s" % (JOINTS, idx))
        print("[build] %-52s pos=%s -> body=%s" % (name, tuple(round(float(v), 5) for v in pos),
                                                   new_body_path))
        moved.append((name, tuple(float(v) for v in pos), new_body_path, new_prim_path, joint_path))
        if args.dry_run:
            continue

        new_body = stage.DefinePrim(new_body_path, "Xform")
        UsdGeom.Xformable(new_body).AddTranslateOp().Set(Gf.Vec3d(*[float(v) for v in pos]))
        UsdPhysics.RigidBodyAPI.Apply(new_body)
        mass = UsdPhysics.MassAPI.Apply(new_body)
        mass.CreateMassAttr().Set(float(ROLLER_MASS_KG))
        mass.CreateCenterOfMassAttr().Set(Gf.Vec3f(0.0, 0.0, 0.0))
        mass.CreateDiagonalInertiaAttr().Set(Gf.Vec3f(ixx, iyy, izz))
        mass.CreatePrincipalAxesAttr().Set(Gf.Quatf(1.0, 0.0, 0.0, 0.0))

        # move the collider spec into the new body and re-centre it on the body origin
        Sdf.CopySpec(stage.GetRootLayer(), child.GetPath(), stage.GetRootLayer(), new_prim_path)
        stage.RemovePrim(child.GetPath())
        prim = stage.GetPrimAtPath(new_prim_path)
        for op in UsdGeom.Xformable(prim).GetOrderedXformOps():
            if op.GetOpName() == "xformOp:translate":
                op.Set(Gf.Vec3d(0.0, 0.0, 0.0))
        UsdGeom.Imageable(prim).CreateVisibilityAttr().Set("invisible")

        joint = UsdPhysics.RevoluteJoint.Define(stage, joint_path)
        joint.CreateBody0Rel().SetTargets([Sdf.Path(CHASSIS)])
        joint.CreateBody1Rel().SetTargets([new_body_path])
        joint.CreateAxisAttr().Set("X")
        joint.CreateLocalPos0Attr().Set(Gf.Vec3f(*[float(v) for v in pos]))
        joint.CreateLocalRot0Attr().Set(Gf.Quatf(0.5, 0.5, 0.5, 0.5))
        joint.CreateLocalPos1Attr().Set(Gf.Vec3f(0.0, 0.0, 0.0))
        joint.CreateLocalRot1Attr().Set(Gf.Quatf(0.5, 0.5, 0.5, 0.5))
        lim = UsdPhysics.LimitAPI.Apply(joint.GetPrim(), "rotX")
        lim.CreateLowAttr().Set(-ROLLER_HALF_LIMIT_DEG)
        lim.CreateHighAttr().Set(ROLLER_HALF_LIMIT_DEG)
        drv = UsdPhysics.DriveAPI.Apply(joint.GetPrim(), "angular")
        drv.CreateTypeAttr().Set("force")
        drv.CreateTargetVelocityAttr().Set(0.0)
        drv.CreateStiffnessAttr().Set(0.0)
        drv.CreateDampingAttr().Set(float(BEARING_DAMPING))

    if args.dry_run:
        print("[build] dry run: %d rollers would be re-bodied" % len(moved))
        return 0

    # roller contact material: rotation, not sliding, must provide rolling
    mats = []
    for mp in ["/Robot/materials/contact_%d" % i for i in range(164, 172)]:
        p = stage.GetPrimAtPath(mp)
        if p and p.IsValid():
            p.GetAttribute("physics:staticFriction").Set(float(ROLLER_MATERIAL_FRICTION))
            p.GetAttribute("physics:dynamicFriction").Set(float(ROLLER_MATERIAL_FRICTION))
            cmb = p.GetAttribute("physxMaterial:frictionCombineMode")
            if cmb:
                p.RemoveProperty("physxMaterial:frictionCombineMode")
            mats.append(mp)
    print("[build] roller materials set to %.2f on %d prims (combine override removed)"
          % (ROLLER_MATERIAL_FRICTION, len(mats)))

    stage.RemovePrim(Sdf.Path(OLD_FIXED_JOINT))
    stage.RemovePrim(Sdf.Path(OLD_BODY))

    dst.parent.mkdir(parents=True, exist_ok=True)
    stage.GetRootLayer().Export(str(dst))
    for extra in ("meshes.usdc", "scene.usda", "robot_cfg.py"):
        s = src.parent / extra
        if s.is_file():
            shutil.copy2(s, dst.parent / extra)

    chk = Usd.Stage.Open(str(dst), Usd.Stage.LoadAll)
    bodies = [p for p in chk.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI)]
    joints = [p for p in chk.Traverse()
              if p.GetTypeName().startswith("Physics") and p.GetTypeName().endswith("Joint")]
    cols = [p for p in chk.Traverse()
            if p.GetTypeName() in ("Cylinder", "Cube", "Sphere", "Capsule")]
    closures = [p for p in chk.Traverse() if p.GetTypeName() == "PhysicsSphericalJoint"]
    roller_bodies = [p for p in bodies if p.GetName().startswith("guide_roller_")]
    roller_joints = [p for p in joints if p.GetName().startswith("guide_roller_")]
    print("[build] src %s sha256=%s" % (src, src_sha[:16]))
    print("[build] dst %s sha256=%s" % (dst, sha256(dst)[:16]))
    print("[build] bodies=%d (delivered 24)  joints=%d (delivered 23)  closures=%d  colliders=%d"
          % (len(bodies), len(joints), len(closures), len(cols)))
    print("[build] roller bodies=%d roller joints=%d fixed joint present=%s old body present=%s"
          % (len(roller_bodies), len(roller_joints),
             bool(chk.GetPrimAtPath(OLD_FIXED_JOINT)), bool(chk.GetPrimAtPath(OLD_BODY))))
    ok = (len(bodies) == 31 and len(roller_joints) == 8 and len(closures) == 6 and len(cols) == 34
          and not chk.GetPrimAtPath(OLD_FIXED_JOINT) and not chk.GetPrimAtPath(OLD_BODY)
          and sha256(src) == src_sha)
    print("[build] %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())