"""Measure the ACHIEVABLE range of every passive joint with the physics solver, over the
full commanded envelope the RL policy can actually ask for, and emit the joint ranges that
bracket it.  This replaces analytic-sign guesses (which is how front3 ended up 0.045 rad
outside its own stop)."""
import json, os, sys
import numpy as np, mujoco

ROOT = r"D:/claude2/fangzhen"
XML = os.path.join(ROOT, "robot/out_cc/_welded_leg_test.xml")
KEYS = ("rear1", "front1", "rear2", "front2", "front3", "front4", "spring1", "spring2", "wheel")
PASSIVE = ("rear2", "front2", "front3", "front4", "spring1", "spring2")
ACT = ("rear1", "front1")
KP, KD, SOFT_D = 60.0, 2.0, 0.4
# the policy's leg action scale is 0.5 rad/unit and actions saturate near +-1.6, plus
# ±0.1 reset noise -> +-0.8 rad on each hip axis is the honest command envelope
ENV = np.arange(-0.80, 0.801, 0.08)

m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
m.opt.gravity[2] = 0.0
for g in range(m.ngeom):
    if m.geom_group[g] == 2:
        m.geom_group[g] = 5
# open the stops first so the measurement is not itself limited by them
for k in KEYS:
    j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "left_%s_joint" % k)
    m.jnt_range[j] = [-99.0, 99.0]
    m.jnt_limited[j] = 1 if k in PASSIVE else 0
J = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
idx = {k: (m.jnt_qposadr[J("left_%s_joint" % k)], m.jnt_dofadr[J("left_%s_joint" % k)])
       for k in KEYS}
RDOF = [m.jnt_dofadr[J("right_%s_joint" % k)] for k in KEYS]


def loop_gap():
    g = 0.0
    for e in range(m.neq):
        b1, b2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
        p1 = d.xpos[b1] + d.xmat[b1].reshape(3, 3) @ ed[0:3]
        p2 = d.xpos[b2] + d.xmat[b2].reshape(3, 3) @ ed[3:6]
        g = max(g, 1000.0 * float(np.linalg.norm(p1 - p2)))
    return g


ach = {k: [9e9, -9e9] for k in KEYS}
gmax = 0.0
n = 0
for th in ENV:
    for cr in ENV:
        mujoco.mj_resetData(m, d)
        for _ in range(6000):
            d.qfrc_applied[:] = 0.0
            for k in ACT:
                a, v = idx[k]
                tgt = th if k == "rear1" else cr
                d.qfrc_applied[v] = KP * (tgt - d.qpos[a]) - KD * d.qvel[v]
            for k in KEYS:
                if k not in ACT:
                    d.qfrc_applied[idx[k][1]] = -SOFT_D * d.qvel[idx[k][1]]
            for v in RDOF:
                d.qfrc_applied[v] = -SOFT_D * d.qvel[v]
            mujoco.mj_step(m, d)
        n += 1
        gmax = max(gmax, loop_gap())
        for k in KEYS:
            a, v = idx[k]
            ach[k][0] = min(ach[k][0], float(d.qpos[a]))
            ach[k][1] = max(ach[k][1], float(d.qpos[a]))

print("welded-leg solve over the full commanded envelope: %d poses, worst gap %.4f mm" % (n, gmax))
print("\n%-9s %-26s %-26s %s" % ("joint", "currently in build_cc.py", "solver-achieved", "recommended"))
import re
bc = open(os.path.join(ROOT, "scripts/build_cc.py"), encoding="utf-8").read()
_f = re.findall(r'"(shank|link2|link3|link4|spring1)":\s*\((-?[\d.]+),\s*(-?[\d.]+)\)', bc)
cur = {k: (lo, hi) for k, lo, hi in _f}
name = {"rear2": "shank", "front2": "link2", "front3": "link3", "front4": "link4",
        "spring1": "spring1"}
out = {}
for k in PASSIVE:
    a, b = ach[k]
    lo, hi = round(a - 0.15, 2), round(b + 0.15, 2)
    c = cur.get(name.get(k, k)) if k != "spring2" else ("-0.030", "0.085")
    if k == "spring2":
        c = ("-0.030", "0.085")   # SPRING_SLIDE, metres of slider travel
    flag = ""
    if c and k != "spring2":
        cl, ch = float(c[0]), float(c[1])
        if cl > a + 1e-6 or ch < b - 1e-6:
            flag = "  ** CURRENT RANGE DOES NOT BRACKET THE WORKSPACE **"
    print("  %-8s %-26s [%+9.4f %+9.4f]      (%+.4f, %+.4f)%s" %
          (k, str(c), a, b, lo, hi, flag))
    out[k] = [lo, hi]
out["_spring2_mm"] = [round(ach["spring2"][0], 4), round(ach["spring2"][1], 4)]
json.dump(out, open(os.path.join(ROOT, "docs/audit/passive_ranges.json"), "w"), indent=1)
print("\nwrote docs/audit/passive_ranges.json")