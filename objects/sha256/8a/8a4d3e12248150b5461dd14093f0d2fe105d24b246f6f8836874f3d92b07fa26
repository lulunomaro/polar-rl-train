"""Is the DEPLOYMENT plant's initial condition even standable?

The sim2sim explosion has been blamed on the policy handover, but the deployment sim spends
14+ s in IDLE before anything else, and my probe showed the robot already at 39-66 deg of pitch
with the wheels commanding 17 rad/s and nothing moving - the signature of unloaded wheels.
This prints the deploy plant's spawn geometry and then lets it sit under the SAME control law the
framework uses (leg PD to the trained stance, wheels held at zero velocity), with no ROS at all.
"""
import os, sys
import mujoco
import numpy as np

ROOT = r"D:/claude2/fangzhen"
FILES = {"training (mjlab)": os.path.join(ROOT, "robot/out_cc/scene_cc.xml"),
         "deployment (sim2sim)": os.path.join(ROOT, "sim2sim_cc/rm_vehicle/mjcf/scene.xml"),
         "deployment field": os.path.join(ROOT, "sim2sim_cc/rm_vehicle/mjcf/scene_field.xml"),
         # control-path A/B: the SAME qfrc_applied law on the training plant tells us whether a
         # difference below is a plant difference or an artefact of how the torque is injected.
         "training plant + qfrc": os.path.join(ROOT, "robot/out_cc/scene_cc.xml")}
STANCE = {"left_front1_joint": 0.2222, "left_rear1_joint": 0.0965,
          "right_front1_joint": 0.2304, "right_rear1_joint": 0.1167}
for tag, path in FILES.items():
    if not os.path.exists(path):
        print("%-24s MISSING %s" % (tag, path)); continue
    m = mujoco.MjModel.from_xml_path(path)
    d = mujoco.MjData(m)
    if m.nkey:
        mujoco.mj_resetDataKeyframe(m, d, 0)
    else:
        mujoco.mj_resetData(m, d)
    mujoco.mj_forward(m, d)
    nm = lambda t, i: mujoco.mj_id2name(m, t, i) or ""
    wheels = [i for i in range(m.ngeom) if "wheel_col" in nm(mujoco.mjtObj.mjOBJ_GEOM, i)]
    zs = [float(d.geom_xpos[i, 2] - m.geom_size[i][0]) for i in wheels]
    floors = [i for i in range(m.ngeom) if nm(mujoco.mjtObj.mjOBJ_GEOM, i) in ("floor", "terrain")]
    print("\n== %s" % tag)
    print("   nq=%d nu=%d neq=%d nkey=%d dt=%.4f" % (m.nq, m.nu, m.neq, m.nkey, m.opt.timestep))
    print("   wheel bottoms z = %s   floor z = %s"
          % (np.round(zs, 4), [round(float(d.geom_xpos[i, 2]), 3) for i in floors]))
    print("   base z = %.4f   subtree COM z = %.4f (x %.4f y %.4f)"
          % (d.qpos[2], d.subtree_com[1][2], d.subtree_com[1][0], d.subtree_com[1][1]))
    print("   geoms touching the floor at spawn:",
          [nm(mujoco.mjtObj.mjOBJ_GEOM, c.geom1) for c in [d.contact[i] for i in range(d.ncon)]][:8])
    # now hold the trained stance with the framework's own law for 3 s
    J = {nm(mujoco.mjtObj.mjOBJ_JOINT, i): i for i in range(m.njnt)}
    A = {nm(mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}
    leg_ctrl = [n for n in A if "front1" in n or "rear1" in n]
    wh_ctrl = [n for n in A if "wheel" in n]
    has_act = bool(leg_ctrl) and os.environ.get("FORCE_QFRC", "0") != "1"
    n = int(3.0 / m.opt.timestep)
    for k in range(n):
        if has_act:
            for cn in leg_ctrl:
                jn = cn.replace("_ctrl", "_joint")
                ja, va = int(m.jnt_qposadr[J[jn]]), int(m.jnt_dofadr[J[jn]])
                tau = 60.0 * (STANCE.get(jn, 0.0) - d.qpos[ja]) - 2.0 * d.qvel[va]
                d.ctrl[A[cn]] = float(np.clip(tau, -40, 40))
            for cn in wh_ctrl:
                va = int(m.jnt_dofadr[J[cn.replace("_ctrl", "_joint")]])
                d.ctrl[A[cn]] = float(np.clip(1.5 * (0.0 - d.qvel[va]), -5.5, 5.5))
        else:
            for i in range(m.njnt):
                jn = nm(mujoco.mjtObj.mjOBJ_JOINT, i)
                if jn in STANCE or jn.endswith("front1_joint") or jn.endswith("rear1_joint"):
                    ja, va = int(m.jnt_qposadr[i]), int(m.jnt_dofadr[i])
                    tgt = STANCE.get(jn, 0.0)
                    tau = 60.0 * (tgt - d.qpos[ja]) - 2.0 * d.qvel[va]
                    q = np.zeros((m.nv, 1)); q[va, 0] = np.clip(tau, -40, 40)
                    mujoco.mj_addForceList if False else None
                    d.qfrc_applied[va] = np.clip(tau, -40, 40)
                elif "wheel" in jn:
                    d.qfrc_applied[int(m.jnt_dofadr[i])] = np.clip(
                        -1.5 * d.qvel[int(m.jnt_dofadr[i])], -5.5, 5.5)
        mujoco.mj_step(m, d)
        if has_act:
            pass
        if k % int(0.5 / m.opt.timestep) == int(0.5 / m.opt.timestep) - 1:
            R2 = np.asarray(d.xmat[1]).reshape(3, 3)
            g2 = R2.T @ np.array([0.0, 0.0, -1.0])
            angs = {jn: round(float(d.qpos[int(m.jnt_qposadr[J[jn]])]), 3)
                    for jn in J if jn.endswith(("front1_joint", "rear1_joint"))}
            print("      t=%.1f base_z=%.4f pitch=%+6.1f legs=%s"
                  % ((k + 1) * m.opt.timestep, d.qpos[2],
                     float(np.degrees(np.arcsin(np.clip(g2[0], -1, 1)))), angs))
    g = np.zeros(3)
    R = np.asarray(d.xmat[1]).reshape(3, 3)
    g = R.T @ np.array([0.0, 0.0, -1.0])
    pitch = np.degrees(np.arcsin(np.clip(g[0], -1, 1)))
    wv = []
    for i in range(m.njnt):
        jn = nm(mujoco.mjtObj.mjOBJ_JOINT, i)
        if "wheel" in jn:
            wv.append(round(float(d.qvel[int(m.jnt_dofadr[i])]), 2))
    R = np.asarray(d.xmat[1]).reshape(3, 3)
    g = R.T @ np.array([0.0, 0.0, -1.0])
    pitch = float(np.degrees(np.arcsin(np.clip(g[0], -1, 1))))
    touching = sorted({nm(mujoco.mjtObj.mjOBJ_GEOM, d.contact[i].geom1)
                       for i in range(d.ncon)} |
                      {nm(mujoco.mjtObj.mjOBJ_GEOM, d.contact[i].geom2)
                       for i in range(d.ncon)})
    print("   after 3 s of the framework IDLE law: base_z=%.4f pitch=%+.1f deg "
          "wheel_vel=%s  contacts=%s"
          % (d.qpos[2], pitch, wv, [t for t in touching if t]))
