"""Jump-height vs MOTOR model: what actually limits the closed-chain robot?

  E1  control-authority ladder : same datasheet motor, only the servo rate/gain changes
  E2  minimum torque ladder    : smallest torque limit that still reaches a height
  E3  model comparison         : our trained plant vs reference MJCF vs the DM8009
                                datasheet plant, with/without a torque-speed envelope

Open loop (crouch -> saturated extension) on robot/out_cc/scene_cc.xml, 1 kHz physics,
contact-truth flight phase.  Writes docs/jump_motor_report.json and
docs/crops/fig_E_motor_jump.png.
"""
import json
import numpy as np
import mujoco

XML = __import__("os").environ.get("JUMP_XML", r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
G = 9.81

m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
m.opt.timestep = 0.001
JID = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n) for n in LEG + WHL}
BID = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n) for n in ["left_wheel", "right_wheel"]}
qa = {n: m.jnt_qposadr[JID[n]] for n in LEG + WHL}
va = {n: m.jnt_dofadr[JID[n]] for n in LEG + WHL}
wb = set(BID.values())
mass = float(sum(m.body_mass))
cforce = np.zeros((6, 1))


def contact():
    touching, fz = False, 0.0
    for k in range(d.ncon):
        c = d.contact[k]
        if m.geom_bodyid[c.geom1] in wb or m.geom_bodyid[c.geom2] in wb:
            touching = True
            mujoco.mj_contactForce(m, d, k, cforce)
            fz += (cforce[0, 0] * c.frame[0] + cforce[1, 0] * c.frame[3] + cforce[2, 0] * c.frame[6])
    return touching, fz


POSES = [(-0.6, 1.05, 0.5, -0.5), (-0.75, 1.2, 0.6, -0.6), (-0.85, 1.35, 0.7, -0.7),
         (-0.95, 1.5, 0.8, -0.8)]


def sim(eff, arm, vmax, kp, kd, cdt, derate=False, friction=(1.5, 1.5),
        pose=(-0.85, 1.35, 0.7, -0.7), t_settle=1.0, t_crouch=0.9, t_push=0.32, t_after=1.4):
    for n in LEG:
        m.dof_armature[va[n]] = arm
        m.dof_frictionloss[va[n]] = friction[0] if "front" in n else friction[1]
    mujoco.mj_resetDataKeyframe(m, d, 0)
    d.qfrc_applied[:] = 0
    nhold = max(1, int(round(cdt / 0.001)))
    tgt = {"front": 0.0, "rear": 0.0}
    cmd = {n: 0.0 for n in LEG}
    st = dict(wmax=0.0, nsat=0, ncmd=0, work=0.0, pkw=0.0)
    tick = [0]

    def step(nsteps):
        for _ in range(nsteps):
            if tick[0] % nhold == 0:
                for nm in LEG:
                    key = "rear" if "rear" in nm else "front"
                    q, dq = d.qpos[qa[nm]], d.qvel[va[nm]]
                    u = kp * (tgt[key] - q) - kd * dq
                    lim = eff * max(0.0, 1.0 - abs(dq) / vmax) if derate else eff
                    cmd[nm] = float(np.clip(u, -lim, lim))
                    st["ncmd"] += 1
                    st["nsat"] += int(abs(u) > lim + 1e-9)
                    st["wmax"] = max(st["wmax"], abs(dq))
            tick[0] += 1
            for nm in LEG:
                d.qfrc_applied[va[nm]] = cmd[nm]
                p = abs(cmd[nm] * d.qvel[va[nm]])
                st["work"] += p * 0.001
                st["pkw"] = max(st["pkw"], p)
            for nm in WHL:
                d.qfrc_applied[va[nm]] = float(np.clip(1.5 * (0.0 - d.qvel[va[nm]]), -5.5, 5.5))
            mujoco.mj_step(m, d)

    step(int(t_settle / 0.001))
    z0 = float(d.qpos[2])
    tgt.update(front=pose[0], rear=pose[2])
    step(int(t_crouch / 0.001))
    zc = float(d.qpos[2])
    tgt.update(front=pose[1], rear=pose[3])
    vz = 0.0
    flight = 0
    gap = 0
    apex = zc
    took_off = False
    for j in range(int(t_after / 0.001)):
        step(1)
        touching, _ = contact()
        vz = max(vz, float(d.qvel[2]))
        if (not touching) and vz > 0.5:
            took_off = True
        if took_off:
            apex = max(apex, float(d.qpos[2]))
            if not touching:
                flight += 1
                gap += 1
            else:
                if gap >= 10:
                    break
                gap = 0
    return dict(vz=vz, h_vz=vz * vz / (2 * G) * 100.0, air_ms=float(flight),
                h_air=G * (flight / 2000.0) ** 2 / 2 * 100.0,
                rise_cm=(apex - z0) * 100.0, crouch_cm=(z0 - zc) * 100.0,
                wmax=st["wmax"], sat_pct=100.0 * st["nsat"] / max(1, st["ncmd"]),
                work_J=st["work"], peak_W=st["pkw"],
                eff=eff, arm=arm, vmax=vmax, kp=kp, kd=kd, cdt=cdt, derate=derate)


