"""Is 'it cannot jump high' a MOTOR-MODELLING problem?

Compare our leg-actuator model against the datasheet-correct DM-J8009 model on the
closed-chain MuJoCo robot (robot/out_cc/scene_cc.xml).

Motor data (sources: docs/MOTOR_PARAMS.md)
  DM-J8009-2EC, 9:1  : rated 20 N*m, peak 40 N*m, no-load 335 rpm @48V (~167 rpm @24V
                       -> 17.5 rad/s), rotor inertia 1.95e-4 kg*m^2
                       => armature = 1.95e-4 * 9^2 = 0.0158 kg*m^2
  SCUT wheelbipe RL   : kp=60 kd=2 effort=40 velocity_limit=17 armature=0.0158
  our current model   : effort=50.9 armature=0.035 velocity_limit=none
  reference MJCF      : forcerange +-54, armature 0.035, no velocity limit

Open-loop crouch -> saturated extension.  No training involved.
"""
import json
import numpy as np
import mujoco

XML = r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml"
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


def contact_state():
    """(touching, total vertical ground force on the wheels [N])."""
    touching = False
    fz = 0.0
    for k in range(d.ncon):
        c = d.contact[k]
        if m.geom_bodyid[c.geom1] in wb or m.geom_bodyid[c.geom2] in wb:
            touching = True
            mujoco.mj_contactForce(m, d, k, cforce)
            fz += cforce[0, 0] * c.frame[0] + cforce[1, 0] * c.frame[3] + cforce[2, 0] * c.frame[6]
    return touching, fz


CONFIGS = [
  # name, effort, armature, vmax, kp, kd, ctrl_dt, linear t-w derating, leg frictionloss
  ("A_our_training", 50.9, 0.035, 1e9, 60.0, 2.0, 0.020, False, 1.5),
  ("B_ref_mjcf  ", 54.0, 0.035, 1e9, 60.0, 2.0, 0.020, False, 1.5),
  ("C_DM8009_24V", 40.0, 0.0158, 17.0, 60.0, 2.0, 0.020, False, 1.5),
  ("D_DM8009_1k ", 40.0, 0.0158, 17.0, 200.0, 5.0, 0.001, False, 1.5),
  ("E_no_speedcap", 40.0, 0.0158, 1e9, 60.0, 2.0, 0.020, False, 1.5),
  ("F_DM8009_16:1", 40.0, 0.0499, 9.8, 60.0, 2.0, 0.020, False, 1.5),
  ("G_tw_curve  ", 40.0, 0.0158, 17.0, 200.0, 5.0, 0.001, True, 1.5),
  ("H_lowfric   ", 40.0, 0.0158, 1e9, 200.0, 5.0, 0.001, False, 0.0),
]
POSES = [(-0.6, 1.05, 0.5, -0.5), (-0.75, 1.2, 0.6, -0.6), (-0.85, 1.35, 0.7, -0.7)]


