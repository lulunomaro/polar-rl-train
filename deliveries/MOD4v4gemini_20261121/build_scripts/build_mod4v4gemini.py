# -*- coding: utf-8 -*-
"""Build MOD4v4gemini (v2: SCUT-aligned forward-zero big yaw + Damiao DM-J4310 specs + exact convex-hull gimbal<->leg collisions)."""
import os, sys, json, math, shutil, hashlib, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pylibs"))

import trimesh
import mujoco
from pxr import Usd, Sdf, Gf, UsdGeom, UsdPhysics, UsdShade
from gemini_patch import (
    SRC, HULL_CACHE, FOLD_MASS, DM4310, JOINT_ARM, JOINT_DAMP, TAU_MAX,
    HOLD_YAW_KP, HOLD_YAW_KD, USD_YAW_KP, USD_YAW_KD, HOLD_FP_KP, HOLD_FP_KD,
    CAD_TO_FORWARD_YAW_RAD, STOW_YAW_QPOS, R_FWD, Q_FWD_WXYZ, FORWARD_DIR_CAD,
    LEG_BODIES, GIMBAL_BODIES, fold_mass_properties, yaw_mass_properties_rotated,
    list_cached_hulls, patch_scene,
)

BUILD = os.path.join(os.path.dirname(HERE), "MOD4v4gemini_build")
PKG = os.path.join(BUILD, "MOD4v4gemini")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

if os.path.exists(BUILD):
    shutil.rmtree(BUILD)