def best_pose(**kw):
    return max((sim(pose=p, **kw) for p in POSES), key=lambda r: (r["air_ms"], r["h_vz"]))


print("plant file: %s" % XML)
print("plant: mass=%.2f kg  weight=%.1f N  nq=%d nv=%d neq=%d" % (mass, mass * G, m.nq, m.nv, m.neq))
out = {"mass_kg": mass, "E1": [], "E2": [], "E3": []}

print("\n=== E1  control authority (motor fixed: DM8009 40 N*m / 0.0158 / 17 rad/s) ===")
print("  %-26s %6s %6s %7s %7s %6s %6s" % ("servo", "crouch", "rise", "vz", "h_vz", "air", "wmax"))
for kp, kd, cdt, tag in ((60.0, 2.0, 0.020, "kp60  @50 Hz (ours)"),
                         (60.0, 2.0, 0.005, "kp60  @200 Hz"),
                         (120.0, 3.0, 0.002, "kp120 @500 Hz"),
                         (200.0, 5.0, 0.001, "kp200 @1 kHz (DM drive)"),
                         (300.0, 6.0, 0.001, "kp300 @1 kHz"),
                         (500.0, 8.0, 0.001, "kp500 @1 kHz (drive max)")):
    r = best_pose(eff=40.0, arm=0.0158, vmax=17.0, kp=kp, kd=kd, cdt=cdt)
    r["tag"] = tag
    out["E1"].append(r)
    print("  %-26s %5.1f %5.1f %6.2f %6.1f %5.0f %6.1f" % (tag, r["crouch_cm"], r["rise_cm"], r["vz"], r["h_vz"], r["air_ms"], r["wmax"]))

print("\n=== E2  minimum torque limit that still reaches each height (kp60@50Hz) ===")
print("  %-8s %6s %6s %7s %7s %6s %7s" % ("N*m", "crouch", "rise", "vz", "h_vz", "air", "sat%"))
for eff in (6.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.9, 54.0):
    r = best_pose(eff=eff, arm=0.0158, vmax=17.0, kp=60.0, kd=2.0, cdt=0.02)
    r["tag"] = "eff%.1f" % eff
    out["E2"].append(r)
    print("  %-8.1f %5.1f %5.1f %6.2f %6.1f %5.0f %6.0f%%" % (eff, r["crouch_cm"], r["rise_cm"], r["vz"], r["h_vz"], r["air_ms"], r["sat_pct"]))

