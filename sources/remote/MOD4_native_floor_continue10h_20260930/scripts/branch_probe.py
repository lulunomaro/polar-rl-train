"""After a PD settle, is the closed chain still CLOSED, and where did it go?

docs/HOWTO.md 33.2(b): commanding the trained hip stance for 1.5 s in native MuJoCo lands at
base_z 0.261 / pitch -46.5 deg with hips at [0.403, -0.222] instead of [0.222, 0.097], while the
same command in the training sim gives base_z 0.0887.  Two possible explanations, and they need
completely different fixes:

  (i)  the equality constraints are being VIOLATED (solver failure) -> fix the solver/contact
       configuration, nothing to do with branches;
  (ii) the constraints are satisfied but the chain found the OTHER assembly branch -> the fix is
       to initialise (and keep) the passive joints on the CAD branch.

This prints, for the settled state: every joint angle vs its declared range, and the actual
geometric gap of each `connect` constraint (distance between the two anchor points it ties).
"""
import mujoco
import numpy as np
import os

ROOT = r"D:/claude2/fangzhen"
STANCE = {"left_front1_joint": 0.222, "left_rear1_joint": 0.097,
          "right_front1_joint": 0.230, "right_rear1_joint": 0.117}
m = mujoco.MjModel.from_xml_path(os.path.join(ROOT, "robot/out_cc/scene_cc.xml"))
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
nm = lambda o, i: mujoco.mj_id2name(m, o, i) or ""
JN = {nm(mujoco.mjtObj.mjOBJ_JOINT, i): i for i in range(m.njnt)}
QA = {k: int(m.jnt_qposadr[v]) for k, v in JN.items()}
VA = {k: int(m.jnt_dofadr[v]) for k, v in JN.items()}
AN = {nm(mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}
# cross the two things the CPU parity harness does differently from the plant defaults
DT = float(os.environ.get("BP_DT", "0.001"))
NOBASE = os.environ.get("BP_NOBASE", "0") == "1"
CAPS1 = os.environ.get("BP_CAPS1", "0") == "1"
m.opt.timestep = DT
if NOBASE:
    for g in range(m.ngeom):
        if "base" in nm(mujoco.mjtObj.mjOBJ_GEOM, g) and nm(mujoco.mjtObj.mjOBJ_GEOM, g).endswith("_col"):
            m.geom_conaffinity[g] = 0; m.geom_contype[g] = 0
if CAPS1:
    for g in range(m.ngeom):
        n2 = nm(mujoco.mjtObj.mjOBJ_GEOM, g)
        if n2.endswith("_col") and "wheel" not in n2 and "base" not in n2:
            m.geom_condim[g] = 1
        elif "wheel" in n2 and n2.endswith("_col"):
            m.geom_condim[g] = 6; m.geom_friction[g] = (1.2, 0.02, 0.002); m.geom_priority[g] = 1
print("config: dt=%.4f disable_base_box=%s capsule_condim1=%s" % (DT, NOBASE, CAPS1))
print("at spawn: base_z=%.4f  nefc=%d" % (d.qpos[2], d.nefc))


def step_hold(sec, kp=60.0, kd=2.0, wk=0.6):
    for _ in range(int(sec / m.opt.timestep)):
        for jn, tgt in STANCE.items():
            d.ctrl[AN[jn.replace("_joint", "_ctrl")]] = float(np.clip(
                kp * (tgt - d.qpos[QA[jn]]) - kd * d.qvel[VA[jn]], -40, 40))
        for jn in ("left_wheel_joint", "right_wheel_joint"):
            d.ctrl[AN[jn.replace("_joint", "_ctrl")]] = float(np.clip(
                -wk * d.qvel[VA[jn]], -5.5, 5.5))
        mujoco.mj_step(m, d)


def eq_gaps():
    out = []
    for i in range(m.neq):
        if int(m.eq_type[i]) != int(mujoco.mjtEq.mjEQ_CONNECT):
            out.append((nm(mujoco.mjtObj.mjOBJ_EQUALITY, i), int(m.eq_type[i]), None)); continue
        b1 = int(m.eq_obj1id[i]); b2 = int(m.eq_obj2id[i])
        # eq_data = [anchor1(3), anchor2(3), ...] in the two body frames
        a1 = np.asarray(m.eq_data[i][0:3], float); a2 = np.asarray(m.eq_data[i][3:6], float)
        R1 = np.asarray(d.xmat[b1], float).reshape(3, 3); R2 = np.asarray(d.xmat[b2], float).reshape(3, 3)
        p1 = np.asarray(d.xpos[b1], float) + R1 @ a1
        p2 = np.asarray(d.xpos[b2], float) + R2 @ a2
        out.append((nm(mujoco.mjtObj.mjOBJ_EQUALITY, i), 3, float(np.linalg.norm(p1 - p2))))
    return out


print("\n--- 1) hold the stance for 1.5 s, then inspect")
step_hold(1.5)
print("RESULT base_z=%.4f  nefc=%d  |qvel|inf=%.2f  hips f1=%+.3f r1=%+.3f" %
      (d.qpos[2], d.nefc, float(np.abs(d.qvel).max()),
       d.qpos[QA["left_front1_joint"]], d.qpos[QA["left_rear1_joint"]]))
for name, t, gap in eq_gaps():
    print("   %-24s type=%d  gap=%s" % (name, t, "-" if gap is None else "%.5f m" % gap))
import sys
if os.environ.get("BP_QUIET") == "1":
    sys.exit(0)
print("\n   joint                     q        range            limited  status")
for jn, j in JN.items():
    q = float(d.qpos[QA[jn]])
    lo, hi = m.jnt_range[j]
    lim = bool(m.jnt_limited[j])
    st = ""
    if lim and (q <= lo + 1e-4 or q >= hi - 1e-4):
        st = "AT LIMIT"
    elif jn in STANCE:
        st = "cmd %+.3f  err %+.3f" % (STANCE[jn], q - STANCE[jn])
    print("   %-24s %+8.3f  [%+.2f,%+.2f]  %-5s  %s" % (jn, q, lo, hi, str(lim), st))
