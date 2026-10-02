"""Quantify WHY the closed-chain robot cannot jump high: is it the *motor settings*?

  A) static torque -> vertical ground-force map (linkage Jacobian, both legs)
  B) armature (rotor reflected inertia)  0.035 (ref MJCF) / 0.010 / 0.003
  C) torque saturation                   20 / 40 / 54 N*m
  D) servo bandwidth (PD gain + control period) 50 Hz deploy vs 200/500 Hz
Reports rise[cm] / airtime[ms] / vz[m/s].  Pure physics, no training.
"""
import json
import numpy as np
import mujoco

XML = r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml"
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]

m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
m.opt.timestep = 0.001
JID = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n) for n in LEG + WHL}
BID = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n) for n in ["left_wheel", "right_wheel"]}
qa = {n: m.jnt_qposadr[JID[n]] for n in LEG + WHL}
va = {n: m.jnt_dofadr[JID[n]] for n in LEG + WHL}
LEGD = [va[n] for n in LEG]
wb = set(BID.values())
mass = float(sum(m.body_mass))
print("model: nq=%d nv=%d nu=%d neq=%d mass=%.2f kg  weight=%.1f N" % (m.nq, m.nv, m.nu, m.neq, mass, mass * 9.81))


def touching():
    for k in range(d.ncon):
        g = d.contact[k]
        if m.geom_bodyid[g.geom1] in wb or m.geom_bodyid[g.geom2] in wb:
            return True
    return False


class Runner:
    """Zero-order-hold PD at an arbitrary control period on top of a 1 kHz sim."""

    def __init__(self, kp, kd, eff, ctrl_dt):
        self.kp, self.kd, self.eff, self.dt = kp, kd, eff, ctrl_dt
        self.n = max(1, int(round(ctrl_dt / 0.001)))
        self.i = 0
        self.tgt = {"front": 0.0, "rear": 0.0}
        self.cmd = {n: 0.0 for n in LEG + WHL}

    def set(self, front, rear):
        self.tgt = {"front": front, "rear": rear}

    def step(self, ksteps):
        for _ in range(ksteps):
            if self.i % self.n == 0:
                for nm in LEG:
                    key = "rear" if "rear" in nm else "front"
                    q, dq = d.qpos[qa[nm]], d.qvel[va[nm]]
                    self.cmd[nm] = float(np.clip(self.kp * (self.tgt[key] - q) - self.kd * dq,
                                                 -self.eff, self.eff))
                for nm in WHL:
                    self.cmd[nm] = float(np.clip(1.5 * (0.0 - d.qvel[va[nm]]), -10.0, 10.0))
            self.i += 1
            for nm in LEG + WHL:
                d.qfrc_applied[va[nm]] = self.cmd[nm]
            mujoco.mj_step(m, d)


def trial(cr, pu, thc, thp, kp, kd, eff, armature, ctrl_dt,
          t_settle=1.2, t_crouch=0.8, t_push=0.35, t_after=1.8):
    for n in LEG:
        m.dof_armature[va[n]] = armature
    mujoco.mj_resetDataKeyframe(m, d, 0)
    d.qfrc_applied[:] = 0
    r = Runner(kp, kd, eff, ctrl_dt)
    r.set(0.0, 0.0)
    r.step(int(t_settle / 0.001))
    z0 = float(d.qpos[2])
    r.set(cr, thc)
    r.step(int(t_crouch / 0.001))
    zc = float(d.qpos[2])
    r.set(pu, thp)
    pk = zc
    vz = 0.0
    air = 0.0
    t_sep = int((t_crouch + t_push) / 0.001)
    for i in range(int(t_after / 0.001)):
        r.step(1)
        pk = max(pk, float(d.qpos[2]))
        vz = max(vz, float(d.qvel[2]))
        if not touching():
            air += 0.001
        elif i > t_sep and air > 20.0:
            break
    return (pk - z0) * 100.0, air * 1000.0, vz, (z0 - zc) * 100.0


print("\n=== A) linkage: torque -> vertical force (static, both legs) ===")
jac = np.zeros((3, m.nv))
jrc = np.zeros((3, m.nv))
for pose in (0.0, -0.35, -0.6, -0.8):
    for n in LEG:
        m.dof_armature[va[n]] = 0.035
    mujoco.mj_resetDataKeyframe(m, d, 0)
    r = Runner(80.0, 3.0, 54.0, 0.002)
    r.set(pose, 0.0)
    r.step(6000)
    mujoco.mj_forward(m, d)
    Jv = np.zeros((2, len(LEGD)))
    for k, b in enumerate(["left_wheel", "right_wheel"]):
        mujoco.mj_jacBody(m, d, jac, jrc, BID[b])
        Jv[k] = jac[2, LEGD]
    jt = Jv.sum(axis=0)
    per = float(np.abs(jt).sum())
    print("  crank q=%+.2f  h=%.3f m  dh/dq=%-34s  %.2f N per N*m -> 2x40Nm=%.0f N=%.2f xW | 2x20Nm=%.2f xW"
          % (pose, float(d.qpos[2]), np.array2string(jt, precision=3, suppress_small=True),
             per, per * 80, per * 80 / (mass * 9.81), per * 40 / (mass * 9.81)))

print("\n=== B/C/D) armature x torque-limit x servo-bandwidth ===")
POSES = [(-0.6, 1.05, 0.5, -0.5), (-0.75, 1.2, 0.6, -0.6), (-0.45, 0.9, 0.3, -0.3),
         (-0.85, 1.35, 0.7, -0.7)]
res = []
for armature in (0.035, 0.010, 0.003):
    for eff in (20.0, 40.0, 54.0):
        for kp, kd, cdt in ((60.0, 2.0, 0.02), (150.0, 4.0, 0.02), (300.0, 6.0, 0.005),
                            (500.0, 8.0, 0.002)):
            best = (-1.0, -1.0, -1.0, -1.0)
            argb = None
            for p in POSES:
                out = trial(p[0], p[1], p[2], p[3], kp, kd, eff, armature, cdt)
                if out[1] > best[1]:
                    best, argb = out, p
            res.append((armature, eff, kp, kd, cdt) + best)
            print("  arm=%.3f eff=%4.0f kp=%5.0f kd=%3.0f dt=%4.0fms -> rise %5.1f cm  air %5.0f ms  "
                  "vz %4.2f  crouch %4.1f cm  pose %s"
                  % (armature, eff, kp, kd, cdt * 1e3, best[0], best[1], best[2], best[3], argb))
json.dump([[float(x) for x in r] for r in res], open(r"D:/claude2/fangzhen/docs/jump_sweep.json", "w"))
print("\n=== ballistic height from airtime  h = g*(T_air/2)^2/2 ===")
for armature, eff, kp, kd, cdt, rise, air, vz, cd in res:
    print("  arm=%.3f eff=%4.0f kp=%5.0f dt=%4.0fms   air %5.0f ms -> %5.1f cm"
          % (armature, eff, kp, cdt * 1e3, air, 9.81 * (air / 2000.0) ** 2 / 2 * 100))
