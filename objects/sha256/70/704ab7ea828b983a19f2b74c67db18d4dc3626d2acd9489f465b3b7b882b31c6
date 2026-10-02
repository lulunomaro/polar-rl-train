"""Whole-body dynamical invariants of the plant, compared with SCUT's own wheelbipeV14_2.

Why this exists: build_cc computed the chassis inertia with a broken anchor -- every part's
lever arm was subtracted from itself -- so the base COM sat exactly at the wheel-axle origin
and Izz was 0.0435 kg*m^2, i.e. a 20 kg, 0.71 m machine with the yaw inertia of a dinner
plate.  That silently broke BOTH skills the user asked about: 小陀螺 spins up ~14x too
easily, and a robot whose COM is AT its axle has no balance problem to learn at all.

In the nominal pose this measures, for our plant and for the reference:
  total mass, COM height above the wheel-axle plane, the composite inertia about the COM,
  the pitch pendulum frequency sqrt(m g h / I_axle), and the yaw impulse a spin needs.
Agreement with an independent same-class machine is the acceptance test for the fix.
"""
import argparse, math, os
import mujoco
import numpy as np

ROOT = r"D:/claude2/fangzhen"
ap = argparse.ArgumentParser()
ap.add_argument("--ours", default=os.path.join(ROOT, "robot/out_cc/scene_cc.xml"))
ap.add_argument("--ref", default=os.path.join(
    ROOT, "refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/"
          "wheelbipeV14_2/mjcf/wheelbipeV14_2.xml"))
a = ap.parse_args()


def _hat(v):
    return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def q2mat(q):
    R = np.zeros(9)
    mujoco.mju_quat2Mat(R, np.asarray(q, float))
    return R.reshape(3, 3)


def body_world_inertia(m, d, b):
    """Full 3x3 inertia of body b about the WORLD origin, in world axes.

    MuJoCo compiles every <inertial> into body_inertial_pos/quat (the inertial frame inside
    the body frame) + body_inertia (DIAGONAL there), so the tensor has to be rebuilt from
    those; data.cinert's 10 numbers are not in the order its docstring suggests."""
    idiag = np.asarray(m.body_inertia[b], float)
    Ri = q2mat(m.body_iquat[b])
    Ib = Ri @ np.diag(idiag) @ Ri.T
    Rw = np.asarray(d.xmat[b]).reshape(3, 3)
    p = np.asarray(d.xipos[b], float)
    mm = float(m.body_mass[b])
    Iw = Rw @ Ib @ Rw.T
    return Iw + mm * (_hat(p) @ _hat(p).T), p, mm      # parallel-axis to the world origin


def analyse(path, label, key_index=0):
    m = mujoco.MjModel.from_xml_path(path)
    d = mujoco.MjData(m)
    if m.nkey:
        mujoco.mj_resetDataKeyframe(m, d, min(key_index, m.nkey - 1))
    else:
        mujoco.mj_resetData(m, d)
    mujoco.mj_forward(m, d)
    name = lambda t, i: (mujoco.mj_id2name(m, t, i) or "")

    cyl = [i for i in range(m.ngeom)
           if "wheel" in name(mujoco.mjtObj.mjOBJ_GEOM, i).lower()
           and int(m.geom_type[i]) == int(mujoco.mjtGeom.mjGEOM_CYLINDER)]
    assert cyl, "no wheel cylinders found in " + path
    ground = min(float(d.geom_xpos[i, 2] - m.geom_size[i][0]) for i in cyl)
    axle_z = float(np.mean([d.geom_xpos[i, 2] for i in cyl]))
    pts = [np.asarray(d.geom_xpos[i], float) for i in cyl]
    axle = np.mean(pts, axis=0)
    half_track = 0.5 * abs(pts[0][1] - pts[1][1]) if len(pts) > 1 else 0.0
    r_wheel = float(np.mean([m.geom_size[i][0] for i in cyl]))

    M = 0.0
    mom = np.zeros(3)
    O = np.zeros((3, 3))
    for b in range(m.nbody):
        Iw, p, mm = body_world_inertia(m, d, b)
        if mm <= 0:
            continue
        M += mm
        mom += mm * p
        O += Iw
    com = mom / M
    I = O - M * (_hat(com) @ _hat(com).T)          # about the COM, world axes
    e = com - axle
    Ipitch = float(I[1, 1] + M * (e[0] ** 2 + e[2] ** 2))
    Iroll = float(I[0, 0] + M * (e[1] ** 2 + e[2] ** 2))
    Izz = float(I[2, 2] + M * (e[0] ** 2 + e[1] ** 2))
    h = com[2] - axle_z
    print("\n== %s ==" % label)
    print("  total mass                 %6.2f kg" % M)
    print("  wheel radius / half track   %.3f m / %.3f m  -> %.2f rad/s wheel per rad/s yaw"
          % (r_wheel, half_track, half_track / r_wheel))
    print("  COM above the axle plane   %+6.3f m     (COM %s)" % (h, np.round(com, 3)))
    print("  COM offset from the axle mid-point: x %+.4f  y %+.4f m  (spin wobble)"
          % (com[0] - axle[0], com[1] - axle[1]))
    print("  I about COM   x / y / z     %s kg*m^2" % np.round([I[0, 0], I[1, 1], I[2, 2]], 4))
    print("  I about axle: pitch %6.3f  roll %6.3f  yaw %6.3f kg*m^2" % (Ipitch, Iroll, Izz))
    if h > 1e-4:
        print("  pitch pendulum sqrt(mgh/I) = %5.2f rad/s -> e-folding fall time %5.2f s"
              % (math.sqrt(M * 9.81 * h / Ipitch), math.sqrt(Ipitch / (M * 9.81 * h))))
    else:
        print("  !! COM is at/below the axle: the robot has NO balance problem to solve")
    for wz in (6.0, 10.0, 14.0):
        tau_max = 2.0 * 5.5 / r_wheel * half_track        # differential wheels, 5.5 Nm each
        print("  spin %4.1f rad/s needs wheel %+5.1f rad/s, %.2f N*m*s impulse, "
              ">=%.2f s to reach at full torque"
              % (wz, wz * half_track / r_wheel, Izz * wz, Izz * wz / tau_max))
    return dict(label=label, mass=M, h=h, Izz=Izz, Ipitch=Ipitch, Iroll=Iroll,
                half_track=half_track, r=r_wheel, com=np.round(com, 4).tolist())


import json, sys
res = [analyse(a.ours, "OURS  robot/out_cc/scene_cc.xml (post-fix)")]
try:
    res.append(analyse(a.ref, "REF   SCUT wheelbipeV14_2 (same class)"))
except Exception as e:
    print("reference failed:", type(e).__name__, str(e)[:120])
old = os.path.join(ROOT, "docs/audit/pre_baseinertia/scene_cc.xml")
json.dump(res, open(os.path.join(ROOT, "docs/audit/plant_invariants.json"), "w"), indent=1)
print("\nwrote docs/audit/plant_invariants.json")