shutil.copytree(SRC, PKG, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

# Copy SCUT gimbal adapter helper into tools/
shutil.copyfile(os.path.join(HERE, "scut_gimbal_adapter_src.py"),
                os.path.join(PKG, "tools", "scut_gimbal_adapter.py"))

props = fold_mass_properties()
yaw_props = yaw_mass_properties_rotated()
body_hulls = list_cached_hulls()

I_fold = props["I"]
w_fold, V_fold = np.linalg.eigh(I_fold)
if np.linalg.det(V_fold) < 0:
    V_fold[:, 2] *= -1

print("fold COM:", props["com"], "principal:", w_fold)
print("yaw rotated COM:", yaw_props["com"])

# ---------------- Copy & orient convex-hull STLs into PKG/mjcf/assets ----------------
mj_dir = os.path.join(PKG, "mjcf")
mj_assets = os.path.join(mj_dir, "assets")
hull_meshes_for_usd = {}   # body_name -> list of (mesh_name, trimesh.Trimesh in final link local frame)

for bn, mlist in body_hulls.items():
    hull_meshes_for_usd[bn] = []
    for mn, src_stl in mlist:
        tm = trimesh.load(src_stl, force="mesh", process=True)
        if bn == "gimbal_yaw_link":
            # Bake R_FWD into gimbal_yaw_link's collision hulls so its body frame stays identity (1,0,0,0) facing +X!
            tm.vertices = tm.vertices @ R_FWD.T
        dst_stl = os.path.join(mj_assets, f"{mn}.stl")
        tm.export(dst_stl)
        hull_meshes_for_usd[bn].append((mn, tm))

# ---------------- MJCF ----------------
xml0 = open(os.path.join(SRC, "mjcf", "scene.xml"), encoding="utf-8", newline="").read()
cwd0 = os.getcwd()
os.chdir(mj_dir)
try:
    tmp = mujoco.MjModel.from_xml_string(patch_scene(xml0, props, yaw_props, body_hulls, actuated=False))
    td = mujoco.MjData(tmp)
    mujoco.mj_forward(tmp, td)
    # Compute exact grounded deployed pose (tires tangent to z=0) for deployed_forward keyframe
    g_ground = tmp.geom("ground").id
    tires = [tmp.geom("left_tire").id, tmp.geom("right_tire").id]
    gap = min(mujoco.mj_geomDistance(tmp, td, g_ground, ti, 4.0, None) for ti in tires)
    q_dep = tmp.qpos0.copy()
    q_dep[2] -= gap + 1e-8
    xml_default = patch_scene(xml0, props, yaw_props, body_hulls, actuated=False, qpos_deployed_grounded=q_dep)
    xml_act = patch_scene(xml0, props, yaw_props, body_hulls, actuated=True, qpos_deployed_grounded=q_dep)
finally:
    os.chdir(cwd0)

open(os.path.join(mj_dir, "scene.xml"), "w", encoding="utf-8", newline="").write(xml_default)
open(os.path.join(mj_dir, "scene_gimbal_actuated.xml"), "w", encoding="utf-8", newline="").write(xml_act)
for fn in ["scene.xml", "scene_gimbal_actuated.xml"]:
    mm = mujoco.MjModel.from_xml_path(os.path.join(mj_dir, fn))
    print(fn, "nu=", mm.nu, "nkey=", mm.nkey, "neq=", mm.neq, "ngeom=", mm.ngeom, "nexclude=", mm.nexclude)

# ---------------- USD (robot.usd & MOD4v4_physx.usd) ----------------
deg = math.pi / 180.0
q_fwd_gf = Gf.Quatf(float(Q_FWD_WXYZ[0]), float(Q_FWD_WXYZ[1]), float(Q_FWD_WXYZ[2]), float(Q_FWD_WXYZ[3]))
q_fwd_gfd = Gf.Quatd(float(Q_FWD_WXYZ[0]), float(Q_FWD_WXYZ[1]), float(Q_FWD_WXYZ[2]), float(Q_FWD_WXYZ[3]))
m3_fwd_row = Gf.Matrix3d(*[float(x) for x in R_FWD.T.flatten()])   # Gf uses row-vector convention!
p_yaw_anchor = np.array([7.1045355626525575e-15, -5.346467242255617e-14, 0.0011999999999932065], dtype=np.float64)

leg_paths = {f"/Robot/links/{b}" for b in LEG_BODIES}
gim_paths = {f"/Robot/links/{b}" for b in GIMBAL_BODIES}

# Same-side intra-leg pairs to filter symmetrically
intra_leg_pairs = set()
for s in ("left", "right"):
    sl = [f"/Robot/links/{s}_{k}_link" for k in ("rear1", "front1", "front2", "front3", "front4", "rear2", "spring1", "spring2", "wheel")]
    for i in range(len(sl)):
        for j in range(i + 1, len(sl)):
            intra_leg_pairs.add((sl[i], sl[j]))
            intra_leg_pairs.add((sl[j], sl[i]))

def add_convex_hull_mesh_prim(stage, parent_path, mesh_name, tm_hull, ref_hull_api, phys_mat_path):
    prim_path = f"{parent_path}/{mesh_name}"
    mesh = UsdGeom.Mesh.Define(stage, prim_path)
    p = mesh.GetPrim()
    verts = np.asarray(tm_hull.vertices, dtype=np.float64)
    faces = np.asarray(tm_hull.faces, dtype=np.int32)
    mesh.CreatePointsAttr([Gf.Vec3f(*map(float, v)) for v in verts])
    mesh.CreateFaceVertexCountsAttr([3] * len(faces))
    mesh.CreateFaceVertexIndicesAttr(faces.flatten().tolist())
    mesh.CreateExtentAttr([Gf.Vec3f(*map(float, verts.min(0))), Gf.Vec3f(*map(float, verts.max(0)))])
    mesh.CreateDoubleSidedAttr(True)
    mesh.CreateOrientationAttr("rightHanded")
    mesh.CreateVisibilityAttr("invisible")

    UsdPhysics.CollisionAPI.Apply(p)
    mcol = UsdPhysics.MeshCollisionAPI.Apply(p)
    mcol.CreateApproximationAttr("convexHull")
    p.CreateAttribute("physics:collisionEnabled", Sdf.ValueTypeNames.Bool).Set(True)
    p.CreateAttribute("physxCollision:contactOffset", Sdf.ValueTypeNames.Float).Set(0.001)
    p.CreateAttribute("physxCollision:restOffset", Sdf.ValueTypeNames.Float).Set(0.0)
    if phys_mat_path:
        p.CreateRelationship("material:binding:physics").SetTargets([phys_mat_path])

    # Match explicit apiSchemas style of /Robot/links/base_link/v4_frame_hull_00
    lo = Sdf.TokenListOp()
    lo.explicitItems = list(ref_hull_api.explicitItems) if (ref_hull_api and ref_hull_api.isExplicit) else [
        "PhysicsCollisionAPI", "PhysicsMeshCollisionAPI", "MaterialBindingAPI"
    ]
    p.SetMetadata("apiSchemas", lo)

usd_report = {}
for fn in ["robot.usd", "MOD4v4_physx.usd"]:
    path = os.path.join(PKG, "assets", fn)
    st = Usd.Stage.Open(path)

    ref_hull = st.GetPrimAtPath("/Robot/links/base_link/v4_frame_hull_00")
    ref_hull_api = ref_hull.GetMetadata("apiSchemas")
    mat_rel = ref_hull.GetRelationship("material:binding:physics")
    phys_mat_path = mat_rel.GetTargets()[0] if (mat_rel and mat_rel.GetTargets()) else Sdf.Path("/Robot/PhysicsMaterials/generic")

    # 1. Re-zero gimbal_yaw_link & its 4 child links to SCUT forward convention (+X at yaw=0)
    yaw_prim = st.GetPrimAtPath("/Robot/links/gimbal_yaw_link")
    yaw_prim.GetAttribute("physics:centerOfMass").Set(Gf.Vec3f(*map(float, yaw_props["com"])))
    pa_yaw_old = yaw_prim.GetAttribute("physics:principalAxes").Get()
    pa_yaw_new = q_fwd_gf * Gf.Quatf(pa_yaw_old)
    yaw_prim.GetAttribute("physics:principalAxes").Set(pa_yaw_new)
    for gname in ["gimbal_yaw_envelope", "v4_vis_gimbal_yaw_link_s_step_01", "v4_vis_gimbal_yaw_link_s_step_02",
                  "v4_vis_gimbal_yaw_link_s_step_03", "v4_vis_gimbal_yaw_link_s_step_04"]:
        gp = st.GetPrimAtPath(f"/Robot/links/gimbal_yaw_link/{gname}")
        gp.CreateAttribute("xformOp:orient", Sdf.ValueTypeNames.Quatf).Set(q_fwd_gf)
        gp.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray).Set(["xformOp:orient"])

    for child_b in ["gimbal_fold_link", "gimbal_pitch_link", "gimbal_uwb_tray_link", "gimbal_uwb_arm_link"]:
        cp = st.GetPrimAtPath(f"/Robot/links/{child_b}")
        m4_old = cp.GetAttribute("xformOp:transform").Get()
        p_old = np.array(m4_old.ExtractTranslation(), dtype=np.float64)
        p_new = p_yaw_anchor + R_FWD @ (p_old - p_yaw_anchor)
        m4_new = Gf.Matrix4d(m3_fwd_row, Gf.Vec3d(*map(float, p_new)))
        cp.GetAttribute("xformOp:transform").Set(m4_new)

    for jn in ["gimbal_fold_joint", "gimbal_uwb_arm_joint"]:
        jp = st.GetPrimAtPath(f"/Robot/joints/{jn}")
        lp0_old = np.array(jp.GetAttribute("physics:localPos0").Get(), dtype=np.float64)
        lp0_new = R_FWD @ lp0_old
        lr0_old = jp.GetAttribute("physics:localRot0").Get()
        lr0_new = q_fwd_gf * Gf.Quatf(lr0_old)
        jp.GetAttribute("physics:localPos0").Set(Gf.Vec3f(*map(float, lp0_new)))
        jp.GetAttribute("physics:localRot0").Set(lr0_new)

    # 2. Fix gimbal_fold_link exact solid mass properties
    fold_prim = st.GetPrimAtPath("/Robot/links/gimbal_fold_link")
    m3_fold = Gf.Matrix3d(*[float(x) for x in V_fold.T.flatten()])
    quat_fold = Gf.Matrix4d(m3_fold, Gf.Vec3d(0, 0, 0)).ExtractRotation().GetQuat()
    fold_prim.GetAttribute("physics:centerOfMass").Set(Gf.Vec3f(*map(float, props["com"])))
    fold_prim.GetAttribute("physics:diagonalInertia").Set(Gf.Vec3f(*map(float, w_fold)))
    fold_prim.GetAttribute("physics:principalAxes").Set(Gf.Quatf(quat_fold))

    # 3. Replace coarse gimbal ellipsoids & centerline leg capsules with exact-CAD convex hulls
    prims_to_remove = [
        "/Robot/links/gimbal_yaw_link/gimbal_yaw_contact",
        "/Robot/links/gimbal_fold_link/gimbal_fold_contact",
        "/Robot/links/gimbal_pitch_link/gimbal_pitch_contact",
        "/Robot/links/left_rear1_link/left_thigh_collision",
        "/Robot/links/right_rear1_link/right_thigh_collision",
        "/Robot/links/left_rear2_link/left_shin_collision",
        "/Robot/links/right_rear2_link/right_shin_collision",
        "/Robot/links/left_front1_link/left_input_collision",
        "/Robot/links/right_front1_link/right_input_collision",
    ]
    for rpath in prims_to_remove:
        if st.GetPrimAtPath(rpath):
            st.RemovePrim(rpath)

    added_hulls = 0
    for bn, mlist in hull_meshes_for_usd.items():
        parent_p = f"/Robot/links/{bn}"
        for mn, tm_h in mlist:
            add_convex_hull_mesh_prim(st, parent_p, mn, tm_h, ref_hull_api, phys_mat_path)
            added_hulls += 1

    # 4. Author Damiao DM-J4310-2EC (24V) angular drives + armature + maxJointVelocity (SCUT-aligned)
    ref_j = st.GetPrimAtPath("/Robot/joints/left_front1_joint")
    ref_j_api = ref_j.GetMetadata("apiSchemas")
    allitems = lambda lo: (list(lo.explicitItems) + list(lo.prependedItems) + list(lo.appendedItems)) if lo else []
    for jn in ["gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint"]:
        j = st.GetPrimAtPath(f"/Robot/joints/{jn}")
        drive = UsdPhysics.DriveAPI.Apply(j, "angular")
        drive.CreateTypeAttr("force")
        if jn == "gimbal_yaw_joint":
            drive.CreateStiffnessAttr(float(USD_YAW_KP * deg))
            drive.CreateDampingAttr(float((USD_YAW_KD + JOINT_DAMP) * deg))
        else:
            drive.CreateStiffnessAttr(float(HOLD_FP_KP * deg))
            drive.CreateDampingAttr(float((HOLD_FP_KD + JOINT_DAMP) * deg))
        drive.CreateMaxForceAttr(float(TAU_MAX))
        drive.CreateTargetPositionAttr(0.0)
        drive.CreateTargetVelocityAttr(0.0)
        j.CreateAttribute("physxJoint:armature", Sdf.ValueTypeNames.Float).Set(float(JOINT_ARM))
        j.CreateAttribute("physxJoint:jointFriction", Sdf.ValueTypeNames.Float).Set(0.0)
        j.CreateAttribute("physxJoint:maxJointVelocity", Sdf.ValueTypeNames.Float).Set(1800.0)   # 31.4 rad/s (>20.94 rad/s DM4310 + chassis spin margin)

        items = allitems(j.GetMetadata("apiSchemas"))
        for extra in allitems(ref_j_api):
            if extra not in items:
                items.append(extra)
        if "PhysicsDriveAPI:angular" not in items:
            items.insert(0, "PhysicsDriveAPI:angular")
        new_lo = Sdf.TokenListOp()
        if ref_j_api is not None and ref_j_api.isExplicit:
            new_lo.explicitItems = items
        else:
            new_lo.prependedItems = items
        j.SetMetadata("apiSchemas", new_lo)
        assert j.HasAPI(UsdPhysics.DriveAPI, "angular"), jn

    # 5. Update physics:filteredPairs symmetrically:
    #    - Remove ALL gimbal <-> leg pairs (enabling true physical gimbal-leg contact in PhysX!)
    #    - Ensure same-side intra-leg pairs (including spring1/2 and wheel_link) have PhysicsFilteredPairsAPI
    removed_gim_leg = 0
    added_intra_leg = 0
    links_scope = st.GetPrimAtPath("/Robot/links")
    for p in links_scope.GetChildren():
        pp = str(p.GetPath())
        rel = p.GetRelationship("physics:filteredPairs")
        tg = [str(t) for t in rel.GetTargets()] if rel else []
        orig_len = len(tg)
        if pp in gim_paths:
            tg = [t for t in tg if t not in leg_paths]
            removed_gim_leg += orig_len - len(tg)
        elif pp in leg_paths:
            tg = [t for t in tg if t not in gim_paths]
            removed_gim_leg += orig_len - len(tg)
            # add same-side intra-leg partners
            for a, b in intra_leg_pairs:
                if a == pp and b not in tg:
                    tg.append(b)
                    added_intra_leg += 1
        if tg or rel:
            if not rel:
                UsdPhysics.FilteredPairsAPI.Apply(p)
                lo_p = p.GetMetadata("apiSchemas")
                p_items = allitems(lo_p)
                if "PhysicsFilteredPairsAPI" not in p_items:
                    p_items.append("PhysicsFilteredPairsAPI")
                    nlo = Sdf.TokenListOp()
                    nlo.explicitItems = p_items
                    p.SetMetadata("apiSchemas", nlo)
                rel = p.CreateRelationship("physics:filteredPairs")
            rel.SetTargets([Sdf.Path(t) for t in sorted(set(tg))])

    rp = st.GetPrimAtPath("/Robot")
    cd = rp.GetCustomData()
    mod = dict(cd.get("mod4v4", {}))
    mod["variant"] = "MOD4v4gemini"
    mod["geminiFixes"] = (
        "SCUT forward-zero gimbal_yaw_joint=0 (+X), fold-link solid inertia/COM, "
        "Damiao DM-J4310-2EC drives+armature, 58 exact-CAD convex-hull gimbal<->leg collisions"
    )
    rp.SetCustomDataByKey("mod4v4", mod)
    st.GetRootLayer().Save()
    usd_report[fn] = dict(
        added_convex_hulls=added_hulls,
        removed_gimbal_leg_filtered_targets=removed_gim_leg,
        added_intra_leg_filtered_targets=added_intra_leg,
        sha256=sha(path),
    )
    print(fn, usd_report[fn])