def run(cfg, pose, t_settle=1.0, t_crouch=0.9, t_push=0.32, t_after=1.5):
    name, eff, arm, vmax, kp, kd, cdt, derate, friction = cfg
    for n in LEG:
        m.dof_armature[va[n]] = arm
        m.dof_frictionloss[va[n]] = friction
    mujoco.mj_resetDataKeyframe(m, d, 0)
    d.qfrc_applied[:] = 0
    nhold = max(1, int(round(cdt / 0.001)))
    tgt = {"front": 0.0, "rear": 0.0}
    cmd = {n: 0.0 for n in LEG}
    st = dict(work=0.0, pkw=0.0, nsat=0, nspd=0, ncmd=0, maxfz=0.0, maxomega=0.0)
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
                    if abs(u) > lim + 1e-9:
                        st["nsat"] += 1
                    if abs(dq) > 0.95 * vmax:
                        st["nspd"] += 1
                    st["maxomega"] = max(st["maxomega"], abs(dq))
            tick[0] += 1
            for nm in LEG:
                d.qfrc_applied[va[nm]] = cmd[nm]
                p = abs(cmd[nm] * d.qvel[va[nm]])
                st["work"] += p * 0.001
                st["pkw"] = max(st["pkw"], p)
            for nm in WHL:
                d.qfrc_applied[va[nm]] = float(np.clip(1.5 * (0.0 - d.qvel[va[nm]]), -5.5, 5.5))
            mujoco.mj_step(m, d)
            _, fz = contact_state()
            st["maxfz"] = max(st["maxfz"], fz)

    step(int(t_settle / 0.001))
    z0 = float(d.qpos[2])
    tgt.update(front=pose[0], rear=pose[2])
    step(int(t_crouch / 0.001))
    zc = float(d.qpos[2])
    tgt.update(front=pose[1], rear=pose[3])
    pk = zc
    vz = 0.0
    air = 0
    took_off = False
    t_rel = int((t_crouch + t_push * 0.5) / 0.001)
    for j in range(int(t_after / 0.001)):
        step(1)
        touching, _ = contact_state()
        pk = max(pk, float(d.qpos[2]))
        vz = max(vz, float(d.qvel[2]))
        if vz > 0.30:
            took_off = True
        if took_off and not touching and j > t_rel:
            air += 1
        elif air > 30 and touching:
            break
    return dict(name=name, eff=eff, arm=arm, vmax=vmax, kp=kp, kd=kd, cdt=cdt, friction=friction,
                pose=pose, crouch_cm=(z0 - zc) * 100.0, rise_cm=(pk - z0) * 100.0,
                vz=vz, h_vz=vz * vz / (2 * G) * 100.0, air_ms=air,
                h_air=G * (air / 2000.0) ** 2 / 2 * 100.0,
                peak_fz_N=st["maxfz"], work_J=st["work"], peak_W=st["pkw"],
                maxomega=st["maxomega"],
                sat_pct=100.0 * st["nsat"] / max(1, st["ncmd"]),
                spd_pct=100.0 * st["nspd"] / max(1, st["ncmd"]))


print("model nq=%d nv=%d nu=%d neq=%d mass=%.2f kg  weight=%.1f N" % (m.nq, m.nv, m.nu, m.neq, mass, mass * G))
print("\n%-14s %-26s %6s %6s %6s %6s %6s %7s %7s %6s %6s %6s" %
      ("config", "(Nm/armature/lim/kp/Hz)", "crouch", "rise", "vz", "h_vz", "air", "h_air", "peakFz", "work", "peakW", "sat%"))
rows = []
for cfg in CONFIGS:
    best = None
    for p in POSES:
        o = run(cfg, p)
        if best is None or o["air_ms"] > best["air_ms"] or (o["air_ms"] == best["air_ms"] and o["h_vz"] > best["h_vz"]):
            best = o
    rows.append(best)
    print("%-14s %-26s %5.1f %5.1f %5.2f %5.1f %5.0f %6.1f %6.0f %5.0fJ %5.0fW %5.0f%%" %
          (best["name"], "(%.0f/%.4f/%.0f/%.0f/%.0f)" % (best["eff"], best["arm"], best["vmax"], best["kw" if False else "kp"], 1.0 / best["cdt"]),
           best["crouch_cm"], best["rise_cm"], best["vz"], best["h_vz"], best["air_ms"], best["h_air"],
           best["peak_fz_N"], best["work_J"], best["peak_W"], best["sat_pct"]))
print("\nmax joint speed seen / speed-saturated fraction:")
for r in rows:
    print("  %-14s wmax=%5.2f rad/s  spd-limited %4.0f%%  torque-limited %4.0f%%  leg-friction %.1f" %
          (r["name"], r["maxomega"], r["spd_pct"], r["sat_pct"], r["friction"]))
json.dump(rows, open(r"D:/claude2/fangzhen/docs/jump_configs.json", "w"), indent=1)