print("\n=== E3  motor-model comparison ===")
CFG = [
  ("ours v9/v10 trained", dict(eff=50.9, arm=0.035, vmax=1e9, kp=60.0, kd=2.0, cdt=0.02)),
  ("reference MJCF", dict(eff=54.0, arm=0.035, vmax=1e9, kp=60.0, kd=2.0, cdt=0.02)),
  ("DM8009 datasheet 9:1", dict(eff=40.0, arm=0.0158, vmax=17.0, kp=60.0, kd=2.0, cdt=0.02)),
  ("DM8009 16:1", dict(eff=40.0, arm=0.0499, vmax=9.8, kp=60.0, kd=2.0, cdt=0.02)),
  ("DM8009 + t-w curve", dict(eff=40.0, arm=0.0158, vmax=17.0, kp=200.0, kd=5.0, cdt=0.001, derate=True)),
  ("ref friction set", dict(eff=40.0, arm=0.0158, vmax=17.0, kp=60.0, kd=2.0, cdt=0.02, friction=(1.5, 0.0))),
]
print("  %-24s %6s %6s %7s %7s %6s %7s %6s" % ("model", "crouch", "rise", "vz", "h_vz", "air", "peakW", "sat%"))
for tag, kw in CFG:
    r = best_pose(**kw)
    r["tag"] = tag
    out["E3"].append(r)
    print("  %-24s %5.1f %5.1f %6.2f %6.1f %5.0f %6.0fW %5.0f%%" %
          (tag, r["crouch_cm"], r["rise_cm"], r["vz"], r["h_vz"], r["air_ms"], r["peak_W"], r["sat_pct"]))
print("\nreference point: the RL policy v9 measured 17.4 cm (vz = 1.85 m/s) on the same 50.9 N*m plant.")
json.dump(out, open(r"D:/claude2/fangzhen/docs/jump_motor_report.json", "w"), indent=1)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(16.5, 5.2))
c1 = [r["h_vz"] for r in out["E1"]]
ax[0].barh([r["tag"] for r in out["E1"]], c1, color=["#c0392b"] + ["#2980b9"] * (len(c1) - 1))
ax[0].axvline(17.4, ls="--", c="k", lw=1.2)
ax[0].text(18.0, 0.15, "RL v9 = 17.4 cm", fontsize=9)
ax[0].set_xlabel("open-loop jump height  vz^2/2g  [cm]")
ax[0].set_title("E1  servo bandwidth, not torque\n(identical DM8009 40 N*m / 17 rad/s motor)")
ax[0].set_xlim(0, max(c1) * 1.4)
e = [r["eff"] for r in out["E2"]]
h = [r["h_vz"] for r in out["E2"]]
ax[1].plot(e, h, "o-", c="#27ae60", lw=2)
ax[1].axhline(17.4, ls="--", c="k", lw=1.2)
ax[1].text(28, 19.0, "RL v9 = 17.4 cm", fontsize=9)
ax[1].axhline(30, ls=":", c="#8e44ad")
ax[1].text(6.5, 31.0, "30 cm target", fontsize=9, color="#8e44ad")
ax[1].axvline(40, ls="-.", c="#c0392b", lw=1)
ax[1].text(40.8, max(h) * 0.30, "DM8009 peak 40 N*m", rotation=90, fontsize=8, color="#c0392b")
ax[1].axvline(50.9, ls=":", c="#7f8c8d", lw=1)
ax[1].text(51.6, max(h) * 0.30, "our 50.9", rotation=90, fontsize=8, color="#7f8c8d")
ax[1].set_xlabel("leg torque limit [N*m]")
ax[1].set_ylabel("jump height [cm]")
ax[1].set_title("E2  how much torque is really needed")
lbl = [r["tag"] for r in out["E3"]]
hv = [r["h_vz"] for r in out["E3"]]
pw = [r["peak_W"] for r in out["E3"]]
x = np.arange(len(lbl))
ax2 = ax[2].twinx()
ax[2].bar(x, hv, 0.55, color="#2980b9")
ax2.plot(x, pw, "s--", c="#e67e22", lw=2)
ax2.set_ylabel("total peak mechanical power [W]")
ax[2].set_xticks(x)
ax[2].set_xticklabels(lbl, rotation=28, ha="right", fontsize=8)
ax[2].set_ylabel("jump height [cm]")
ax[2].set_title("E3  motor model comparison")
for a in ax:
    a.grid(alpha=.25)
fig.suptitle("STEP double-wheel-leg, 20 kg: what limits the jump - motor model vs policy", fontsize=12)
fig.tight_layout()
fig.savefig(r"D:/claude2/fangzhen/docs/crops/fig_E_motor_jump.png", dpi=130)
print("figure -> docs/crops/fig_E_motor_jump.png")
