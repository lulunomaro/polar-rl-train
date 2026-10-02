"""How tall a step / barricade can THIS robot actually climb?  (measured on the validated plant)

The 2026 map, measured out of RMUC2026_V2.0.0.stp, contains steps up to 0.22 m and obstacles up
to 0.416 m.  Spawning a learning agent in front of geometry its mechanism can never surmount is
not "training on the map" - it wastes the environments on that row and then the terrain
curriculum demotes everyone (v14's Curriculum/terrain_levels/mean sitting at 0.067 is that
symptom).  So measure the machine's own vertical authority and use it as the curriculum cap,
and state plainly which map features this chassis cannot climb.

Method: hold the chassis rigid at a fixed pose (re-imposing root position + zeroing root
velocity every step), drive the two hip-axis motors of one leg across their commanded range,
let the passive four-bar joints settle through the validated equality constraints, and read the
wheel's height relative to the chassis.  The stroke is the answer.
"""
import os, sys
import numpy as np
import mujoco

ROOT = r"D:/claude2/fangzhen"
m = mujoco.MjModel.from_xml_path(os.path.join(ROOT, "robot/out_cc/scene_cc.xml"))
d = mujoco.MjData(m)
nm = lambda o, i: mujoco.mj_id2name(m, o, i)
JID = {nm(mujoco.mjtObj.mjOBJ_JOINT, i): i for i in range(m.njnt)}
QA = {k: int(m.jnt_qposadr[v]) for k, v in JID.items()}
VA = {k: int(m.jnt_dofadr[v]) for k, v in JID.items()}
AID = {nm(mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}
WHEEL_G = "left_wheel_col"
R = float(m.geom_size[int(mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, WHEEL_G))][0])
BASE_Z = 0.35


def wheel_below_base(f1, r1, seconds=1.2):
    """Left leg: hip targets (front1, rear1) -> wheel bottom relative to the chassis origin."""
    d.qpos[:] = 0.0
    d.qvel[:] = 0.0
    d.qpos[0:3] = (0.0, 0.0, BASE_Z)
    d.qpos[3] = 1.0
    n = int(seconds / m.opt.timestep)
    for k in range(n):
        for jn, tgt in (("left_front1_joint", f1), ("left_rear1_joint", r1),
                        ("right_front1_joint", 0.0), ("right_rear1_joint", 0.0)):
            cn = jn.replace("_joint", "_ctrl")
            d.ctrl[AID[cn]] = float(np.clip(300.0 * (tgt - d.qpos[QA[jn]])
                                            - 10.0 * d.qvel[VA[jn]], -60, 60))
        mujoco.mj_step(m, d)
        d.qpos[0:3] = (0.0, 0.0, BASE_Z)      # weld the chassis back in place
        d.qpos[3:7] = (1.0, 0.0, 0.0, 0.0)
        d.qvel[0:6] = 0.0
    g = int(mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, WHEEL_G))
    return float(BASE_Z - (d.geom_xpos[g, 2] - R))      # wheel BOTTOM below the chassis origin


grid = np.arange(-0.55, 0.56, 0.05)
vals = {}
for f1 in grid:
    for r1 in grid:
        try:
            vals[(round(f1, 2), round(r1, 2))] = wheel_below_base(f1, r1, 0.6)
        except Exception:
            pass
v = np.array(list(vals.values()))
print("left-leg vertical stroke over the commanded hip range (+-0.55 rad):")
print("   wheel bottom below chassis origin: %.3f .. %.3f m   (n=%d poses)"
      % (v.min(), v.max(), len(v)))
print("   => leg stroke (max - min) = %.3f m" % (v.max() - v.min()))
best = max(vals, key=lambda k: vals[k]); worst = min(vals, key=lambda k: vals[k])
print("   deepest reach  front1=%+.2f rear1=%+.2f -> %.3f m" % (best[0], best[1], vals[best]))
print("   shortest reach front1=%+.2f rear1=%+.2f -> %.3f m" % (worst[0], worst[1], vals[worst]))
# the nominal (CAD) pose and the trained stance, for reference
print("   nominal (0,0)          -> %.3f m" % wheel_below_base(0.0, 0.0, 1.0))
print("   trained stance .22/.10 -> %.3f m" % wheel_below_base(0.222, 0.097, 1.0))
print("""
Interpretation for the terrain curriculum: climbing a step of height h needs one wheel to be
lifted to h + wheel_radius while the other wheel still carries the robot, so h_max is bounded by
the leg stroke above (and in practice by chassis attitude and by the fact that the chassis box
must not dig in).  Anything in the map taller than that is a feature this chassis can only
approach at an angle or bypass; the curriculum should stop at the capability, not at the CAD.""")
