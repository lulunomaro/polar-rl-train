# -*- coding: utf-8 -*-
"""Shared MJCF & geometry patch logic for MOD4v4 -> MOD4v4gemini (SCUT-aligned + DM-J4310 + Exact Hull Collisions)."""
import os, re, struct, math, glob
import numpy as np

SRC = r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\mod4v4_audit\MOD4v4"
HULL_CACHE = r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\mod4v4_audit\hulls_cache"

FOLD_MASS = 0.7804303729717087
YAW_MASS = 0.5508142897658876

# Raw CAD pitch axis & camera forward direction (in saved SolidWorks pose where gimbal pointed into stow pocket)
PITCH_AXIS_CAD = np.array([-0.5046705004249628, 0.8633120443969364, 0.0])
FORWARD_DIR_CAD = -np.cross(PITCH_AXIS_CAD, [0.0, 0.0, 1.0])   # = (-0.863312044397, -0.504670500425, 0.0)
# Angle to rotate the saved CAD gimbal around +Z so gimbal_yaw_joint=0 faces chassis +X (matching SCUT WheelBipe V14_2)
CAD_TO_FORWARD_YAW_RAD = float(-math.atan2(FORWARD_DIR_CAD[1], FORWARD_DIR_CAD[0]))   # +2.612592403477097 rad (+149.690498 deg)
STOW_YAW_QPOS = -CAD_TO_FORWARD_YAW_RAD                                               # -2.612592403477097 rad (-149.690498 deg)

# Rotation matrix R0 = Rz(CAD_TO_FORWARD_YAW_RAD) and quaternion q0 = (w, x, y, z)
_c0, _s0 = math.cos(CAD_TO_FORWARD_YAW_RAD), math.sin(CAD_TO_FORWARD_YAW_RAD)
R_FWD = np.array([[_c0, -_s0, 0.0],
                  [_s0,  _c0, 0.0],
                  [0.0,  0.0, 1.0]], dtype=np.float64)
Q_FWD_WXYZ = np.array([math.cos(0.5 * CAD_TO_FORWARD_YAW_RAD), 0.0, 0.0, math.sin(0.5 * CAD_TO_FORWARD_YAW_RAD)], dtype=np.float64)

# Authoritative Damiao DM-J4310-2EC (24V) motor specifications (10:1 internal planetary + 1:1 external ratio)
DM4310 = dict(
    model="DM-J4310-2EC",
    manufacturer="Damiao Technology (达妙科技)",
    bus_voltage_v=24.0,
    gear_ratio_internal=10.0,
    yaw_belt_teeth_drive=51,
    yaw_belt_teeth_driven=51,
    yaw_external_belt_ratio=1.0,
    fold_external_ratio=1.0,
    pitch_external_ratio=1.0,
    continuous_torque_nm=3.0,
    peak_torque_nm=7.0,
    rated_speed_rpm=120.0,
    no_load_speed_rpm=200.0,
    rated_speed_rad_s=120.0 * 2.0 * math.pi / 60.0,      # 12.566370614359172 rad/s
    no_load_speed_rad_s=200.0 * 2.0 * math.pi / 60.0,    # 20.943951023931955 rad/s
    rotor_inertia_kg_m2=1.8e-5,
    output_armature_kg_m2=0.0018,                        # 1.8e-5 * (10.0 * 1.0)^2
    passive_damping_nm_s_rad=0.02,
    envelope_intercept_nm=7.5,                           # linear fit through (120 rpm, 3 Nm) and (200 rpm, 0 Nm), clipped at 7.0 Nm
    envelope_slope_nm_s_rad=3.0 / ((200.0 - 120.0) * 2.0 * math.pi / 60.0),  # 0.35809862195676453 N*m*s/rad
    nominal_mass_kg=0.300,
)

JOINT_ARM = DM4310["output_armature_kg_m2"]     # 0.0018 kg*m^2
JOINT_DAMP = DM4310["passive_damping_nm_s_rad"] # 0.02 N*m*s/rad
TAU_MAX = DM4310["peak_torque_nm"]              # 7.0 N*m

