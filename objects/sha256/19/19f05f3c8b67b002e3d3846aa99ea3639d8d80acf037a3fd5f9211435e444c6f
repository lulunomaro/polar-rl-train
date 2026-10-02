"""Jump feasibility, corrected.

Measured on the validated model (scripts/leg2d.py + scripts/cc_gaps.py):
  MJ crank qpos  +  -> leg EXTENDED   (analytic crank -)
  MJ crank qpos  -  -> leg COMPRESSED (analytic crank +)
so a jump is: crouch to crank<0 (store energy in the 350 N gas spring), then a saturated
step to crank>0.  Airborne time is detected from real wheel contacts.
"""
import sys
import numpy as np, mujoco
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m); m.opt.timestep = 0.001
def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
def B(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
qa = {n: m.jnt_qposadr[J(n)] for n in LEG + WHL}; va = {n: m.jnt_dofadr[J(n)] for n in LEG + WHL}
wheel_bodies = {B("left_wheel"), B("right_wheel")}
L = Kite2D(CAD, "cc")
def ext_mj(th_mj, cr_mj):
    r = L.solve(-th_mj, -cr_mj); return float("nan") if r is None else r["ext"] / 1000.0
def touching():
    for g in d.contact:
        for ge in (g.geom1, g.geom2):
            if m.geom_bodyid[ge] in wheel_bodies:
                return True
    return False

def trial(crouch, push, th_c, th_p, kp, kd, eff, t_crouch=0.7, t_push=0.30, t_free=1.5):
    mujoco.mj_resetDataKeyframe(m, d, 0); d.qvel[:] = 0
    def hold(tc, tt, n):
        for _ in range(n):
            for nm in LEG:
                tgt = tt if "rear" in nm else tc
                d.qfrc_applied[va[nm]] = float(np.clip(kp * (tgt - d.qpos[qa[nm]]) - kd * d.qvel[va[nm]], -eff, eff))
            for nm in WHL:
                d.qfrc_applied[va[nm]] = float(np.clip(1.5 * (0.0 - d.qvel[va[nm]]), -10, 10))
            mujoco.mj_step(m, d)
    hold(0.0, 0.0, 900)
    z_st = float(d.qpos[2])
    hold(crouch, th_c, int(t_crouch / 0.001))
    z_low = float(d.qpos[2])
    hold(push, th_p, int(t_push / 0.001))
    pk = float(d.qpos[2]); air = 0.0; vz_max = 0.0; left = False
    for _ in range(int(t_free / 0.001)):
        for nm in LEG:
            d.qfrc_applied[va[nm]] = float(np.clip(kp * (push - d.qpos[qa[nm]]) - kd * d.qvel[va[nm]], -eff, eff))
        for nm in WHL:
            d.qfrc_applied[va[nm]] = float(np.clip(1.5 * (0.0 - d.qvel[va[nm]]), -10, 10))
        mujoco.mj_step(m, d)
        pk = max(pk, float(d.qpos[2])); vz_max = max(vz_max, float(d.qvel[2]))
        if not touching():
            left = True; air += 0.001
    return z_st, z_low, pk, air, vz_max, left

print(" crouch  push  thigh(c->p)  kp eff | z_stand z_low  peak | rise[cm] above-stand  air[ms] vmax")
res = []
for crouch in (-0.45, -0.6, -0.75, -0.9):
    for push in (0.6, 0.75, 0.9, 1.05):
        for th_c, th_p in ((0.0, 0.0), (0.3, -0.3), (0.5, -0.5)):
            for kp, eff in ((60, 30.0), (60, 54.0), (200, 54.0)):
                zs, zl, pk, air, vz, left = trial(crouch, push, th_c, th_p, kp, 2.0, eff)
                res.append((air * 1000, (pk - zs) * 100, (pk - zl) * 100, crouch, push, th_c, th_p, kp, eff, zs, zl, pk, vz, left))
res.sort(key=lambda r: (-r[0], -r[1]))
for r in res[:16]:
    print("  %+5.2f %+5.2f   %+.1f->%+.1f   %3d %2.0f | %.3f  %.3f  %.3f |  %6.1f      %6.1f     %5.0f  %.2f %s"
          % (r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[1], r[2], r[0], r[12], "AIR" if r[13] else "-"))
print("\nbest airborne: %.0f ms, rise above standing %.1f cm (crouch %+.2f push %+.2f thigh %+.1f->%+.1f kp %d eff %.0f)"
      % (res[0][0], res[0][1], res[0][3], res[0][4], res[0][5], res[0][6], res[0][7], res[0][8]))
n_air = sum(1 for r in res if r[13])
print("trials that actually left the ground: %d of %d" % (n_air, len(res)))
best_rise = max(res, key=lambda r: r[1])
print("best rise (air or not): %.1f cm above standing, air %.0f ms" % (best_rise[1], best_rise[0]))
