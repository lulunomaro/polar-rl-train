"""Authoritative joint-limit / joint-axis health check on an isolated, welded leg.

cc_gaps.py writes the analytic pose straight into qpos and only measures equality gaps, so it
cannot see a passive joint sitting outside its own <joint range> (MuJoCo clamps that at step
time and silently jams the closed chain).  Here the base is welded, gravity is off, the two
actuated hip-axis joints are driven by the training PD gains, and every other joint carries
only LIGHT dissipation - enough to settle, not enough to stall the mechanism.  What it
settles to is what the simulator really allows.
"""
import os, sys
import numpy as np, mujoco

ROOT = r"D:/claude2/fangzhen"
XML = os.path.join(ROOT, "robot/out_cc/rm_vehicle_cc.xml")
KEYS = ("rear1", "front1", "rear2", "front2", "front3", "front4", "spring1", "spring2", "wheel")
ACT = ("rear1", "front1")
SIDE = "left"
KP, KD, SOFT_D = 60.0, 2.0, 0.4     # SOFT_D: dissipate, do not resist statically

WELD = os.path.join(ROOT, "robot/out_cc/_welded_leg_test.xml")
_t = open(XML, encoding="utf-8").read()
assert '<freejoint name="floating_base"/>' in _t
open(WELD, "w", encoding="utf-8").write(_t.replace('<freejoint name="floating_base"/>', ""))
m = mujoco.MjModel.from_xml_path(WELD)
d = mujoco.MjData(m)
m.opt.gravity[2] = 0.0
for g in range(m.ngeom):
    if m.geom_group[g] == 2:
        m.geom_group[g] = 5
J = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
idx = {}
for k in KEYS:
    j = J("%s_%s_joint" % (SIDE, k)); assert j >= 0, k
    idx[k] = (m.jnt_qposadr[j], m.jnt_dofadr[j],
              (float(m.jnt_range[j][0]), float(m.jnt_range[j][1])) if m.jnt_limited[j] else None)
RDOF = [m.jnt_dofadr[J("right_%s_joint" % k)] for k in KEYS]
print("welded-leg model: nq=%d nv=%d nu=%d neq=%d" % (m.nq, m.nv, m.nu, m.neq))


def loop_gap():
    g = 0.0
    for e in range(m.neq):
        b1, b2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
        p1 = d.xpos[b1] + d.xmat[b1].reshape(3, 3) @ ed[0:3]
        p2 = d.xpos[b2] + d.xmat[b2].reshape(3, 3) @ ed[3:6]
        g = max(g, 1000.0 * float(np.linalg.norm(p1 - p2)))
    return g


rows = []
for th in np.arange(-0.55, 0.551, 0.11):
    for cr in np.arange(-0.55, 0.551, 0.11):
        mujoco.mj_resetData(m, d)
        for i in range(8000):
            d.qfrc_applied[:] = 0.0
            for k in ACT:
                a, v, _ = idx[k]
                tgt = th if k == "rear1" else cr
                d.qfrc_applied[v] = KP * (tgt - d.qpos[a]) - KD * d.qvel[v]
            for k in KEYS:
                if k not in ACT:
                    d.qfrc_applied[idx[k][1]] = -SOFT_D * d.qvel[idx[k][1]]
            for v in RDOF:
                d.qfrc_applied[v] = -SOFT_D * d.qvel[v]
            mujoco.mj_step(m, d)
        e = {k: float(d.qpos[idx[k][0]]) for k in KEYS}
        rows.append((th, cr, e, loop_gap(), float(np.abs(d.qvel).max())))

print("\n%-7s %-7s | %-9s %-9s %-9s %-9s %-9s %-9s | %-8s %s" %
      ("thigh", "crank", "rear2", "front2", "front3", "front4", "spr1", "spr2",
       "gap mm", "track err"))
trk = []
for th, cr, e, g, qv in rows:
    trk.append(max(abs(e["rear1"] - th), abs(e["front1"] - cr)))
    if abs(cr) < 1e-9 or abs(th) < 1e-9:
        print("%-7.2f %-7.2f | %+9.4f %+9.4f %+9.4f %+9.4f %+9.4f %+9.4f | %-8.4f %.4f" %
              (th, cr, e["rear2"], e["front2"], e["front3"], e["front4"], e["spring1"],
               e["spring2"], g, trk[-1]))
print("\nworst actuated tracking error: %.4f rad (%.2f deg)" % (max(trk), np.degrees(max(trk))))
clip = {k: [9e9, -9e9] for k in KEYS}
viol = {k: 0 for k in KEYS}
for th, cr, e, g, qv in rows:
    for k in KEYS:
        clip[k] = [min(clip[k][0], e[k]), max(clip[k][1], e[k])]
        if idx[k][2] and (e[k] < idx[k][2][0] - 1e-6 or e[k] > idx[k][2][1] + 1e-6):
            viol[k] += 1
print("\n== passive joint: solver-achieved range vs MJCF <joint range> ==")
bad = []
for k in KEYS:
    if not idx[k][2]:
        print("  %-8s unlimited            achieved [%9.4f %9.4f]" % (k, clip[k][0], clip[k][1]))
        continue
    lo, hi = idx[k][2]; a, b = clip[k]
    ok = a >= lo - 1e-6 and b <= hi + 1e-6
    if not ok:
        bad.append(k)
    print("  %-8s [%8.3f %8.3f]  achieved [%8.4f %8.4f]  margin [%+.3f %+.3f]  %s" %
          (k, lo, hi, a, b, a - lo, hi - b,
           "OK" if ok else "**CLIPPED in %d/121 poses; needs [%8.3f %8.3f]**"
           % (viol[k], a - 0.15, b + 0.15)))
print("\nworst equality gap %.4f mm    clipped joints: %s" % (max(r[3] for r in rows), bad or "none"))