# Default scene (nu=6) passive hold gains & USD default angular drive gains (SCUT-aligned)
HOLD_YAW_KP = 20.0     # N*m/rad in default nu=6 MJCF scene so yaw stays forward without a 7th actuator
HOLD_YAW_KD = 0.8      # N*m*s/rad
USD_YAW_KP = 0.0       # Matches SCUT wheelbipe_V14_2.py: gimbal_yaw stiffness=0.0, damping=0.5 (velocity / effort mode)
USD_YAW_KD = 0.5
HOLD_FP_KP = 40.0      # Fold & Pitch hold stiffness (N*m/rad)
HOLD_FP_KD = 1.2       # Fold & Pitch hold damping (N*m*s/rad)

LEG_BODIES = [
    "left_rear1_link", "left_front3_link", "left_front4_link", "left_rear2_link", "left_wheel_link",
    "left_spring1_link", "left_spring2_link", "left_front1_link", "left_front2_link",
    "right_rear1_link", "right_front3_link", "right_front4_link", "right_rear2_link", "right_wheel_link",
    "right_spring1_link", "right_spring2_link", "right_front1_link", "right_front2_link",
]
GIMBAL_BODIES = [
    "gimbal_yaw_link", "gimbal_fold_link", "gimbal_pitch_link", "gimbal_uwb_tray_link", "gimbal_uwb_arm_link",
]


def _stl_tris(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        raw = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    return np.frombuffer(raw[:, 12:48].tobytes(), dtype="<f4").reshape(n, 3, 3).astype(np.float64)


def fold_mass_properties(src=SRC):
    """Exact solid (signed tetrahedra) COM + inertia of the three fold STL shells, scaled to the CAD mass."""
    vol_t, m1, C = 0.0, np.zeros(3), np.zeros((3, 3))
    allv = []
    for i in range(3):
        t = _stl_tris(os.path.join(src, "mjcf", "assets", f"v4_vis_gimbal_fold_link_s_step_0{i}.stl"))
        allv.append(t.reshape(-1, 3))
        a, b, c = t[:, 0], t[:, 1], t[:, 2]
        det = np.einsum("ij,ij->i", a, np.cross(b, c))
        vol_t += det.sum() / 6.0
        m1 += (det[:, None] * (a + b + c)).sum(0) / 24.0
        for p in range(3):
            for q in range(3):
                s = (2 * a[:, p] * a[:, q] + 2 * b[:, p] * b[:, q] + 2 * c[:, p] * c[:, q]
                     + a[:, p] * b[:, q] + b[:, p] * a[:, q] + b[:, p] * c[:, q] + c[:, p] * b[:, q]
                     + c[:, p] * a[:, q] + a[:, p] * c[:, q])
                C[p, q] += (det * s).sum() / 120.0
    com = m1 / vol_t
    Cc = C - vol_t * np.outer(com, com)
    I = (np.trace(Cc) * np.eye(3) - Cc) * (FOLD_MASS / vol_t)
    allv = np.vstack(allv)
    vmin, vmax = allv.min(0), allv.max(0)
    return dict(volume_m3=vol_t, density=FOLD_MASS / vol_t, com=com, I=I,
                bbox_center=(vmin + vmax) / 2, bbox_half=(vmax - vmin) / 2)


def yaw_mass_properties_rotated():
    """Rotate gimbal_yaw_link's original COM and inertia tensor by R_FWD into the SCUT forward-zero frame."""
    com_old = np.array([-0.01724401756, 0.00851317838962, 0.0218078942176], dtype=np.float64)
    Ixx, Iyy, Izz, Ixy, Ixz, Iyz = (
        0.00151075464026, 0.00119207905756, 0.00200053201685,
        2.56138383725e-05, 0.000190853020898, -3.02835592522e-05,
    )
    I_old = np.array([[Ixx, Ixy, Ixz],
                      [Ixy, Iyy, Iyz],
                      [Ixz, Iyz, Izz]], dtype=np.float64)
    com_new = R_FWD @ com_old
    I_new = R_FWD @ I_old @ R_FWD.T
    return dict(com=com_new, I=I_new)


def list_cached_hulls(cache_dir=HULL_CACHE):
    files = sorted(glob.glob(os.path.join(cache_dir, "v4_col_*.stl")))
    if not files:
        raise RuntimeError(f"No cached hulls found in {cache_dir}")
    body_map = {}
    for fp in files:
        mn = os.path.splitext(os.path.basename(fp))[0]
        bn = re.match(r"^v4_col_(.+)_\d\d$", mn).group(1)
        body_map.setdefault(bn, []).append((mn, fp))
    return body_map


def _sub1(text, old, new):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"expected exactly one occurrence, got {n}: {old[:95]}")
    return text.replace(old, new)


