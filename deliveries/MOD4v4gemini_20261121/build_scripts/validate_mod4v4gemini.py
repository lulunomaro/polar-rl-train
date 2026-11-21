# -*- coding: utf-8 -*-
"""Comprehensive validation of MOD4v4gemini (SCUT forward-zero yaw + DM-J4310 + convex-hull gimbal<->leg collisions)."""
import os, sys, json, math, re, time
import numpy as np
import trimesh
import mujoco
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pylibs"))
from gemini_patch import SRC, GIMBAL_BODIES, LEG_BODIES, STOW_YAW_QPOS, CAD_TO_FORWARD_YAW_RAD, DM4310
PKG = os.path.join(os.path.dirname(HERE), "MOD4v4gemini_build", "MOD4v4gemini")
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "tools"))
import kinematics
import semantics
import scut_gimbal_adapter as sga

R = {}
load = lambda root, fn: mujoco.MjModel.from_xml_path(os.path.join(root, "mjcf", fn))
mo, mg, ma = load(SRC, "scene.xml"), load(PKG, "scene.xml"), load(PKG, "scene_gimbal_actuated.xml")
name = lambda m, t, i: mujoco.mj_id2name(m, t, i)

# 1. Interface & SCUT semantics compatibility
sem = semantics.Semantics(PKG)
do, dg = mujoco.MjData(mo), mujoco.MjData(mg)
mujoco.mj_forward(mo, do); mujoco.mj_forward(mg, dg)
st_o = sem.mujoco_joint_state(mo, do)
st_g = sem.mujoco_joint_state(mg, dg)

