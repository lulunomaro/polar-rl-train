"""Generate the deployment stand-up KEYFRAME on the correct assembly branch.

Why this exists (docs/HOWTO.md 33, 35): the leg is a CLOSED chain with a preloaded gas spring
(6000 N/m x 58 mm = 350 N = 1.8x body weight), so "zero torque" is not a rest state - left alone
for a second the robot throws itself onto the other assembly branch (measured: base_z 0.075 ->
0.246, hips 3.93/6.58 rad).  A deployment that spawns at qpos=0 and then waits for a controller to
activate therefore hands the policy a machine it has never seen.

The fix is to spawn ON the trained stance with the PASSIVE joints already satisfied, and that
state is not guessed: it is produced by holding the hips at the measured stance with the training
PD until every equality gap is < 1e-4 m, then freezing the resulting qpos into a <keyframe>.

Outputs
  docs/audit/stand_keyframe.json      qpos + qvel + the verification numbers
  a <keyframe> appended to the deployment MJCF (idempotent, marker-delimited)
"""
import argparse, json, os
import mujoco
import numpy as np

ROOT = r"D:/claude2/fangzhen"
ap = argparse.ArgumentParser()
ap.add_argument("--plant", default=os.path.join(ROOT, "robot/out_cc/scene_cc.xml"))
ap.add_argument("--stance", default=os.environ.get("RM_STANCE", "0.222,0.097,0.230,0.117"),
                help="hip targets, contract order L_front1 L_rear1 R_front1 R_rear1")
ap.add_argument("--seconds", type=float, default=3.0)
ap.add_argument("--write-to", default="", help="deployment MJCF to append the keyframe to")
a = ap.parse_args()