def patch_scene(xml, props, yaw_props, body_hulls, *, actuated, qpos_deployed_grounded=None):
    fmt = lambda v: " ".join(repr(float(x)) for x in v)
    I_fold = props["I"]
    I_yaw = yaw_props["I"]

    # 1. model name
    xml = _sub1(xml, 'model="MOD4v4_articulated_load"',
                'model="MOD4v4gemini_gimbal_actuated"' if actuated else 'model="MOD4v4gemini_articulated_load"')

    # 2. Register convex-hull collision STL meshes in <asset>
    mesh_lines = []
    for bn in sorted(body_hulls.keys()):
        for mn, _ in body_hulls[bn]:
            mesh_lines.append(f'    <mesh name="{mn}" file="{mn}.stl" />')
    xml = _sub1(xml, '  </asset>', '\r\n'.join(mesh_lines) + '\r\n  </asset>')

    # 3. Re-zero gimbal_yaw_link to SCUT forward convention (gimbal_yaw_joint=0 faces chassis +X):
    #    3a. Rotate gimbal_yaw_link inertial COM + fullinertia by R_FWD
    xml = _sub1(xml,
        '<inertial mass="0.550814289766" pos="-0.01724401756 0.00851317838962 0.0218078942176" '
        'fullinertia="0.00151075464026 0.00119207905756 0.00200053201685 2.56138383725e-05 0.000190853020898 -3.02835592522e-05" />',
        f'<inertial mass="0.550814289766" pos="{fmt(yaw_props["com"])}" '
        f'fullinertia="{fmt([I_yaw[0,0], I_yaw[1,1], I_yaw[2,2], I_yaw[0,1], I_yaw[0,2], I_yaw[1,2]])}" />')

    #    3b. Rotate gimbal_yaw_link's 5 visual meshes by Q_FWD_WXYZ
    q_str = fmt(Q_FWD_WXYZ)
    for gname in ["gimbal_yaw_envelope", "v4_vis_gimbal_yaw_link_s_step_01", "v4_vis_gimbal_yaw_link_s_step_02",
                  "v4_vis_gimbal_yaw_link_s_step_03", "v4_vis_gimbal_yaw_link_s_step_04"]:
        pat = re.compile(r'(<geom name="' + re.escape(gname) + r'" class="visual"[^>]*?)\s*/>')
        xml, n = pat.subn(rf'\1 quat="{q_str}" />', xml)
        if n != 1:
            raise RuntimeError(f"Failed rotating visual geom {gname}")

    #    3c. Rotate direct child attachments under gimbal_yaw_link (gimbal_fold_link and gimbal_uwb_arm_link) by R_FWD / Q_FWD_WXYZ
    fold_pos_new = R_FWD @ np.array([-0.0252335250438, 0.0431656022585, 0.0404999999997], dtype=np.float64)
    arm_pos_new = R_FWD @ np.array([0.0651714425141, -0.0276955425887, 0.0251090935504], dtype=np.float64)
    xml = _sub1(xml,
        '<body name="gimbal_fold_link" pos="-0.0252335250438 0.0431656022585 0.0404999999997">',
        f'<body name="gimbal_fold_link" pos="{fmt(fold_pos_new)}" quat="{q_str}">')
    xml = _sub1(xml,
        '<body name="gimbal_uwb_arm_link" pos="0.0651714425141 -0.0276955425887 0.0251090935504">',
        f'<body name="gimbal_uwb_arm_link" pos="{fmt(arm_pos_new)}" quat="{q_str}">')

    # 4. Fix gimbal_fold_link exact solid mass properties (local frame of gimbal_fold_link unchanged)
    xml = _sub1(xml,
        '<inertial mass="0.780430372972" pos="0.112137397505 -0.00398847976182 0.153497081058" '
        'fullinertia="0.144405896859 0.24663279416 0.115782352628 -0.0197319354988 -0.121331097213 -0.0239890268415" />',
        f'<inertial mass="0.780430372972" pos="{fmt(props["com"])}" '
        f'fullinertia="{fmt([I_fold[0,0], I_fold[1,1], I_fold[2,2], I_fold[0,1], I_fold[0,2], I_fold[1,2]])}" />')

    # 5. Add gimble_aim site on gimbal_pitch_link BEFORE replacing pitch contact geom
    xml = _sub1(xml,
        '<geom class="collision" name="gimbal_pitch_contact"',
        f'<site name="gimbal_aim" pos="0 0 0" zaxis="{fmt(FORWARD_DIR_CAD)}" size=".004 .004 .06" type="cylinder" rgba="1 .2 .2 1" group="4" />\r\n'
        '            <geom class="collision" name="gimbal_pitch_contact"')

    # 6. Remove coarse gimbal ellipsoids & inaccurate centerline thigh/shin/input capsules, inject exact-CAD convex hulls
    for old_g in ["gimbal_yaw_contact", "gimbal_fold_contact", "gimbal_pitch_contact",
                  "left_thigh_collision", "right_thigh_collision",
                  "left_shin_collision", "right_shin_collision",
                  "left_input_collision", "right_input_collision"]:
        xml, n = re.subn(r'\r?\n[ \t]*<geom [^>]*name="' + re.escape(old_g) + r'"[^>]*/>', '', xml)
        if n != 1:
            raise RuntimeError(f"Expected 1 {old_g}, got {n}")

    for bn, mlist in body_hulls.items():
        g_lines = "\r\n".join(f'          <geom name="{mn}" class="collision" type="mesh" mesh="{mn}" />' for mn, _ in mlist)
        pat = re.compile(r'(<body name="' + re.escape(bn) + r'"[^>]*>\r?\n[ \t]*<inertial [^>]*/>\r?\n(?:[ \t]*<joint [^>]*/>\r?\n)?)')
        xml, n = pat.subn(r'\1' + g_lines + '\r\n', xml, count=1)
        if n != 1:
            raise RuntimeError(f"Failed injecting hulls into body {bn}")

    # 7. Damiao DM-J4310-2EC (24V) armature & damping on gimbal joints
    for jn in ["gimbal_yaw_joint", "gimbal_fold_joint", "gimbal_pitch_joint"]:
        if actuated:
            extra = f'damping="{JOINT_DAMP}" armature="{JOINT_ARM}"'
        else:
            if jn == "gimbal_yaw_joint":
                extra = f'damping="{JOINT_DAMP + HOLD_YAW_KD}" armature="{JOINT_ARM}" stiffness="{HOLD_YAW_KP}" springref="0"'
            else:
                extra = f'damping="{JOINT_DAMP + HOLD_FP_KD}" armature="{JOINT_ARM}" stiffness="{HOLD_FP_KP}" springref="0"'
        pat = re.compile(r'(<joint name="' + re.escape(jn) + r'" [^>]*?)damping="0" armature="0"')
        xml, n = pat.subn(r'\1' + extra, xml)
        if n != 1:
            raise RuntimeError(f"Failed updating joint {jn}")

    # 8. UWB parallelogram couplings: match leg closed-chain solver rigidity
    for nm, coef in [("gimbal_uwb_tray_joint_coupling", "0 -1 0 0 0"), ("gimbal_uwb_arm_joint_coupling", "0 1 0 0 0")]:
        j1 = nm.replace("_coupling", "")
        xml = _sub1(xml,
            f'<joint name="{nm}" joint1="{j1}" joint2="gimbal_fold_joint" polycoef="{coef}" />',
            f'<joint name="{nm}" joint1="{j1}" joint2="gimbal_fold_joint" polycoef="{coef}" solref=".001 1" solimp=".9999 .99999 .0001" />')

    # 9. Enable physical gimbal <-> leg collisions & complete same-side intra-leg closed-chain exclusions
    for lb in LEG_BODIES:
        for gb in GIMBAL_BODIES:
            line = f'<exclude body1="{lb}" body2="{gb}" />'
            xml, n = re.subn(r'\r?\n[ \t]*' + re.escape(line), '', xml)
            if n != 1:
                raise RuntimeError(f"Missing exclude {line}")

    extra_excl = []
    for s in ("left", "right"):
        same_leg = [f"{s}_rear1_link", f"{s}_front1_link", f"{s}_front2_link", f"{s}_front3_link",
                    f"{s}_front4_link", f"{s}_rear2_link", f"{s}_spring1_link", f"{s}_spring2_link", f"{s}_wheel_link"]
        for i in range(len(same_leg)):
            for j in range(i + 1, len(same_leg)):
                b1, b2 = same_leg[i], same_leg[j]
                if f'body1="{b1}" body2="{b2}"' not in xml and f'body1="{b2}" body2="{b1}"' not in xml:
                    extra_excl.append(f'    <exclude body1="{b1}" body2="{b2}" />')
    xml = _sub1(xml, '  </contact>', '\r\n'.join(extra_excl) + '\r\n  </contact>')

    # 10. Actuated variant: append 3 DM-J4310 torque <motor>s (indices 6, 7, 8, matching motors 0..5 & SCUT IdealPDActuator) + sensors
    if actuated:
        xml = _sub1(xml,
            '    <motor name="right_wheel_joint_motor" joint="right_wheel_joint" gear="1" ctrlrange="-5.77590977444 5.77590977444" forcerange="-5.77590977444 5.77590977444" />\r\n',
            '    <motor name="right_wheel_joint_motor" joint="right_wheel_joint" gear="1" ctrlrange="-5.77590977444 5.77590977444" forcerange="-5.77590977444 5.77590977444" />\r\n'
            f'    <motor name="gimbal_yaw_joint_motor" joint="gimbal_yaw_joint" gear="1" ctrlrange="-{TAU_MAX} {TAU_MAX}" forcerange="-{TAU_MAX} {TAU_MAX}" />\r\n'
            f'    <motor name="gimbal_fold_joint_motor" joint="gimbal_fold_joint" gear="1" ctrlrange="-{TAU_MAX} {TAU_MAX}" forcerange="-{TAU_MAX} {TAU_MAX}" />\r\n'
            f'    <motor name="gimbal_pitch_joint_motor" joint="gimbal_pitch_joint" gear="1" ctrlrange="-{TAU_MAX} {TAU_MAX}" forcerange="-{TAU_MAX} {TAU_MAX}" />\r\n')
        xml = _sub1(xml, '  </sensor>',
            '    <jointpos name="gimbal_yaw_pos" joint="gimbal_yaw_joint" />\r\n'
            '    <jointvel name="gimbal_yaw_vel" joint="gimbal_yaw_joint" />\r\n'
            '    <jointpos name="gimbal_fold_pos" joint="gimbal_fold_joint" />\r\n'
            '    <jointvel name="gimbal_fold_vel" joint="gimbal_fold_joint" />\r\n'
            '    <jointpos name="gimbal_pitch_pos" joint="gimbal_pitch_joint" />\r\n'
            '    <jointvel name="gimbal_pitch_vel" joint="gimbal_pitch_joint" />\r\n'
            '    <framequat name="gimbal_aim_orientation" objtype="site" objname="gimbal_aim" />\r\n'
            '    <gyro name="gimbal_aim_gyro" site="gimbal_aim" />\r\n'
            '  </sensor>')

    # 11. Update guide_ground_stow keyframe yaw angle from 0 -> STOW_YAW_QPOS (-2.6125924 rad) so stow pose stays in the exact safe pocket!
    xml, n = re.subn(
        r'(<key name="guide_ground_stow" qpos="[^"]*?) 0 (0\.951204442337 -0\.938114472947 -0\.951204442337 0\.951204442337")',
        rf'\1 {STOW_YAW_QPOS!r} \2',
        xml, count=1)
    if n != 1:
        raise RuntimeError("Failed updating guide_ground_stow yaw angle")

    if qpos_deployed_grounded is not None:
        key_dep = f'    <key name="deployed_forward" qpos="{" ".join(repr(float(x)) for x in qpos_deployed_grounded)}" />\r\n'
        xml = _sub1(xml, '  </keyframe>', key_dep + '  </keyframe>')

    return xml
