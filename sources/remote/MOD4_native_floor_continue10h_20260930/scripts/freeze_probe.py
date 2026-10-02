"""Does "zero qvel+qacc every step" actually freeze the robot?

That is exactly what the bridge's spawn-hold (sim2sim/wsl/patch_spawn_hold.py) tries to do, and
docs/HOWTO.md 27.3 recorded that it did NOT work (the hips were already at -179.9 deg 115 ms
after the bridge started).  Reproduce the mechanism here, in plain MuJoCo, with zero torque on
every joint - the worst case - and see whether the freeze holds or the state still runs away.
"""
import os
import mujoco
import numpy as np
ROOT = r"D:/claude2/fangzhen"
m = mujoco.MjModel.from_xml_path(os.path.join(ROOT, "robot/out_cc/scene_cc.xml"))
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
m.opt.timestep = 0.001
nm = lambda o, i: mujoco.mj_id2name(m, o, i) or ""
# disable the base box, like mjlab's CollisionCfg(disable_other_geoms=True)
for g in range(m.ngeom):
    n2 = nm(mujoco.mjtObj.mjOBJ_GEOM, g)
    if n2 and "base" in n2 and n2.endswith("_col"):
        m.geom_conaffinity[g] = 0; m.geom_contype[g] = 0
print("base box disabled; spawn base_z=%.4f" % d.qpos[2])

AN = {nm(mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}
QA = {nm(mujoco.mjtObj.mjOBJ_JOINT, i): int(m.jnt_qposadr[i]) for i in range(m.njnt)}
VA = {nm(mujoco.mjtObj.mjOBJ_JOINT, i): int(m.jnt_dofadr[i]) for i in range(m.njnt)}


def run(mode, seconds=2.0, ctrl=False):
    mujoco.mj_resetDataKeyframe(m, d, 0)
    for g in range(m.ngeom):
        n2 = nm(mujoco.mjtObj.mjOBJ_GEOM, g)
        if n2 and "base" in n2 and n2.endswith("_col"):
            m.geom_conaffinity[g] = 0; m.geom_contype[g] = 0
    for k in range(int(seconds / m.opt.timestep)):
        if ctrl:  # what IDLE does: hold the hips at the stance with the training PD
            for jn, tgt in (("left_front1_joint", 0.222), ("left_rear1_joint", 0.097),
                            ("right_front1_joint", 0.230), ("right_rear1_joint", 0.117)):
                d.ctrl[AN[jn.replace("_joint", "_ctrl")]] = float(np.clip(
                    60.0 * (tgt - d.qpos[QA[jn]]) - 2.0 * d.qvel[VA[jn]], -40, 40))
        mujoco.mj_step1(m, d)
        if mode == "freeze":
            d.qvel[:] = 0.0
            d.qacc[:] = 0.0
        elif mode == "freeze_q":
            d.qvel[:] = 0.0
            d.qacc[:] = 0.0
            mujoco.mj_forward(m, d)
        mujoco.mj_step2(m, d)
    print("  %-9s ctrl=%-5s -> base_z=%+.4f  hips f1=%+.3f r1=%+.3f  |qvel|inf=%.2f  nefc=%d"
          % (mode, str(ctrl), d.qpos[2], d.qpos[QA["left_front1_joint"]],
             d.qpos[QA["left_rear1_joint"]], float(np.abs(d.qvel).max()), d.nefc))

for ctrl in (False, True):
    run("none", 2.0, ctrl)
    run("freeze", 2.0, ctrl)
print("\nexpected: 'none' drifts/flips, 'freeze' holds base_z=0.0750 exactly.")
