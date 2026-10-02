"""Emit a wheelbipe_ros2_sim2sim compatible description of the VALIDATED closed chain.

Unlike the earlier serial-chain export this one starts from the MJCF that was proven to
reproduce the SJTU similar-linkage (scripts/cc_gaps.py: 0.0000 mm loop closure over the
whole workspace; scripts/cc_warp_test.py: 0.02 deg agreement with the mujoco-warp GPU
solver), so the geometry is copied, not re-derived.  Only the deployment-specific
plumbing changes:

  * no <actuator> block  - the framework injects effort through qfrc_applied
  * visual geoms stay in group 2 (rendered), collision geoms stay in group 3 (hidden)
  * meshes renamed to *.STL under ../meshes, root lifted so the wheels start on the floor
  * the eight-joint ros2_control contract is satisfied natively: left/right front1,
    rear1, wheel, spring2 all exist, and spring2 is a REAL gas-spring slider now (the
    earlier "locked placeholder" hack is gone)

Outputs (under --out): mjcf/{rm_vehicle.xml,scene.xml}, meshes/*.STL,
                       xacro/{robot_sim.xacro,robot_real.xacro}, config/rm_vehicle.yaml
"""
import argparse, json, math, os, re, shutil
import numpy as np
import mujoco

ap = argparse.ArgumentParser()
ap.add_argument("--src", default=r"D:/claude2/fangzhen/robot/out_cc")
ap.add_argument("--out", default=r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle")
ap.add_argument("--prefix", default="rm_vehicle")
ap.add_argument("--stand-z", type=float, default=0.075)
args = ap.parse_args()

mj_dir = os.path.join(args.out, "mjcf"); me = os.path.join(args.out, "meshes")
xc = os.path.join(args.out, "xacro");   cf = os.path.join(args.out, "config")
for dd in (mj_dir, me, xc, cf):
    os.makedirs(dd, exist_ok=True)
for f in list(os.listdir(me)):
    os.remove(os.path.join(me, f))

# ------------------------------------------------------------------ 1. meshes
xml = open(os.path.join(args.src, "rm_vehicle_cc.xml"), encoding="utf-8").read()

import re as _re
def _limit(pattern, default):
    m = _re.search(pattern, xml)
    if not m:
        return default
    return max(abs(float(v)) for v in m.group(1).replace("|", " ").split())

# the MJCF is the single source of truth for the actuator ceilings, so the deployment
# config can never drift away from the plant it is supposed to represent.
LEG_TORQUE = _limit(r'name="left_front1_ctrl"[^>]*forcerange="([-0-9 ]+)"', 40.0)
WHEEL_TORQUE = _limit(r'name="left_wheel_ctrl"[^>]*forcerange="([-0-9. ]+)"', 6.4188)

# The controller YAML used to hard-code a FIFTH copy of the PD gains and the action scales
# (60 / 2 / 1.5 / 0.5 / 10.0, and motion_angular_z +-1.0).  Two of those were already wrong
# when it was written and +-1.0 silently deletes the high-rate gyro (小陀螺).  Everything now
# comes from train/deploy/contract.json, generated from the training config by
# scripts/write_deploy_contract.py; scripts/check_contract_drift.py fails if they disagree.
CONTRACT_JSON = os.path.join(r"D:/claude2/fangzhen", "train/deploy/contract.json")
if os.path.exists(CONTRACT_JSON):
    CT = json.load(open(CONTRACT_JSON, encoding="utf-8"))
    print("deployment contract:", {k: CT[k] for k in sorted(CT)
                                   if k in ("leg_kp", "leg_kd", "wheel_kd",
                                            "leg_action_scale", "wheel_action_scale",
                                            "command_limits", "checkpoint")})
else:
    print("WARNING: %s missing -> falling back to the values v12 was trained with. Run "
          "scripts/write_deploy_contract.py before exporting a deployment." % CONTRACT_JSON)
    CT = dict(leg_kp=60.0, leg_kd=2.0, wheel_kd=1.5, leg_action_scale=0.5,
              wheel_action_scale=10.0,
              command_limits=dict(linear_x=[-1.0, 1.8], angular_z=[-1.0, 1.0]))
_LX = CT["command_limits"]["linear_x"]
_AZ = CT["command_limits"]["angular_z"]
print("plant torques -> legs %.1f N*m, wheels %.1f N*m" % (LEG_TORQUE, WHEEL_TORQUE))
meshes = re.findall(r'<mesh name="([^"]+)" file="([^"]+)"', xml)
for name, fn in meshes:
    src = os.path.join(args.src, "meshes", fn)
    shutil.copy2(src, os.path.join(me, fn[:-4] + ".STL"))
    xml = xml.replace('file="%s"' % fn, 'file="../meshes/%s.STL"' % fn[:-4])
xml = xml.replace(' meshdir="meshes/"', "")

# ------------------------------------------------------------------ 2. MJCF edits
# Contact model.  Training builds the robot through mjlab CollisionCfg(
#     geom_names_expr=collide_geoms, contype=0, conaffinity=1,
#     condim={wheels: 6, ".*": 1}, priority={wheels: 1},
#     friction={wheels: (1.2, 0.02, 0.002)}, disable_other_geoms=True),
# which is NOT what the raw MJCF says.  Three concrete mismatches made the deployed
# plant a different physical object than the trained one:
#   * leg/spring capsules: MJCF default condim=3 (sticking friction) vs trained condim=1
#   * chassis box:         MJCF conaffinity=1 (can touch the floor) vs trained collision OFF
#   * wheels:              MJCF friction "1.2 0.01 0.001" vs trained "1.2 0.02 0.002"
# Reproduce the trained contact model so the policy is evaluated on the plant it learned.
_CAPS = re.compile(r"<geom name=\"[^\"]*_(?:rear1|rear2|front[1-4]|spring[12])_col\"")
def _condim1(mo):
    t = mo.group(0)
    return t if "condim=" in t else re.sub(r"<geom name=", '<geom condim="1" name=', t, count=1)
xml = _CAPS.sub(_condim1, xml)
# rewrite in place - adding a second contype/conaffinity would be a duplicate attribute
def _box_off(mo):
    return re.sub(r'conaffinity="\d+"', 'conaffinity="0"', mo.group(0))
xml = re.sub(r'<geom name="base_col"[^>]*>', _box_off, xml, count=1)
xml = xml.replace('name="left_wheel_col"', 'friction="1.2 0.02 0.002" name="left_wheel_col"')
xml = xml.replace('name="right_wheel_col"', 'friction="1.2 0.02 0.002" name="right_wheel_col"')
print("contact model -> trained: capsules condim=1, chassis box non-colliding, wheel friction 1.2/0.02/0.002")
# Physics rate: KEEP the plant's own 1 ms step.  Matching training's 2 ms looks principled but
# is not, because the two sims apply actuator damping by different mechanisms.  mjlab drives the
# wheels through a MuJoCo joint actuator whose affine bias MuJoCo integrates IMPLICITLY; the
# deployment injects tau = kd*(v_cmd - omega) as an explicit qfrc_applied, which only stays
# stable while kd*dt < M.  With the wheel DOF inertia M = 1.6169e-3 kg*m^2 (measured from the
# plant mass matrix; body 6.169e-4 + armature 1.0e-3) and kd = 1.5:
#     dt = 0.001 -> kd*dt/M = 0.928   (stable)
#     dt = 0.002 -> kd*dt/M = 1.855   (UNSTABLE: overshoots every single step)
# Reproduce with scripts/wheel_servo_stability.py.
if os.environ.get("RM_DEPLOY_DT"):
    xml = re.sub(r"(<option [^>]*?timestep=\")[0-9.]+(\")",
                 r"\g<1>%s\g<2>" % os.environ["RM_DEPLOY_DT"], xml, count=1)
print("deployment physics timestep: keeping the plant's own 1 ms "
      "(2 ms makes the explicit wheel servo diverge; see wheel_servo_stability.py)")
# Solver regime.  The task was trained with mjlab SimulationCfg(timestep=0.002,
# iterations=10, ls_iterations=10, impratio=50, cone="elliptic") while the MJCF ships
# iterations=100 / ls_iterations=50 / impratio=1 / pyramidal.  With six <connect>
# equalities the closed chain is enforced *softly* during training and *stiffly* in the
# deployment, which is a materially different plant - the deployed policy balances but
# refuses to execute the jump.  Replicate the training regime here.
import os as _os
# Measured: with iterations=10 / impratio=50 the CPU Newton solver cannot hold the six
# <connect> equalities and MuJoCo reports "Nan, Inf or huge value in QACC at DOF 4"
# within 0.27 s.  mjlab only gets away with it because it runs mujoco-warp on the GPU.
# Keep the plant's own stiff, accurate regime in the deployment.
SOLVE_TRAIN = _os.environ.get("RM_DEPLOY_TRAIN_SOLVER", "0") == "1"
if SOLVE_TRAIN:
    xml = re.sub(r'<option ([^>]*?)/>',
                 r'<option \1 iterations="10" ls_iterations="10" impratio="50" '
                 r'cone="elliptic"/>', xml, count=1)
    xml = re.sub(r' iterations="100" ls_iterations="50"', '', xml, count=1)
    print("deployment solver -> training regime (iter 10, ls 10, impratio 50, elliptic)")


# The plant already uses the convention validated in MuJoCo: visual geoms in group 2 (shown),
# collision primitives in group 3 (hidden).  The old 3->2 / 4->1 remap was a leftover from when
# visuals lived in group 3; with the current plant it pushed every collision capsule and the
# chassis box into the visible set, so the deployed sim drew a translucent shell over the robot.
# (group="4" no longer exists, so that half of the remap was a silent no-op.)
xml = re.sub(r'\n  <actuator>.*?\n  </actuator>\n', "\n", xml, flags=re.S)
xml = xml.replace('<body name="base_link" pos="0 0 0">',
                  '<body name="base_link" pos="0 0 %g">' % args.stand_z)
xml = xml.replace('<mujoco model="rm_vehicle_cc">', '<mujoco model="%s_cc_sim2sim">' % args.prefix)
# the bridge expects the classic SCUT collision-geom naming for its contact lookups
xml = xml.replace('_col"', '_link_collision"')
# The stand-up keyframe (scripts/make_stand_keyframe.py, verified: max equality gap 0.019 mm,
# wheels on the floor, no passive joint on a limit).  Without it the bridge spawns at qpos0 and the
# preloaded gas spring (350 N = 1.8x body weight) throws the CLOSED chain onto its other assembly
# branch during the seconds before a controller activates - docs/HOWTO.md sections 33 and 35.
_KF = r"D:/claude2/fangzhen/docs/audit/stand_keyframe.json"
if os.path.exists(_KF):
    _k = json.load(open(_KF, encoding="utf-8"))
    _line = '  <keyframe><key name="stand" qpos="%s" qvel="%s"/></keyframe>' % (
        " ".join("%.6f" % v for v in _k["qpos"]), " ".join("0" for _ in _k["qvel"]))
    xml = xml.replace("</mujoco>",
                      "<!-- STAND_KEYFRAME_BEGIN -->\n%s\n<!-- STAND_KEYFRAME_END -->\n</mujoco>"
                      % _line)
    print("stand keyframe injected (base_z=%.5f, max eq gap=%.5f mm)"
          % (_k["base_z"], _k["eq_gap_max_mm"]))
else:
    print("WARNING: %s missing - the deployment will spawn at qpos0 and the closed chain can flip"
          % _KF)
open(os.path.join(mj_dir, "rm_vehicle.xml"), "w", encoding="utf-8", newline="\n").write(xml)
m = mujoco.MjModel.from_xml_path(os.path.join(mj_dir, "rm_vehicle.xml"))
print("MJCF ok: nq=%d nv=%d nu=%d neq=%d nbody=%d mass=%.2f kg"
      % (m.nq, m.nv, m.nu, m.neq, m.nbody, sum(m.body_mass)))

sc = ['<?xml version="1.0" encoding="utf-8"?>',
      '<mujoco model="%s scene">' % args.prefix, '  <include file="rm_vehicle.xml"/>',
      '  <statistic center="0 0 0.4" extent="0.8"/>',
      '  <visual><headlight diffuse="0.6 0.6 0.6" ambient="0.1 0.1 0.1" specular="0.9 0.9 0.9"/>',
      '    <global azimuth="-140" elevation="-20" offwidth="1280" offheight="720"/></visual>',
      '  <asset><texture type="skybox" builtin="flat" rgb1="0 0 0" rgb2="0 0 0" width="512" height="3072"/>',
      '    <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" '
      'rgb2="0.1 0.2 0.3" markrgb="0.8 0.8 0.8" width="300" height="300"/>',
      '    <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" '
      'reflectance="0.2"/></asset>',
      '  <worldbody><light pos="1 0 3.5" dir="0 0 -1" directional="true"/>',
      '    <geom name="floor" size="0 0 0.05" type="plane" material="groundplane" '
      'contype="1" conaffinity="255" friction="1.6 0.01 0.001"/></worldbody>',
      '</mujoco>']
open(os.path.join(mj_dir, "scene.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(sc) + "\n")

# ---------------------------------------------------------------- 2b. map-shaped scene
# The RL policy is trained on the RMUC2026 7v7 field (docs/MAP_2026.md), so the
# deployment simulator gets a matching scene: the measured ramp incline, stair riser/run
# and barricade size are written straight out of cad/out_map/field_dims.json.
FD = r"D:/claude2/fangzhen/cad/out_map/field_dims.json"
if os.path.isfile(FD):
    dims = json.load(open(FD, encoding="utf-8"))
    s_lo, s_hi = dims["slope_deg"]; h_lo, h_hi = dims["step_height_m"]
    r_lo, r_hi = dims["step_run_m"]; o_lo, o_hi = dims["obstacle_height_m"]
    w_lo, w_hi = dims["obstacle_width_m"]
    ang = math.radians(float(np.clip((s_lo + s_hi) / 2.0, 8.0, 30.0)))
    rise = 0.62; ln = rise / math.tan(ang)
    n_st = 5; rise_st = rise / n_st; run_st = float(np.clip((r_lo + r_hi) / 2 * 0.55, 0.18, 0.45))
    bh = float(np.clip((o_lo + o_hi) / 2, 0.05, 0.30)); bw = float(np.clip((w_lo + w_hi) / 2, 0.25, 0.9))
    # NOTE: the robot spawns at the model origin, so the first flat pad must COVER x=0.
    # With the pad starting at x=0 the wheels hung over the edge and the whole robot fell
    # through the world (z -> -7000 m, zero contacts) in the first field-scene test.
    g = []; x = 0.0
    # A catch-all plane UNDER everything: without it a failed climb meant falling into
    # the void (z -> -1000 m) instead of a readable tip-over on the ground.
    g.append('    <geom name="ground" type="plane" size="0 0 0.05" contype="1" conaffinity="255" '
             'friction="1.6 0.02 0.002" rgba="0.34 0.38 0.44 1" pos="0 0 -0.02"/>')
    g.append('    <geom name="flat_spawn" type="box" size="4.0 3 0.06" pos="%.2f 0 -0.06" contype="1" '
             'conaffinity="255" friction="1.6 0.02 0.002" rgba="0.42 0.46 0.52 1"/>' % (x + 1.5))
    x += 5.5
    thick = 0.35
    cz = rise / 2 - thick / 2 * math.cos(ang)
    g.append('    <geom name="ramp" type="box" size="%.2f 3 %.2f" pos="%.2f 0 %.2f" zaxis="%.4f 0 %.4f" '
             'contype="1" conaffinity="255" friction="1.6 0.02 0.002" rgba="0.5 0.55 0.62 1"/>'
             % (ln / 2 + 0.25, thick, x + ln / 2, cz, math.cos(ang), math.sin(ang)))
    x += ln
    g.append('    <geom name="platform" type="box" size="1.2 3 %.2f" pos="%.2f 0 %.2f" contype="1" '
             'conaffinity="255" friction="1.6 0.02 0.002" rgba="0.55 0.6 0.66 1"/>'
             % (rise / 2, x + 1.2, rise / 2 - 0.05))
    x += 2.4
    for i in range(n_st):
        top = rise - (i + 1) * rise_st
        g.append('    <geom name="step_%d" type="box" size="%.2f 3 %.2f" pos="%.2f 0 %.2f" contype="1" '
                 'conaffinity="255" friction="1.6 0.02 0.002" rgba="0.48 0.53 0.6 1"/>'
                 % (i, run_st / 2, (top + rise_st) / 2 + 0.05, x + run_st / 2, (top + rise_st) / 2))
        x += run_st
    g.append('    <geom name="flat_b" type="box" size="3 3 0.05" pos="%.2f 0 -0.05" contype="1" '
             'conaffinity="255" friction="1.6 0.02 0.002" rgba="0.42 0.46 0.52 1"/>' % (x + 3))
    g.append('    <geom name="barricade" type="box" size="%.2f 1.2 %.2f" pos="%.2f 0 %.2f" contype="1" '
             'conaffinity="255" friction="1.6 0.02 0.002" rgba="0.62 0.5 0.42 1"/>'
             % (bw / 2, bh / 2, x + 5.0, bh / 2 - 0.05))
    sf = ['<?xml version="1.0" encoding="utf-8"?>',
          '<mujoco model="%s on RMUC2026 field">' % args.prefix,
          '  <include file="rm_vehicle.xml"/>',
          '  <visual><global offwidth="1280" offheight="768"/>',
          '    <headlight diffuse="0.7 0.7 0.7" ambient="0.35 0.35 0.35" specular="0.2 0.2 0.2"/></visual>',
          '  <asset><texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" '
          'rgb2="0.25 0.28 0.33" width="256" height="256"/></asset>',
          '  <worldbody>'] + g + [
          '    <light pos="4 -3 6" dir="-0.2 0.2 -1" diffuse="0.9 0.9 0.9" specular="0.2 0.2 0.2"/>',
          '  </worldbody>', '</mujoco>']
    open(os.path.join(mj_dir, "scene_field.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(sf) + "\n")
    print("wrote mjcf/scene_field.xml  (ramp %.1f deg rise %.2f m, %d steps %.1f/%.1f cm, barricade %.0f cm)"
          % (math.degrees(ang), rise, n_st, rise_st * 100, run_st * 100, bh * 100))

# ------------------------------------------------------------------ 3. xacro from the MJCF
def nm(obj, i): return mujoco.mj_id2name(m, obj, i)
TYPE = {mujoco.mjtJoint.mjJNT_HINGE: "revolute", mujoco.mjtJoint.mjJNT_SLIDE: "prismatic",
        mujoco.mjtJoint.mjJNT_FREE: "floating"}
u = ['<?xml version="1.0"?>', '<robot name="%s">' % args.prefix,
     '  <link name="world"/>',
     '  <joint name="fixed_base" type="fixed"><parent link="world"/>'
     '<child link="%s"/><origin xyz="0 0 %g"/></joint>'
     % (nm(mujoco.mjtObj.mjOBJ_BODY, 1), args.stand_z)]
for b in range(1, m.nbody):                       # 0=world, 1=base_link (its own
                                        # <link> must exist for the URDF parser)
    j = next((jj for jj in range(m.njnt) if m.jnt_bodyid[jj] == b
              and m.jnt_type[jj] != mujoco.mjtJoint.mjJNT_FREE), -1)
    par = m.body_parentid[b]
    xyz = " ".join("%.5f" % v for v in m.body_pos[b])
    if j >= 0:
        lo, hi = m.jnt_range[j]
        limited = bool(m.jnt_limited[j])
        axis = " ".join("%.3f" % v for v in m.jnt_axis[j])
        kind = TYPE.get(int(m.jnt_type[j]), "revolute")
        eff = 50.9 if "front1" in nm(mujoco.mjtObj.mjOBJ_JOINT, j) or "rear1" in nm(mujoco.mjtObj.mjOBJ_JOINT, j) \
            else (10.0 if "wheel" in nm(mujoco.mjtObj.mjOBJ_JOINT, j) else 50.0)
        u.append('  <joint name="%s" type="%s">' % (nm(mujoco.mjtObj.mjOBJ_JOINT, j), kind))
        u.append('    <parent link="%s"/><child link="%s"/>'
                 % (nm(mujoco.mjtObj.mjOBJ_BODY, par), nm(mujoco.mjtObj.mjOBJ_BODY, b)))
        u.append('    <origin xyz="%s" rpy="0 0 0"/><axis xyz="%s"/>' % (xyz, axis))
        u.append('    <limit lower="%.4f" upper="%.4f" effort="%.2f" velocity="40"/>'
                 % (lo if limited else -6.28, hi if limited else 6.28, eff))
        u.append('    <dynamics damping="%.4f" friction="%.4f"/>'
                 % (m.dof_damping[m.jnt_dofadr[j]], m.dof_frictionloss[m.jnt_dofadr[j]]))
        u.append('  </joint>')
    else:
        if b == 1:
            pass                      # covered by the fixed_base joint in the header
        else:
            u.append('  <joint name="%s_fixed" type="fixed"><parent link="%s"/><child link="%s"/>'
                     '<origin xyz="%s" rpy="0 0 0"/></joint>'
                     % (nm(mujoco.mjtObj.mjOBJ_BODY, b), nm(mujoco.mjtObj.mjOBJ_BODY, par),
                        nm(mujoco.mjtObj.mjOBJ_BODY, b), xyz))
    u.append('  <link name="%s">' % nm(mujoco.mjtObj.mjOBJ_BODY, b))
    if m.body_mass[b] > 0:
        # MuJoCo stores the diagonalised inertia; the principal-axis frame is good enough
        # for the xacro (the physics comes from the MJCF, this drives TF / ros2_control).
        ii = m.body_inertia[b]
        u.append('    <inertial><origin xyz="0 0 0" rpy="0 0 0"/><mass value="%.4f"/>'
                 '<inertia ixx="%.6f" ixy="0" ixz="0" iyy="%.6f" iyz="0" izz="%.6f"/></inertial>'
                 % (m.body_mass[b], ii[0], ii[1], ii[2]))
    for g in range(m.ngeom):
        if m.geom_bodyid[g] == b and m.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH \
           and m.geom_group[g] == 2:
            mn = nm(mujoco.mjtObj.mjOBJ_MESH, m.geom_dataid[g])
            u.append('    <visual><geometry><mesh filename="package://robot_descriptions/%s/meshes/%s"'
                     ' scale="0.001 0.001 0.001"/></geometry></visual>' % (args.prefix, mn))
    u.append('  </link>')

CONTRACT = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint",
            "left_wheel_joint", "right_wheel_joint", "left_spring2_joint", "right_spring2_joint"]
missing = [c for c in CONTRACT if c not in
           [nm(mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]]
assert not missing, "contract joints missing from the MJCF: %s" % missing

def ros2control_block(plugin, with_dt7):
    r = ['  <ros2_control name="RmVehicleControlCC" type="system">', '    <hardware>',
         '      <plugin>%s</plugin>' % plugin]
    if with_dt7:
        r += ['      <param name="serial_port">/dev/wheelbipe_h7</param>',
              '      <param name="baudrate">2000000</param>',
              '      <param name="serial_reconnect_interval_ms">1000</param>',
              '      <param name="state_timeout_ms">100</param>']
    r.append('    </hardware>')
    for jn in CONTRACT:
        wheel, spring = "wheel" in jn, "spring" in jn
        eff = 10.0 if wheel else (50.0 if spring else 50.9)
        lo, hi = (-5.0, 5.0) if spring else (-eff, eff)
        r.append('    <joint name="%s">' % jn)
        for ci in ("position", "velocity"):
            r.append('      <command_interface name="%s"/>' % ci)
        r.append('      <command_interface name="effort">'
                 '<param name="min">%.1f</param><param name="max">%.1f</param>'
                 '</command_interface>' % (lo, hi))
        r += ['      <command_interface name="kp"/>', '      <command_interface name="kd"/>',
              '      <state_interface name="position"><param name="initial_value">0.0</param></state_interface>']
        for si in ("velocity", "effort"):
            r.append('      <state_interface name="%s"/>' % si)
        r.append('    </joint>')
    r.append('    <sensor name="imu">')
    for s in ("orientation.w", "orientation.x", "orientation.y", "orientation.z",
              "angular_velocity.x", "angular_velocity.y", "angular_velocity.z",
              "linear_acceleration.x", "linear_acceleration.y", "linear_acceleration.z"):
        r.append('      <state_interface name="%s"/>' % s)
    r.append('    </sensor>')
    if with_dt7:
        r.append('    <sensor name="dt7">')
        for s in ("cmd_state", "cmd_vel_x", "cmd_omega_z", "cmd_height"):
            r.append('      <state_interface name="%s"/>' % s)
        r.append('    </sensor>')
    r.append('  </ros2_control>')
    return r

for fn, plugin, dt7 in (("robot_sim.xacro", "mujoco_ros2_control/MujocoSystem", False),
                        ("robot_real.xacro", "template_real_ros2_ctrl::RealBridge", True)):
    body = u + ros2control_block(plugin, dt7) + ["</robot>"]
    open(os.path.join(xc, fn), "w", encoding="utf-8", newline="\n").write("\n".join(body) + "\n")
    print("wrote", os.path.join(xc, fn))

def arr(vals):
    return "[" + ", ".join("%.6f" % float(x) for x in vals) + "]"

y = """# ros2_control configuration for the closed-chain (similar-linkage) STEP robot.
# Joint order is the fixed eight-joint contract of wheelbipe_ros2_sim2sim; front1 is the
# hip-mounted crank that drives the PASSIVE knee through the linkage, rear1 the thigh.

/**:
  controller_manager:
    ros__parameters:
      update_rate: 500
      joint_state_broadcaster:
        type: joint_state_broadcaster/JointStateBroadcaster
      template_ros2_controller:
        type: robot_locomotion/TemplateRos2Controller

  joint_state_broadcaster:
    ros__parameters:
      update_rate: 500

  template_ros2_controller:
    ros__parameters:
      update_rate: 500
      joints:
""" + "".join("        - %s\n" % n for n in CONTRACT) + """      command_interfaces:
        - position
        - velocity
        - effort
        - kp
        - kd
      state_interfaces:
        - position
        - velocity
        - effort
      sensors:
        - imu
      joint_stiffness: %s
      joint_damping: %s
      joint_action_scale: %s
      joint_output_max: %s
      joint_output_min: %s
      default_dof_pos: %s
      joint_bias: %s
      prepare_dof_pos: %s
      prepare_kp: [60.0, 60.0, 60.0, 60.0]
      prepare_kd: [2.0, 2.0, 2.0, 2.0]
      motion_linear_x_min: %s
      motion_linear_x_max: %s
      motion_angular_z_min: %s
      motion_angular_z_max: %s
      default_command_height: 0.22
      command_height_min: 0.18
      command_height_max: 0.34
      rl_inference_frequency: 50
      lowlevel_output_mode: "effort_pd_vel"\n      # (the plant has no <actuator> block; effort arrives as qfrc_applied, so "hardware_pd_vel" would
      #  command the wheels with zero torque -- see HOWTO section 20)
      gas_spring_preload: [350.0, 350.0]
""" % (
     # ONE PLACEHOLDER PER LINE, in the order they appear in the template above.  The
     # ordering bug here once shipped a YAML whose joint_stiffness held the damping array.
     arr([CT["leg_kp"]] * 4 + [0.0] * 4),                       # joint_stiffness
     arr([CT["leg_kd"]] * 4 + [CT["wheel_kd"]] * 2 + [0.0] * 2),  # joint_damping
     arr([CT["leg_action_scale"]] * 4 + [CT["wheel_action_scale"]] * 2 + [0.0] * 2),
     arr([LEG_TORQUE] * 4 + [WHEEL_TORQUE] * 2 + [50.0] * 2),   # joint_output_max
     arr([-LEG_TORQUE] * 4 + [-WHEEL_TORQUE] * 2 + [-50.0] * 2),
     arr([0.0] * 8),                                            # default_dof_pos
     arr([0.0] * 8),                                            # joint_bias
     arr([0.0] * 4),                                            # prepare_dof_pos
     _LX[0], _LX[1],                                            # motion_linear_x min / max
     _AZ[0], _AZ[1])                                            # motion_angular_z min / max
open(os.path.join(cf, "%s.yaml" % args.prefix), "w", encoding="utf-8", newline="\n").write(y)
print("wrote config/rm_vehicle.yaml")
