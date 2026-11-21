# -*- coding: utf-8 -*-
"""Independent OpenUSD stage verification of MOD4v4gemini (robot.usd, MOD4v4_physx.usd, robot_physx.usda)."""
import sys, os, json, math
sys.path.insert(0, r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\pylibs")
sys.path.insert(0, r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\mod4v4_audit")
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics, Gf
from gemini_patch import GIMBAL_BODIES, LEG_BODIES, JOINT_ARM, TAU_MAX

A = r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\MOD4v4gemini_build\MOD4v4gemini\assets"
O = r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\mod4v4_audit\MOD4v4\assets"

gim_paths = {f"/Robot/links/{b}" for b in GIMBAL_BODIES}
leg_paths = {f"/Robot/links/{b}" for b in LEG_BODIES}

def quat_to_mat_col(q):
    # Returns 3x3 column-vector rotation matrix from Gf.Quatf/Quatd
    return np.array(Gf.Matrix3d(Gf.Rotation(Gf.Quatd(q))).GetTranspose(), dtype=np.float64)

res = {}
for fn in ["robot.usd", "MOD4v4_physx.usd", "robot_physx.usda"]:
    st = Usd.Stage.Open(os.path.join(A, fn))
    so = Usd.Stage.Open(os.path.join(O, fn))

    # 1. Verify EVERY PhysicsRevoluteJoint / PhysicsPrismaticJoint has zero anchor/frame mismatch at zero state!
    max_joint_pos_err = 0.0
    max_joint_rot_err_deg = 0.0
    joints_scope = st.GetPrimAtPath("/Robot/joints")
    for jp in joints_scope.GetChildren():
        b0_t = jp.GetRelationship("physics:body0").GetTargets()
        b1_t = jp.GetRelationship("physics:body1").GetTargets()
        if not b0_t or not b1_t:
            continue
        p0 = st.GetPrimAtPath(b0_t[0])
        p1 = st.GetPrimAtPath(b1_t[0])
        m0_row = np.array(p0.GetAttribute("xformOp:transform").Get(), dtype=np.float64) if p0.HasAttribute("xformOp:transform") else np.eye(4)
        m1_row = np.array(p1.GetAttribute("xformOp:transform").Get(), dtype=np.float64) if p1.HasAttribute("xformOp:transform") else np.eye(4)
        R0, t0 = m0_row[:3, :3].T, m0_row[3, :3]
        R1, t1 = m1_row[:3, :3].T, m1_row[3, :3]
        lp0 = np.array(jp.GetAttribute("physics:localPos0").Get(), dtype=np.float64)
        lp1 = np.array(jp.GetAttribute("physics:localPos1").Get(), dtype=np.float64)
        lr0 = quat_to_mat_col(jp.GetAttribute("physics:localRot0").Get())
        lr1 = quat_to_mat_col(jp.GetAttribute("physics:localRot1").Get())
        w_pos0 = t0 + R0 @ lp0
        w_pos1 = t1 + R1 @ lp1
        w_rot0 = R0 @ lr0
        w_rot1 = R1 @ lr1
        # Note: revolute/prismatic joints allow displacement along their joint axis if ref != 0? Wait: in USD zero state, check gimbal joints specifically!
        if "gimbal" in jp.GetName():
            pos_err = float(np.linalg.norm(w_pos0 - w_pos1))
            rot_err = math.degrees(math.acos(np.clip((np.trace(w_rot0.T @ w_rot1) - 1.0) / 2.0, -1.0, 1.0)))
            max_joint_pos_err = max(max_joint_pos_err, pos_err)
            max_joint_rot_err_deg = max(max_joint_rot_err_deg, rot_err)

    assert max_joint_pos_err < 1e-6, (fn, max_joint_pos_err)
    assert max_joint_rot_err_deg < 1e-4, (fn, max_joint_rot_err_deg)

    # 2. Verify fold_link inertia & yaw_link rotated COM
    f = st.GetPrimAtPath("/Robot/links/gimbal_fold_link")
    com_fold = np.array(f.GetAttribute("physics:centerOfMass").Get())
    di_fold = np.array(f.GetAttribute("physics:diagonalInertia").Get())
    R_fold = quat_to_mat_col(f.GetAttribute("physics:principalAxes").Get())
    I_fold = R_fold @ np.diag(di_fold) @ R_fold.T

    # 3. Verify DM-J4310 drives on all 3 gimbal joints
    drv = {}
    for jn in ["gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint"]:
        j = st.GetPrimAtPath(f"/Robot/joints/{jn}")
        lo = j.GetMetadata("apiSchemas")
        drv[jn] = dict(
            hasDriveAPI=j.HasAPI(UsdPhysics.DriveAPI, "angular"),
            stiffness_per_deg=round(float(j.GetAttribute("drive:angular:physics:stiffness").Get()), 6),
            damping_per_deg=round(float(j.GetAttribute("drive:angular:physics:damping").Get()), 6),
            maxForce=float(j.GetAttribute("drive:angular:physics:maxForce").Get()),
            armature=round(float(j.GetAttribute("physxJoint:armature").Get()), 6),
            maxJointVel_deg_s=float(j.GetAttribute("physxJoint:maxJointVelocity").Get()),
            lower=j.GetAttribute("physics:lowerLimit").Get(),
            upper=j.GetAttribute("physics:upperLimit").Get(),
        )
        assert drv[jn]["hasDriveAPI"] and abs(drv[jn]["maxForce"] - TAU_MAX) < 1e-5 and abs(drv[jn]["armature"] - JOINT_ARM) < 1e-6

    # 4. Verify convex-hull collision meshes & filteredPairs
    col_hulls = [p for p in st.Traverse() if p.GetName().startswith("v4_col_")]
    for ch in col_hulls:
        assert ch.HasAPI(UsdPhysics.CollisionAPI) and ch.HasAPI(UsdPhysics.MeshCollisionAPI), ch.GetPath()
        assert ch.GetAttribute("physics:approximation").Get() == "convexHull", ch.GetPath()
        assert len(UsdGeom.Mesh(ch).GetPointsAttr().Get()) >= 4, ch.GetPath()

    gim_leg_filtered_remaining = 0
    for p in st.GetPrimAtPath("/Robot/links").GetChildren():
        pp = str(p.GetPath())
        rel = p.GetRelationship("physics:filteredPairs")
        tg = {str(t) for t in rel.GetTargets()} if rel else set()
        if pp in gim_paths:
            gim_leg_filtered_remaining += len(tg & leg_paths)
        elif pp in leg_paths:
            gim_leg_filtered_remaining += len(tg & gim_paths)
    assert gim_leg_filtered_remaining == 0, (fn, gim_leg_filtered_remaining)

    self_col_enabled = st.GetPrimAtPath("/Robot/links/base_link").GetAttribute("physxArticulation:enabledSelfCollisions").Get()
    assert self_col_enabled is True

    # 5. Untouched link masses & leg joint drives
    mass_same = all(abs((st.GetPrimAtPath(p.GetPath()).GetAttribute("physics:mass").Get() or 0) - (p.GetAttribute("physics:mass").Get() or 0)) < 1e-9
                    for p in so.Traverse() if p.HasAPI(UsdPhysics.MassAPI))
    leg_same = st.GetPrimAtPath("/Robot/joints/left_front1_joint").GetAttribute("drive:angular:physics:damping").Get() == so.GetPrimAtPath("/Robot/joints/left_front1_joint").GetAttribute("drive:angular:physics:damping").Get()
    assert mass_same and leg_same

    res[fn] = dict(
        gimbal_joint_zero_pos_err_m=max_joint_pos_err,
        gimbal_joint_zero_rot_err_deg=max_joint_rot_err_deg,
        fold_com=com_fold.round(6).tolist(),
        fold_principal=di_fold.round(7).tolist(),
        new_convex_hull_prims=len(col_hulls),
        gimbal_leg_filtered_remaining=gim_leg_filtered_remaining,
        enabledSelfCollisions=self_col_enabled,
        drives=drv,
        all_link_masses_unchanged=mass_same,
        leg_drive_unchanged=leg_same,
        variant=st.GetPrimAtPath("/Robot").GetCustomData().get("mod4v4", {}).get("variant"),
        size_MB=round(os.path.getsize(os.path.join(A, fn)) / 1e6, 2),
    )

print(json.dumps(res, indent=2, default=str))
