"""Which freeze actually freezes?

scripts/freeze_probe.py showed that zeroing qvel/qacc between mj_step1 and mj_step2 does NOT hold
the state (|qvel| reached 9923 rad/s and the base still moved) - which is exactly why the bridge
spawn-hold in docs/HOWTO.md 27.3 failed.  Try the alternatives and keep only what provably works.
"""
import os
import mujoco
import numpy as np
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
m.opt.timestep = 0.001
nm = lambda o, i: mujoco.mj_id2name(m, o, i) or ""
for g in range(m.ngeom):
    n2 = nm(mujoco.mjtObj.mjOBJ_GEOM, g)
    if n2 and "base" in n2 and n2.endswith("_col"):
        m.geom_conaffinity[g] = 0; m.geom_contype[g] = 0
Q0 = d.qpos.copy(); V0 = d.qvel.copy()
QA = {nm(mujoco.mjtObj.mjOBJ_JOINT, i): int(m.jnt_qposadr[i]) for i in range(m.njnt)}


def run(mode, seconds=2.0):
    mujoco.mj_resetDataKeyframe(m, d, 0)
    for g in range(m.ngeom):
        n2 = nm(mujoco.mjtObj.mjOBJ_GEOM, g)
        if n2 and "base" in n2 and n2.endswith("_col"):
            m.geom_conaffinity[g] = 0; m.geom_contype[g] = 0
    for k in range(int(seconds / m.opt.timestep)):
        if mode == "no_step":
            mujoco.mj_forward(m, d)
            d.time += m.opt.timestep          # keep the ROS sim clock alive, do not integrate
        elif mode == "restore":
            mujoco.mj_step(m, d)
            d.qpos[:] = Q0
            d.qvel[:] = V0
            d.qacc[:] = 0.0
            d.time += 0.0                      # time follows the integrator; restore state only
        else:
            mujoco.mj_step(m, d)
    print("  %-8s -> base_z=%+.5f  hips f1=%+.4f r1=%+.4f  |q|inf=%.4f  |qvel|inf=%.2f"
          % (mode, d.qpos[2], d.qpos[QA["left_front1_joint"]],
             d.qpos[QA["left_rear1_joint"]], float(np.abs(d.qpos).max()),
             float(np.abs(d.qvel).max())))


run("free", 2.0)
run("no_step", 2.0)
run("restore", 2.0)
print("\nexpected: no_step and restore keep base_z=0.07500 exactly; free does not.")
