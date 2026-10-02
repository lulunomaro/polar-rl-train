# -*- coding: utf-8 -*-
"""Does the solver iteration budget buy fidelity?  CPU-only, no GPU contention.

The MJCF asks MuJoCo for Newton with iterations=100, ls_iterations=50, tolerance=1e-8 -
far more solver work than a typical legged-robot config, and solver time dominates the
per-step cost of a model with 6 equality constraints.  Measure the jump result AND the
closed-chain gap under cheaper settings, so speed can be bought with numbers in hand.
"""
import time
import numpy as np
import mujoco

XML = r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml"
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
G = 9.81

ref = mujoco.MjModel.from_xml_path(XML)
rd = mujoco.MjData(ref)
JID = {n: mujoco.mj_name2id(ref, mujoco.mjtObj.mjOBJ_JOINT, n) for n in LEG + WHL}
qa = {n: ref.jnt_qposadr[JID[n]] for n in LEG + WHL}
va = {n: ref.jnt_dofadr[JID[n]] for n in LEG + WHL}
mass = float(sum(ref.body_mass))

EQ = []
for e in range(ref.neq):
  if ref.eq_type[e] == mujoco.mjtEq.mjEQ_CONNECT:
    dat = np.asarray(ref.eq_data[e])
    # <connect> with a single anchor: eq_data[0:3] = anchor point in body1 frame,
    # enforced to coincide with body2 s origin.
    EQ.append((int(ref.eq_obj1id[e]), int(ref.eq_obj2id[e]), dat[0:3], dat[3:6]))
print("mass=%.2f kg, connect constraints=%d" % (mass, len(EQ)))


def gap_mm(d):
  w = 0.0
  for b1, b2, a1, a2 in EQ:
    p1 = d.xpos[b1] + d.xmat[b1].reshape(3, 3) @ a1
    p2 = d.xpos[b2] + d.xmat[b2].reshape(3, 3) @ a2
    w = max(w, float(np.linalg.norm(p1 - p2)))
  return w * 1000.0


def trial(it, ls, tol, dt, pose, kp=60.0, kd=2.0, eff=40.0,
          t_settle=1.0, t_crouch=0.9, t_after=1.2):
  m = mujoco.MjModel.from_xml_path(XML)
  d = mujoco.MjData(m)
  m.opt.iterations, m.opt.ls_iterations, m.opt.tolerance, m.opt.timestep = it, ls, tol, dt
  for n in LEG:
    m.dof_armature[va[n]] = 0.0158
    m.dof_frictionloss[va[n]] = 1.5 if "front" in n else 0.0
  mujoco.mj_resetDataKeyframe(m, d, 0)
  d.qfrc_applied[:] = 0
  tgt = {"front": 0.0, "rear": 0.0}
  cmd = {n: 0.0 for n in LEG}

  def step(k):
    for _ in range(k):
      for nm in LEG:
        key = "rear" if "rear" in nm else "front"
        cmd[nm] = float(np.clip(kp * (tgt[key] - d.qpos[qa[nm]]) - kd * d.qvel[va[nm]], -eff, eff))
      for nm in LEG:
        d.qfrc_applied[va[nm]] = cmd[nm]
      for nm in WHL:
        d.qfrc_applied[va[nm]] = float(np.clip(1.5 * (0.0 - d.qvel[va[nm]]), -5.5, 5.5))
      mujoco.mj_step(m, d)

  t0 = time.perf_counter()
  step(int(t_settle / dt)); z0 = float(d.qpos[2]); g0 = gap_mm(d)
  tgt.update(front=pose[0], rear=pose[2])
  step(int(t_crouch / dt)); zc = float(d.qpos[2]); g1 = gap_mm(d)
  tgt.update(front=pose[1], rear=pose[3])
  vz = 0.0; apex = zc; g2 = 0.0
  for _ in range(int(t_after / dt)):
    step(1)
    vz = max(vz, float(d.qvel[2])); apex = max(apex, float(d.qpos[2])); g2 = max(g2, gap_mm(d))
  el = time.perf_counter() - t0
  ns = int((t_settle + t_crouch + t_after) / dt)
  return dict(vz=vz, h=vz * vz / (2 * G) * 100.0, rise=(apex - z0) * 100.0,
              crouch=(z0 - zc) * 100.0, g_settle=g0, g_crouch=g1, g_max=g2, kstep=ns / el / 1000.0)


POSES = [(-0.6, 1.05, 0.5, -0.5), (-0.85, 1.35, 0.7, -0.7)]
CFGS = [
  ("current    it=100 ls=50  tol=1e-8  dt=2ms", 100, 50, 1e-8, 0.002),
  ("mjlab-ish  it=30  ls=20  tol=1e-6  dt=2ms", 30, 20, 1e-6, 0.002),
  ("cheap      it=10  ls=10  tol=1e-4  dt=2ms", 10, 10, 1e-4, 0.002),
  ("very tight it=200 ls=100 tol=1e-10 dt=2ms", 200, 100, 1e-10, 0.002),
  ("dt=1ms     it=30  ls=20  tol=1e-6  dt=1ms", 30, 20, 1e-6, 0.001),
  ("dt=4ms     it=30  ls=20  tol=1e-6  dt=4ms", 30, 20, 1e-6, 0.004),
]
print("\n%-43s %5s %6s %6s %6s %9s %9s %7s" %
      ("solver config", "vz", "h_cm", "rise", "crouch", "worst-gap", "settle-gap", "kstep/s"))
for tag, it, ls, tol, dt in CFGS:
  rs = [trial(it, ls, tol, dt, p) for p in POSES]
  b = max(rs, key=lambda r: r["h"])
  print("%-43s %5.2f %6.1f %6.1f %6.1f %7.4fmm %7.4fmm %7.1f" %
        (tag, b["vz"], b["h"], b["rise"], b["crouch"], b["g_max"], b["g_settle"],
         sum(r["kstep"] for r in rs) / len(rs)))
  print("     per-pose vz = %s" % ["%.2f" % r["vz"] for r in rs])