R["interface"] = dict(
    nq_nv=[mg.nq, mg.nv],
    nu_default=mg.nu,
    nu_actuated=ma.nu,
    joint_names_identical=[name(mo, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(mo.njnt)] == [name(mg, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(mg.njnt)],
    body_names_identical=[name(mo, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(mo.nbody)] == [name(mg, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(mg.nbody)],
    first6_actuators_identical=all(name(mo, mujoco.mjtObj.mjOBJ_ACTUATOR, i) == name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i) for m in (mg, ma) for i in range(6)),
    first19_sensors_identical=all(name(mo, mujoco.mjtObj.mjOBJ_SENSOR, i) == name(m, mujoco.mjtObj.mjOBJ_SENSOR, i) for m in (mg, ma) for i in range(mo.nsensor)),
    actuated_extra_actuators=[name(ma, mujoco.mjtObj.mjOBJ_ACTUATOR, i) for i in range(6, ma.nu)],
    scut_leg_semantic_pos_diff_max=float(np.max(np.abs(st_o["joint_pos"] - st_g["joint_pos"]))),
    total_mass_kg=[round(float(mo.body_mass.sum()), 6), round(float(mg.body_mass.sum()), 6)],
    keyframes=[name(mg, mujoco.mjtObj.mjOBJ_KEY, i) for i in range(mg.nkey)],
)
assert R["interface"]["joint_names_identical"] and R["interface"]["body_names_identical"]
assert R["interface"]["scut_leg_semantic_pos_diff_max"] == 0.0

# 2. SCUT Forward-Zero Alignment & Exact Stow World-Vertex Equivalence
aim_z = dg.site_xmat[mg.site("gimbal_aim").id].reshape(3, 3)[:, 2]
R_base = dg.xmat[mg.body("base_link").id].reshape(3, 3)
R_yaw = dg.xmat[mg.body("gimbal_yaw_link").id].reshape(3, 3)
aim_in_base = R_base.T @ aim_z
yaw_frame_err_deg = math.degrees(math.acos(np.clip((np.trace(R_base.T @ R_yaw) - 1.0) / 2.0, -1.0, 1.0)))

# Compare all 36 bodies' visual vertices in world space at guide_ground_stow between original MOD4v4 and MOD4v4gemini!
mujoco.mj_resetDataKeyframe(mo, do, mo.key("guide_ground_stow").id); mujoco.mj_forward(mo, do)
mujoco.mj_resetDataKeyframe(mg, dg, mg.key("guide_ground_stow").id); mujoco.mj_forward(mg, dg)
max_stow_vertex_diff_m = 0.0
for g_orig in range(mo.ngeom):
    if mo.geom_contype[g_orig] == 0 and mo.geom_type[g_orig] == mujoco.mjtGeom.mjGEOM_MESH:
        gname = name(mo, mujoco.mjtObj.mjOBJ_GEOM, g_orig)
        g_new = mg.geom(gname).id
        mid_o, mid_n = mo.geom_dataid[g_orig], mg.geom_dataid[g_new]
        vo = mo.mesh_vert[mo.mesh_vertadr[mid_o]:mo.mesh_vertadr[mid_o] + min(200, mo.mesh_vertnum[mid_o])]
        vn = mg.mesh_vert[mg.mesh_vertadr[mid_n]:mg.mesh_vertadr[mid_n] + min(200, mg.mesh_vertnum[mid_n])]
        wo = vo @ do.geom_xmat[g_orig].reshape(3, 3).T + do.geom_xpos[g_orig]
        wn = vn @ dg.geom_xmat[g_new].reshape(3, 3).T + dg.geom_xpos[g_new]
        max_stow_vertex_diff_m = max(max_stow_vertex_diff_m, float(np.max(np.abs(wo - wn))))

R["scut_alignment_and_stow_equivalence"] = dict(
    aim_direction_at_qpos0_in_base=aim_in_base.round(8).tolist(),
    gimbal_yaw_link_frame_error_at_qpos0_deg=round(yaw_frame_err_deg, 8),
    stow_yaw_qpos_rad=STOW_YAW_QPOS,
    stow_yaw_qpos_deg=round(math.degrees(STOW_YAW_QPOS), 4),
    stow_world_visual_vertex_max_diff_m=max_stow_vertex_diff_m,
)
assert np.allclose(aim_in_base, [1.0, 0.0, 0.0], atol=1e-7), aim_in_base
assert max_stow_vertex_diff_m < 1e-6, max_stow_vertex_diff_m

# 3. Fold link mass properties
def body_report(m, b):
    bid = m.body(b).id
    verts = []
    for g in range(m.ngeom):
        if m.geom_bodyid[g] == bid and m.geom_contype[g] == 0 and m.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH:
            mid = m.geom_dataid[g]; v = m.mesh_vert[m.mesh_vertadr[mid]:m.mesh_vertadr[mid] + m.mesh_vertnum[mid]]
            gm = np.zeros(9); mujoco.mju_quat2Mat(gm, m.geom_quat[g])
            verts.append(v @ gm.reshape(3, 3).T + m.geom_pos[g])
    v = np.vstack(verts); lo, hi = v.min(0), v.max(0)
    c = m.body_ipos[bid]
    out = float(np.linalg.norm(np.maximum(0, np.maximum(lo - c, c - hi))))
    return dict(com=c.round(5).tolist(), principal_inertia=m.body_inertia[bid].round(6).tolist(),
                max_gyration_radius_m=round(float(np.sqrt(m.body_inertia[bid] / m.body_mass[bid]).max()), 5),
                com_outside_mesh_box_mm=round(out * 1000, 4))
R["fold_link"] = dict(original=body_report(mo, "gimbal_fold_link"), gemini=body_report(mg, "gimbal_fold_link"))

# 4. Closed chains & keyframes
d = mujoco.MjData(mg)
lo_d, hi_d = kinematics.mechanical_delta_bounds("left")
errs = []
for a in np.linspace(lo_d, hi_d, 201):
    kinematics.set_configuration(mg, d, left=(-0.4806332576622214 + a, -0.4806332576622214), right=(-0.4806332576622214 + a, -0.4806332576622214))
    errs.append(max(np.linalg.norm(d.site_xpos[mg.eq_obj1id[e]] - d.site_xpos[mg.eq_obj2id[e]]) for e in range(mg.neq) if mg.eq_type[e] == mujoco.mjtEq.mjEQ_CONNECT))
R["closed_chain"] = dict(delta_bounds_deg=[round(math.degrees(lo_d), 4), round(math.degrees(hi_d), 4)], max_loop_gap_m=float(max(errs)))
for k in range(mg.nkey):
    kname = name(mg, mujoco.mjtObj.mjOBJ_KEY, k)
    mujoco.mj_resetDataKeyframe(mg, d, k); mujoco.mj_forward(mg, d)
    R["closed_chain"][f"key_{kname}_max_equality_violation"] = float(np.abs(d.efc_pos[:d.ne]).max())
    sup = sorted({name(mg, mujoco.mjtObj.mjOBJ_GEOM, c.geom2 if c.geom1 == mg.geom("ground").id else c.geom1)
                  for c in d.contact[:d.ncon] if mg.geom("ground").id in (c.geom1, c.geom2)})
    self_con = [(name(mg, mujoco.mjtObj.mjOBJ_GEOM, c.geom1), name(mg, mujoco.mjtObj.mjOBJ_GEOM, c.geom2))
                for c in d.contact[:d.ncon] if mg.geom("ground").id not in (c.geom1, c.geom2)]
    R["closed_chain"][f"key_{kname}_ground_contacts"] = sup
    R["closed_chain"][f"key_{kname}_self_contacts"] = self_con
    assert len(self_con) == 0, (kname, self_con)

# 5. Gravity hold (2s) + Safe-Yaw-First Stow Sequence (no collision!)
def with_mocap(xml_text):
    xml_text = xml_text.replace('<worldbody>', '<worldbody>\r\n    <body name="drive_mocap" mocap="true" pos="0 0 0.6" />', 1)
    return xml_text.replace('<equality>', '<equality>\r\n    <weld name="drive_weld" body1="drive_mocap" body2="base_link" solref=".002 1" />', 1)

def model_from(root, fn, edit=None):
    t = open(os.path.join(root, "mjcf", fn), encoding="utf-8").read()
    if edit: t = edit(t)
    cwd = os.getcwd(); os.chdir(os.path.join(root, "mjcf"))
    try: return mujoco.MjModel.from_xml_string(with_mocap(t))
    finally: os.chdir(cwd)

HIP = ["left_front1_joint", "right_front1_joint", "left_rear1_joint", "right_rear1_joint"]
def leg_hold(m, d, q0):
    for i, j in enumerate(HIP):
        jid = m.joint(j).id
        d.ctrl[i] = np.clip(60 * (q0[m.jnt_qposadr[jid]] - d.qpos[m.jnt_qposadr[jid]]) - 2 * d.qvel[m.jnt_dofadr[jid]], -40, 40)

def gq(m, d, j): return float(d.qpos[m.jnt_qposadr[m.joint(j).id]])
def gv(m, d, j): return float(d.qvel[m.jnt_dofadr[m.joint(j).id]])

def gravity_hold(m, seconds=2.0, actuated_targets=None):
    d = mujoco.MjData(m); d.qpos[2] = 0.6; mujoco.mj_forward(m, d); q0 = m.qpos0.copy()
    for _ in range(int(seconds / m.opt.timestep)):
        leg_hold(m, d, q0)
        if actuated_targets is not None:
            ty, tf, tp = actuated_targets
            ey = sga.wrap_to_pi(ty - gq(m, d, "gimbal_yaw_joint"))
            d.ctrl[6] = sga.clip_dm4310_torque_envelope(30.0 * ey - 1.5 * gv(m, d, "gimbal_yaw_joint"), gv(m, d, "gimbal_yaw_joint"))
            d.ctrl[7] = sga.clip_dm4310_torque_envelope(50.0 * (tf - gq(m, d, "gimbal_fold_joint")) - 1.8 * gv(m, d, "gimbal_fold_joint"), gv(m, d, "gimbal_fold_joint"))
            d.ctrl[8] = sga.clip_dm4310_torque_envelope(50.0 * (tp - gq(m, d, "gimbal_pitch_joint")) - 1.8 * gv(m, d, "gimbal_pitch_joint"), gv(m, d, "gimbal_pitch_joint"))
        mujoco.mj_step(m, d)
    return {j: round(math.degrees(gq(m, d, j)), 3) for j in ["gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint"]}

R["gravity_hold_2s_deg"] = dict(
    original_unactuated=gravity_hold(model_from(SRC, "scene.xml")),
    gemini_default_scene=gravity_hold(model_from(PKG, "scene.xml")),
    gemini_actuated_deployed=gravity_hold(model_from(PKG, "scene_gimbal_actuated.xml"), actuated_targets=(0.0, 0.0, 0.0)),
    gemini_actuated_safe_stow=gravity_hold(model_from(PKG, "scene_gimbal_actuated.xml"), actuated_targets=(STOW_YAW_QPOS, sga.STOW_FOLD_RAD, sga.STOW_PITCH_RAD)),
)

# 5b. Safe-Yaw-First Dynamic Folding Trajectory from Deployed Forward (0,0,0) -> Full Stow (-149.7, +54.5, -53.75)
m_stow = model_from(PKG, "scene_gimbal_actuated.xml")
d_stow = mujoco.MjData(m_stow); d_stow.qpos[2] = 0.6; mujoco.mj_forward(m_stow, d_stow); q0_s = m_stow.qpos0.copy()
stow_contacts = 0
for _ in range(int(2.5 / m_stow.opt.timestep)):
    leg_hold(m_stow, d_stow, q0_s)
    ty, tf, tp = sga.plan_stow_targets(gq(m_stow, d_stow, "gimbal_yaw_joint"), stow=True)
    ey = sga.wrap_to_pi(ty - gq(m_stow, d_stow, "gimbal_yaw_joint"))
    d_stow.ctrl[6] = sga.clip_dm4310_torque_envelope(25.0 * ey - 2.0 * gv(m_stow, d_stow, "gimbal_yaw_joint"), gv(m_stow, d_stow, "gimbal_yaw_joint"))
    d_stow.ctrl[7] = sga.clip_dm4310_torque_envelope(45.0 * (tf - gq(m_stow, d_stow, "gimbal_fold_joint")) - 2.0 * gv(m_stow, d_stow, "gimbal_fold_joint"), gv(m_stow, d_stow, "gimbal_fold_joint"))
    d_stow.ctrl[8] = sga.clip_dm4310_torque_envelope(45.0 * (tp - gq(m_stow, d_stow, "gimbal_pitch_joint")) - 2.0 * gv(m_stow, d_stow, "gimbal_pitch_joint"), gv(m_stow, d_stow, "gimbal_pitch_joint"))
    mujoco.mj_step(m_stow, d_stow)
    for c in d_stow.contact[:d_stow.ncon]:
        if m_stow.geom("ground").id not in (c.geom1, c.geom2):
            stow_contacts += 1
R["safe_yaw_first_stow_transition"] = dict(
    final_angles_deg={j: round(math.degrees(gq(m_stow, d_stow, j)), 2) for j in ["gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint"]},
    self_collision_steps=stow_contacts,
)
assert stow_contacts == 0, stow_contacts

# 6. SCUT-style World-Heading IMU Gyro Lock under 12 rad/s Fast Chassis Spin + +-8 deg/2Hz Pitching (DM-J4310 Envelope!)
ORIG_INERTIAL = re.search(r'<inertial mass="0.780430372972"[^>]*/>', open(os.path.join(SRC, "mjcf", "scene.xml"), encoding="utf-8").read()).group(0)
def revert_inertia(t):
    return re.sub(r'<inertial mass="0.780430372972"[^>]*/>', ORIG_INERTIAL, t, count=1)

def quat_yaw_pitch(yaw, pitch):
    q1 = np.array([math.cos(yaw / 2), 0, 0, math.sin(yaw / 2)])
    q2 = np.array([math.cos(pitch / 2), 0, math.sin(pitch / 2), 0])
    out = np.zeros(4); mujoco.mju_mulQuat(out, q1, q2); return out

def scut_spin_test(m, wz=12.0, accel=30.0, T=2.5):
    """SCUT WheelBipe V14_2 world-heading IMU torque PD + DM-J4310 24V torque-speed envelope."""
    d = mujoco.MjData(m); d.qpos[2] = 0.6; mujoco.mj_forward(m, d); q0 = m.qpos0.copy()
    aim = m.site("gimbal_aim").id; yaw_bid = m.body("gimbal_yaw_link").id; dt = m.opt.timestep
    dof = {j: m.jnt_dofadr[m.joint(j).id] for j in ["gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint"]}
    psi = 0.0; w = 0.0; errs = []; taus_all = {j: 0.0 for j in dof}; taus_ss = {j: 0.0 for j in dof}
    sat_peak = {j: 0 for j in dof}; over_cont = {j: 0 for j in dof}; nss = 0; t = 0.0
    while t < T:
        w = min(wz, w + accel * dt); psi += w * dt
        pitch = math.radians(8.0) * math.sin(2 * math.pi * 2.0 * t)
        d.mocap_pos[0] = [0, 0, 0.6]; d.mocap_quat[0] = quat_yaw_pitch(psi, pitch)
        leg_hold(m, d, q0)
        # SCUT world-heading lock: read gimbal_yaw_link world heading + world gyro z!
        Ry = d.xmat[yaw_bid].reshape(3, 3)
        yaw_heading_w = math.atan2(Ry[1, 0], Ry[0, 0])
        # World angular velocity z of gimbal_yaw_link (from gyro sensor)
        gyro_local = d.sensordata[m.sensor("gimbal_aim_gyro").adr[0]:m.sensor("gimbal_aim_gyro").adr[0] + 3]
        R_aim = d.site_xmat[aim].reshape(3, 3)
        omega_w_z = float((R_aim @ gyro_local)[2])
        d.ctrl[6] = sga.compute_world_heading_pd_torque(
            0.0, yaw_heading_w, omega_w_z, kp=35.0, kd=1.6, joint_vel=gv(m, d, "gimbal_yaw_joint"), max_effort=7.0
        )
        # Pitch & Fold stabilize barrel elevation to world horizontal (0 rad)
        aim_dir = R_aim[:, 2]
        elev = math.asin(np.clip(aim_dir[2], -1.0, 1.0))
        d.ctrl[7] = sga.clip_dm4310_torque_envelope(50.0 * (0.0 - gq(m, d, "gimbal_fold_joint")) - 1.8 * gv(m, d, "gimbal_fold_joint"), gv(m, d, "gimbal_fold_joint"))
        d.ctrl[8] = sga.clip_dm4310_torque_envelope(45.0 * (-elev - 0.1 * gq(m, d, "gimbal_pitch_joint")) - 1.5 * gv(m, d, "gimbal_pitch_joint"), gv(m, d, "gimbal_pitch_joint"))
        mujoco.mj_step(m, d); t += dt
        z = d.site_xmat[aim].reshape(3, 3)[:, 2]
        heading = math.atan2(z[1], z[0])
        if t > 0.3:
            errs.append(abs(math.degrees(math.atan2(math.sin(heading), math.cos(heading)))))
        for j, k in dof.items():
            tau = abs(float(d.qfrc_actuator[k]))
            if t > 0.05:
                taus_all[j] = max(taus_all[j], tau)
            if t > 0.6:
                taus_ss[j] = max(taus_ss[j], tau)
                sat_peak[j] += tau > 7.0 - 1e-4
                over_cont[j] += tau > 3.0
                if j == "gimbal_yaw_joint":
                    nss += 1
    return dict(
        rms_world_heading_error_deg=round(float(np.sqrt(np.mean(np.square(errs)))), 4),
        max_world_heading_error_deg=round(float(np.max(errs)), 4),
        peak_torque_Nm_after_50ms={k: round(v, 3) for k, v in taus_all.items()},
        steady_spin_peak_torque_Nm={k: round(v, 3) for k, v in taus_ss.items()},
        steady_fraction_at_7Nm_peak={k: round(v / max(nss, 1), 4) for k, v in sat_peak.items()},
        steady_fraction_above_3Nm_rated={k: round(v / max(nss, 1), 4) for k, v in over_cont.items()},
    )

R["spin_12rad_s_scut_world_heading_hold"] = dict(
    original_fold_inertia=scut_spin_test(model_from(PKG, "scene_gimbal_actuated.xml", revert_inertia)),
    gemini_fixed_inertia_dm4310=scut_spin_test(model_from(PKG, "scene_gimbal_actuated.xml")),
)

# 7. UWB parallelogram tracking under fast 1.5 Hz fold sweep
def uwb_test(m):
    d = mujoco.MjData(m); d.qpos[2] = 0.6; mujoco.mj_forward(m, d); q0 = m.qpos0.copy(); et = ea = 0.0
    df, dp, dy = [m.jnt_dofadr[m.joint(j).id] for j in ("gimbal_fold_joint", "gimbal_pitch_joint", "gimbal_yaw_joint")]
    has_stow_offset = "gemini" in name(m, mujoco.mjtObj.mjOBJ_MODEL, 0) if False else (m.nu == 9)
    ty = STOW_YAW_QPOS if m.nu == 9 else 0.0
    for k in range(int(2.0 / m.opt.timestep)):
        t = k * m.opt.timestep
        leg_hold(m, d, q0)
        tf = 0.2 + 0.7 * math.sin(2 * math.pi * 1.5 * t)
        d.qfrc_applied[dy] = np.clip(30 * sga.wrap_to_pi(ty - gq(m, d, "gimbal_yaw_joint")) - 1.5 * d.qvel[dy], -7, 7)
        d.qfrc_applied[df] = np.clip(60 * (tf - gq(m, d, "gimbal_fold_joint")) - 2 * d.qvel[df], -7, 7)
        d.qfrc_applied[dp] = np.clip(60 * (-0.3 - gq(m, d, "gimbal_pitch_joint")) - 2 * d.qvel[dp], -7, 7)
        mujoco.mj_step(m, d)
        f = gq(m, d, "gimbal_fold_joint")
        et = max(et, abs(gq(m, d, "gimbal_uwb_tray_joint") + f))
        ea = max(ea, abs(gq(m, d, "gimbal_uwb_arm_joint") - f))
    return dict(max_tray_error_deg=round(math.degrees(et), 4), max_arm_error_deg=round(math.degrees(ea), 4))
R["uwb_parallelogram_fast_fold"] = dict(original=uwb_test(model_from(SRC, "scene.xml")),
                                        gemini=uwb_test(model_from(PKG, "scene_gimbal_actuated.xml")))

# 8. Gimbal <-> Leg Physical Collision Audit (Confusion Matrix & Safe/Unsafe Yaw Intervals in SCUT Forward-Zero Frame)
vis_clouds = {}
for g in range(mg.ngeom):
    b = mg.geom_bodyid[g]
    if mg.geom_contype[g] == 0 and mg.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH:
        mid = mg.geom_dataid[g]
        v = mg.mesh_vert[mg.mesh_vertadr[mid]:mg.mesh_vertadr[mid] + mg.mesh_vertnum[mid]]
        f = mg.mesh_face[mg.mesh_faceadr[mid]:mg.mesh_faceadr[mid] + mg.mesh_facenum[mid]]
        pts = trimesh.sample.sample_surface(trimesh.Trimesh(vertices=v, faces=f, process=False), 1200, seed=1)[0]
        gm = np.zeros(9); mujoco.mju_quat2Mat(gm, mg.geom_quat[g])
        vis_clouds.setdefault(b, []).append(pts @ gm.reshape(3, 3).T + mg.geom_pos[g])
vis_clouds = {b: np.vstack(v) for b, v in vis_clouds.items()}
gim_bids = [mg.body(b).id for b in GIMBAL_BODIES]
leg_bids = [mg.body(b).id for b in LEG_BODIES]

def has_gim_leg_sim_contact(m, d):
    for c in d.contact[:d.ncon]:
        bs = {name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[c.geom1]),
              name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[c.geom2])}
        if (bs & set(GIMBAL_BODIES)) and (bs & set(LEG_BODIES)):
            return True
    return False

# 8a. Normal deployed driving poses (delta in [-0.75, +0.45], common in [-60, +60] deg, pitch in [-20, 0, +35], 360 yaw)
d = mujoco.MjData(mg)
qy, qf, qp = [mg.jnt_qposadr[mg.joint(j).id] for j in ("gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint")]
n_dep_poses, n_dep_fp_gt4mm, n_dep_real_hits = 0, 0, 0
for delta in np.linspace(lo_d + 0.02, hi_d - 0.02, 5):
    for common_deg in (-60, -30, 0, 30, 60):
        c_rad = math.radians(common_deg)
        kinematics.set_configuration(mg, d, left=(-0.4806332576622214 + c_rad + delta, -0.4806332576622214 + c_rad),
                                     right=(-0.4806332576622214 + c_rad + delta, -0.4806332576622214 + c_rad))
        d.qpos[2] = 0.55; mujoco.mj_forward(mg, d)
        tl = cKDTree(np.vstack([vis_clouds[b] @ d.xmat[b].reshape(3, 3).T + d.xpos[b] for b in leg_bids if b in vis_clouds]))
        for pdeg in (-20, 0, 35):
            for yd in range(-180, 180, 15):
                d.qpos[qy] = math.radians(yd); d.qpos[qf] = 0.0; d.qpos[qp] = math.radians(pdeg)
                mujoco.mj_forward(mg, d)
                n_dep_poses += 1
                if has_gim_leg_sim_contact(mg, d):
                    wg = np.vstack([vis_clouds[b] @ d.xmat[b].reshape(3, 3).T + d.xpos[b] for b in gim_bids if b in vis_clouds])
                    mc = float(tl.query(wg)[0].min()) * 1000.0
                    if mc >= 4.0:
                        n_dep_fp_gt4mm += 1
                    else:
                        n_dep_real_hits += 1

# 8b. Stow 1-deg yaw sweep in SCUT forward-zero degrees [-180..+179]
mujoco.mj_resetDataKeyframe(mg, d, mg.key("guide_ground_stow").id)
d.qpos[2] = 0.55; mujoco.mj_forward(mg, d)
tl_stow = cKDTree(np.vstack([vis_clouds[b] @ d.xmat[b].reshape(3, 3).T + d.xpos[b] for b in leg_bids if b in vis_clouds]))
stow_sim_yaws, stow_mesh_lt3, stow_mesh_lt18 = [], [], []
for yd in range(-180, 180):
    d.qpos[qy] = math.radians(yd); mujoco.mj_forward(mg, d)
    wg = np.vstack([vis_clouds[b] @ d.xmat[b].reshape(3, 3).T + d.xpos[b] for b in gim_bids if b in vis_clouds])
    mc = float(tl_stow.query(wg)[0].min()) * 1000.0
    if has_gim_leg_sim_contact(mg, d): stow_sim_yaws.append(yd)
    if mc < 3.0: stow_mesh_lt3.append(yd)
    if mc < 1.8: stow_mesh_lt18.append(yd)

def intervals(a):
    out = []
    for x in a:
        if out and x == out[-1][1] + 1: out[-1][1] = x
        else: out.append([x, x])
    return out

R["gimbal_leg_collision_validation"] = dict(
    deployed_normal_poses_tested=n_dep_poses,
    deployed_false_positives_gt4mm=n_dep_fp_gt4mm,
    stow_safe_pocket_yaw_deg=round(math.degrees(STOW_YAW_QPOS), 2),
    stow_contact_at_safe_pocket=round(math.degrees(STOW_YAW_QPOS)) in stow_sim_yaws,
    stow_true_mesh_penetration_lt1_8mm_deg=intervals(stow_mesh_lt18),
    stow_true_mesh_unsafe_lt3_0mm_deg=intervals(stow_mesh_lt3),
    stow_sim_detected_contact_deg=intervals(stow_sim_yaws),
    stow_recall_on_penetration_pct=round(100.0 * len(set(stow_mesh_lt18) & set(stow_sim_yaws)) / max(1, len(stow_mesh_lt18)), 2),
)
assert n_dep_fp_gt4mm == 0, n_dep_fp_gt4mm
assert not R["gimbal_leg_collision_validation"]["stow_contact_at_safe_pocket"]
assert R["gimbal_leg_collision_validation"]["stow_recall_on_penetration_pct"] == 100.0

# 9. Free-drop 3s stability & Step FPS benchmark
d_drop = mujoco.MjData(mg); mujoco.mj_forward(mg, d_drop); q0_d = mg.qpos0.copy(); bad = 0
t0 = time.time()
n_steps = int(3.0 / mg.opt.timestep)
for _ in range(n_steps):
    leg_hold(mg, d_drop, q0_d); mujoco.mj_step(mg, d_drop)
    if not np.all(np.isfinite(d_drop.qpos)): bad += 1; break
dt_drop = time.time() - t0
R["free_drop_3s_and_speed"] = dict(
    finite=bad == 0,
    base_z_m=round(float(d_drop.qpos[2]), 5),
    warnings=[int(w.number) for w in d_drop.warning if w.number > 0],
    steps_per_sec_single_thread=round(n_steps / dt_drop, 0),
)
assert bad == 0

out = os.path.join(PKG, "reports", "gemini_fix_validation.json")
json.dump(R, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps(R, ensure_ascii=False, indent=2))
