"""Does the DEPLOYMENT plant explode with zero torque?  (the export's own initialisation)

The bridge logged hips at -179.9 deg with velocities of 1865 rad/s 0.115 s after it started and
before any controller was loaded, i.e. the deployment model destroys itself during its first
hundred physics steps.  Step it with zero torque and watch.
"""
import mujoco
import numpy as np
ROOT = r"D:/claude2/fangzhen"
for tag, path in (("deploy scene", ROOT + r"/sim2sim_cc/rm_vehicle/mjcf/scene.xml"),
                  ("deploy robot only", ROOT + r"/sim2sim_cc/rm_vehicle/mjcf/rm_vehicle.xml"),
                  ("training scene", ROOT + r"/robot/out_cc/scene_cc.xml")):
    m = mujoco.MjModel.from_xml_path(path)
    d = mujoco.MjData(m)
    if m.nkey:
        mujoco.mj_resetDataKeyframe(m, d, 0)
    else:
        mujoco.mj_resetData(m, d)
    mujoco.mj_forward(m, d)
    gaps = []
    print("\n== %s   qpos0 base %s   neq=%d" % (tag, np.round(d.qpos[:3], 4), m.neq))
    for i in range(m.neq):
        print("     eq type=%d obj1=%s obj2=%s data=%s"
              % (m.eq_type[i],
                 mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, int(m.eq_obj1id[i])),
                 mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, int(m.eq_obj2id[i])),
                 np.round(m.eq_data[i], 4)))
    for k in range(400):
        mujoco.mj_step(m, d)
        if k % 80 == 79:
            print("   t=%.3f base_z=%+.4f  |qvel|inf=%9.2f  hips %s"
                  % (d.time, d.qpos[2], float(np.abs(d.qvel).max()),
                     np.round([d.qpos[int(m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)])]
                               for n in ("left_front1_joint", "left_rear1_joint")], 3)))