m = mujoco.MjModel.from_xml_path(a.plant)
d = mujoco.MjData(m)
nm = lambda o, i: mujoco.mj_id2name(m, o, i) or ""
JN = {nm(mujoco.mjtObj.mjOBJ_JOINT, i): i for i in range(m.njnt)}
QA = {k: int(m.jnt_qposadr[v]) for k, v in JN.items()}
VA = {k: int(m.jnt_dofadr[v]) for k, v in JN.items()}
AN = {nm(mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
STANCE = dict(zip(LEG, [float(x) for x in a.stance.split(",")]))
assert len(STANCE) == 4


def gaps():
    out = []
    for i in range(m.neq):
        if int(m.eq_type[i]) != int(mujoco.mjtEq.mjEQ_CONNECT):
            continue
        b1, b2 = int(m.eq_obj1id[i]), int(m.eq_obj2id[i])
        a1 = np.asarray(m.eq_data[i][0:3], float); a2 = np.asarray(m.eq_data[i][3:6], float)
        R1 = np.asarray(d.xmat[b1], float).reshape(3, 3); R2 = np.asarray(d.xmat[b2], float).reshape(3, 3)
        p1 = np.asarray(d.xpos[b1], float) + R1 @ a1
        p2 = np.asarray(d.xpos[b2], float) + R2 @ a2
        out.append(float(np.linalg.norm(p1 - p2)))
    return out


mujoco.mj_resetDataKeyframe(m, d, 0)
# The first version of this script settled the legs with a PD and left the wheels damped-only,
# and the resulting keyframe had 20.6 deg of nose-down pitch baked into its quaternion
# (w=0.9838, y=0.179).  Handing that to the policy is out of distribution - training spawns
# UPRIGHT - and it was the reason the parity harness still toppled after the keyframe landed.
# So the settle now balances pitch through the wheels, exactly like the deployment stand-up law.
BAL = (float(os.environ.get("RM_PREP_KP", "8.0")),
       float(os.environ.get("RM_PREP_KD", "1.2")),
       float(os.environ.get("RM_PREP_VMAX", "20.0")))
bal_v = 0.0
root_dof = int(m.jnt_dofadr[JN[[k for k in JN if "floating" in k or "base" in k][0]]])
for _ in range(int(a.seconds / m.opt.timestep)):
    for jn, tgt in STANCE.items():
        d.ctrl[AN[jn.replace("_joint", "_ctrl")]] = float(np.clip(
            120.0 * (tgt - d.qpos[QA[jn]]) - 5.0 * d.qvel[VA[jn]], -60, 60))
    R = np.asarray(d.xmat[1], float).reshape(3, 3)
    g = R.T @ np.array([0.0, 0.0, -1.0])
    pitch = float(np.arcsin(np.clip(g[0], -1.0, 1.0)))
    rate = float(d.qvel[root_dof + 1])
    # A plain proportional law on the WHEEL VELOCITY TARGET cannot hold a segway: with a
    # damping-only servo (tau = kd*(v_cmd - v)) any constant tilt settles at a constant wheel
    # speed where the torque - and therefore the horizontal force - is exactly zero.  Measured:
    # kp=0, 3 and 8 all converge to +20.5 deg.  The balance has to command ACCELERATION, so
    # integrate the tilt term into the velocity target (this is what a real segway loop does).
    bal_v = float(np.clip(bal_v + (BAL[0] * pitch + BAL[1] * rate) * m.opt.timestep,
                          -BAL[2], BAL[2]))
    for jn in ("left_wheel_joint", "right_wheel_joint"):
        d.ctrl[AN[jn.replace("_joint", "_ctrl")]] = float(np.clip(
            1.5 * (bal_v - d.qvel[VA[jn]]), -5.5, 5.5))
    mujoco.mj_step(m, d)

g = gaps()
qpos = d.qpos.copy()
wheels = []
for jn in ("left_wheel_joint", "right_wheel_joint"):
    gi = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, jn.replace("_joint", "_col"))
    wheels.append(float(d.geom_xpos[gi, 2] - m.geom_size[gi][0]))
lim = {}
for jn, j in JN.items():
    if m.jnt_limited[j]:
        lo, hi = m.jnt_range[j]
        q = float(d.qpos[QA[jn]])
        if q <= lo + 1e-4 or q >= hi - 1e-4:
            lim[jn] = [round(q, 4), round(float(lo), 3), round(float(hi), 3)]
res = dict(plant=os.path.basename(a.plant), stance=STANCE, seconds=a.seconds,
           base_z=round(float(qpos[2]), 5), eq_gap_max_mm=round(1000 * max(g), 5),
           pitch_deg=round(float(np.degrees(np.arcsin(np.clip(
               (np.asarray(d.xmat[1], float).reshape(3, 3).T
                @ np.array([0.0, 0.0, -1.0]))[0], -1, 1)))), 3),
           wheel_bottom_z=[round(x, 5) for x in wheels],
           achieved_hips={k: round(float(qpos[QA[k]]), 4) for k in LEG},
           passive_at_limit=lim, qpos=[round(float(x), 6) for x in qpos],
           qvel=[0.0] * m.nv)
print("base_z=%.5f  pitch=%.2f deg  max equality gap=%.5f mm  wheel bottoms=%s  hips=%s"
      "  limits=%s"
      % (res["base_z"], res["pitch_deg"], res["eq_gap_max_mm"],
         [round(x, 4) for x in wheels], res["achieved_hips"], lim or "none"))
assert res["eq_gap_max_mm"] < 0.1, "the chain is not closed - refusing to write a keyframe"
assert not lim, "a passive joint is sitting on its limit - wrong branch?"
assert max(abs(x) for x in wheels) < 0.02, "wheels are not on the floor"
assert abs(res["pitch_deg"]) < 5.0, (   # training spawns UPRIGHT; a pitched keyframe
    "keyframe pitch %.1f deg is out of distribution" % res["pitch_deg"])
os.makedirs(os.path.join(ROOT, "docs/audit"), exist_ok=True)
json.dump(res, open(os.path.join(ROOT, "docs/audit/stand_keyframe.json"), "w"), indent=1)
print("wrote docs/audit/stand_keyframe.json")

if a.write_to:
    t = open(a.write_to, encoding="utf-8").read()
    beg, endm = "<!-- STAND_KEYFRAME_BEGIN -->", "<!-- STAND_KEYFRAME_END -->"
    line = '  <keyframe><key name="stand" qpos="%s" qvel="%s"/></keyframe>' % (
        " ".join("%.6f" % v for v in res["qpos"]), " ".join("0" for _ in res["qvel"]))
    if beg in t:
        pre, rest = t.split(beg, 1); post = rest.split(endm, 1)[1]
        t = pre + beg + "\n" + line + "\n" + endm + post
    else:
        t = t.replace("</mujoco>", "%s\n%s\n%s\n</mujoco>" % (beg, line, endm))
    open(a.write_to, "w", encoding="utf-8", newline="\n").write(t)
    print("keyframe written into", a.write_to)
    chk = mujoco.MjModel.from_xml_path(a.write_to)
    dd = mujoco.MjData(chk)
    mujoco.mj_resetDataKeyframe(chk, dd, 0)
    mujoco.mj_forward(chk, dd)
    print("reloaded: nkey=%d  base_z=%.5f  |qvel|=%.1f" % (chk.nkey, dd.qpos[2],
                                                           float(np.abs(dd.qvel).max())))