# ---------------- Update JSON metadata contracts ----------------
mp_path = os.path.join(PKG, "model_parameters.json")
mp = json.load(open(mp_path, encoding="utf-8"))
mp["model"] = "MOD4v4gemini"
mp["gimbal_motor"] = dict(
    **DM4310,
    joints=["gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint"],
    yaw_transmission_evidence="STEP verified: active pulley (v4_vis_base_link_s_step_16#0 @ (0.0798,0.0290,-0.0113)m, r_tip=40.03mm, 51 teeth) drives passive pulley (-云台yaw传动同步带轮_被动-1, r_tip=40.04mm, 51 teeth) -> exact 1:1 ratio",
    fold_pitch_transmission_evidence="STEP verified coaxial 4310减速电机_修复-2 (fold) and 4310减速电机_修复-1 (pitch), 1:1 direct output",
    status="User confirmed yaw & pitch use Damiao 4310; STEP confirms coaxial 4310 on fold & pitch and 51:51 belt on yaw",
)
mp["gimbal_scut_alignment_and_collision"] = dict(
    zero_pose_convention="SCUT WheelBipe V14_2 aligned: gimbal_yaw_joint=0 faces chassis +X; gimbal_yaw_link quat=(1,0,0,0) Euler Z equals world barrel heading",
    cad_saved_stow_yaw_rad=STOW_YAW_QPOS,
    cad_saved_stow_yaw_deg=math.degrees(STOW_YAW_QPOS),
    gimbal_leg_collision_enabled=True,
    convex_hull_count_total=sum(len(v) for v in body_hulls.values()),
    convex_hull_bodies= {k: len(v) for k, v in body_hulls.items()},
)
json.dump(mp, open(mp_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

ul_path = os.path.join(PKG, "cad", "upper_limits.json")
ul = json.load(open(ul_path, encoding="utf-8"))
ul["reference"] = "SCUT-aligned forward-zero convention: gimbal_yaw_joint=0 faces chassis +X; fold & pitch relative to horizontal deployed pose"
ul["cad_raw_yaw_to_forward_offset_deg"] = math.degrees(CAD_TO_FORWARD_YAW_RAD)
ul["stow_pose_deg"] = {
    "gimbal_yaw_joint": math.degrees(STOW_YAW_QPOS),
    "gimbal_fold_joint": 54.5,
    "gimbal_pitch_joint": -53.75,
}
json.dump(ul, open(ul_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

ic_path = os.path.join(PKG, "assets", "import_contract.json")
ic = json.load(open(ic_path, encoding="utf-8"))
ic["asset_variant"] = "MOD4v4gemini"
ic["source_mjcf_sha256"] = sha(os.path.join(mj_dir, "scene.xml"))
ic["output_usd_sha256"] = usd_report["robot.usd"]["sha256"]
ic["native_MJCF_equalities"] = 12
for jn in ["gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint"]:
    ic["joints"][jn]["motor_hardware"] = dict(
        model=DM4310["model"],
        continuous_torque_Nm=DM4310["continuous_torque_nm"],
        peak_torque_Nm=DM4310["peak_torque_nm"],
        rated_speed_rad_s=DM4310["rated_speed_rad_s"],
        no_load_speed_rad_s=DM4310["no_load_speed_rad_s"],
        armature_kg_m2=JOINT_ARM,
        passive_damping_Nm_s_rad=JOINT_DAMP,
        external_ratio=1.0,
    )
ic["gemini_fold_link_mass_properties"] = dict(
    mass_kg=FOLD_MASS,
    com_m=props["com"].tolist(),
    fullinertia_kg_m2=[I_fold[0,0], I_fold[1,1], I_fold[2,2], I_fold[0,1], I_fold[0,2], I_fold[1,2]],
    principal_kg_m2=w_fold.tolist(),
    method="exact signed-tetrahedron volume integration of the three gimbal_fold_link STEP meshes, scaled to CAD mass",
)
ic["gimbal_scut_alignment"] = dict(
    site="gimbal_aim",
    yaw_zero_direction_in_base_frame=[1.0, 0.0, 0.0],
    stow_safe_pocket_yaw_rad=STOW_YAW_QPOS,
    mjcf_keyframes=["guide_ground_stow", "deployed_forward"],
    adapter_module="tools/scut_gimbal_adapter.py",
)
ic["gimbal_leg_contact_enabled"] = True
json.dump(ic, open(ic_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

rc_path = os.path.join(PKG, "runtime_config.json")
rc = json.load(open(rc_path, encoding="utf-8"))
rc["asset_variant"] = "MOD4v4gemini"
rc["MJCF_gimbal_actuated"] = "mjcf/scene_gimbal_actuated.xml"
rc["gimbal_actuator_order_in_actuated_scene"] = ["gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint"]
rc["gimbal_actuator_names_in_actuated_scene"] = ["gimbal_yaw_joint_motor", "gimbal_fold_joint_motor", "gimbal_pitch_joint_motor"]
rc["gimbal_actuator_indices_in_actuated_scene"] = [6, 7, 8]
rc["gimbal_motor_hardware"] = DM4310
rc["gimbal_default_scene_behaviour"] = (
    "scene.xml keeps nu=6 for 100% MOD4v3 R3 compatibility; gimbal_yaw_joint=0 faces chassis +X "
    "(SCUT WheelBipe V14_2 convention) with passive hold springs on yaw/fold/pitch."
)
rc["gimbal_actuated_scene_behaviour"] = (
    "scene_gimbal_actuated.xml (nu=9) exposes three direct torque <motor> actuators (±7.0 Nm DM-J4310-2EC) "
    "supporting SCUT world-heading IMU gyro PD, SCUT random yaw-velocity disturbance, and safe-pocket stow."
)
rc["gimbal_stow_safe_yaw_rad"] = STOW_YAW_QPOS
rc["gimbal_leg_collision_enabled"] = True
rc["gimbal_contact_reset_bodies"] = GIMBAL_BODIES
json.dump(rc, open(rc_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

json.dump(dict(usd=usd_report, built=datetime.datetime.now().isoformat()),
          open(os.path.join(BUILD, "build_meta.json"), "w", encoding="utf-8"), indent=2)
print("BUILD OK ->", PKG)
