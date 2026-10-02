"""Does the deployed plant, released from qpos0 with NO actuation, snap to the other
assembly branch of the similar-link four-bar and fall through its own stance?

That is what the ROS2 sim shows in IDLE (base_z -0.169 m, rear1 -2.851 rad) because
state_idle applies zero gains.  If it reproduces here, the deployment instability is not an
actuator-law problem at all: the policy is simply handed a collapsed robot."""
import os, numpy as np, mujoco
ROOT = r"D:/claude2/fangzhen"
for tag, xml in (("DEPLOYED", os.path.join(ROOT, "sim2sim_cc/rm_vehicle/mjcf/scene.xml")),
                 ("TRAINING", os.path.join(ROOT, "robot/out_cc/scene_cc.xml"))):
    if not os.path.exists(xml):
        print(tag, "missing", xml); continue
    m = mujoco.MjModel.from_xml_path(xml)
    d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, 0) if m.nkey else mujoco.mj_resetData(m, d)
    mujoco.mj_forward(m, d)
    leg = ["left_rear1_joint", "left_front1_joint", "left_rear2_joint", "left_front3_joint"]
    a = [m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)] for n in leg]
    def snap():
        return " ".join("%s=%+7.3f" % (n[:13], d.qpos[x]) for n, x in zip(leg, a))
    print("\n=== %s : qpos0 ===" % tag)
    print("   base_z %+.4f  %s" % (d.qpos[2], snap()))
    print("   equality gap %.4f mm" % max(
        1000 * np.linalg.norm(
            (d.xpos[int(m.eq_obj1id[e])] + d.xmat[int(m.eq_obj1id[e])].reshape(3, 3) @ m.eq_data[e][0:3]) -
            (d.xpos[int(m.eq_obj2id[e])] + d.xmat[int(m.eq_obj2id[e])].reshape(3, 3) @ m.eq_data[e][3:6]))
        for e in range(m.neq)))
    # PASSIVE: no actuation at all, exactly what state_idle.cpp delivers (kp=kd=0, effort=0)
    for _ in range(int(3.0 / m.opt.timestep)):
        d.qfrc_applied[:] = 0.0
        for i in range(m.nu):
            d.ctrl[i] = 0.0
        mujoco.mj_step(m, d)
    gap = max(1000 * np.linalg.norm(
        (d.xpos[int(m.eq_obj1id[e])] + d.xmat[int(m.eq_obj1id[e])].reshape(3, 3) @ m.eq_data[e][0:3]) -
        (d.xpos[int(m.eq_obj2id[e])] + d.xmat[int(m.eq_obj2id[e])].reshape(3, 3) @ m.eq_data[e][3:6]))
        for e in range(m.neq))
    print("   after 3 s UNACTUATED: base_z %+.4f  %s  gap %.3f mm  %s" %
          (d.qpos[2], snap(), gap,
           "**BRANCH FLIP + COLLAPSE**" if abs(d.qpos[2] - 0.075) > 0.05 else "held"))
    # ACTIVE: hold qpos0 with the training leg PD, as mjlab does from step 1
    m2 = mujoco.MjModel.from_xml_path(xml); d2 = mujoco.MjData(m2)
    mujoco.mj_resetDataKeyframe(m2, d2, 0) if m2.nkey else mujoco.mj_resetData(m2, d2)
    q0 = d2.qpos.copy()
    dof = [m2.jnt_dofadr[m2.jnt_qposadr[mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_JOINT, n)]][:1]
           for n in leg[:2]]
    dof = [m2.jnt_dofadr[mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_JOINT, n)] for n in leg[:2]]
    for _ in range(int(3.0 / m2.opt.timestep)):
        d2.qfrc_applied[:] = 0.0
        for k in (0, 1):
            d2.qfrc_applied[dof[k]] = 60.0 * (q0[a[k]] - d2.qpos[a[k]]) - 2.0 * d2.qvel[dof[k]]
        mujoco.mj_step(m2, d2)
    print("   after 3 s WITH leg PD: base_z %+.4f  %s  %s" %
          (d2.qpos[2], " ".join("%s=%+7.3f" % (n[:13], d2.qpos[x]) for n, x in zip(leg, a)),
           "stable" if abs(d2.qpos[2] - 0.075) < 0.05 else "collapsed"))