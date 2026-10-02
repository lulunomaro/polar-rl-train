"""Authoritative skill verification: plain MuJoCo + the exported ONNX + the deployment
control law.  Nothing here depends on mjlab's observation/reward bookkeeping, so the
reset-drift artefact that inflated the mjlab-side jump number cannot occur: airborne time
and body rise are read from `data.contact` and the free-joint qpos/qvel directly.

  python scripts/verify_skills_mujoco.py --onnx train/deploy/<policy>.onnx [--field]

Phases:  A run ladder   B gyro (小陀螺) ladder   C jump (跳) ladder   D field traverse
"""
import argparse, json, math, os
import numpy as np, mujoco, onnxruntime as ort

ap = argparse.ArgumentParser()
ap.add_argument("--onnx", required=True)
ap.add_argument("--scene", default=r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
ap.add_argument("--field-scene", default=r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle_cc/mjcf/scene_field.xml")
ap.add_argument("--out", default=r"D:/claude2/fangzhen/docs/crops/skills_mujoco.json")
ap.add_argument("--skip-field", action="store_true")
ap.add_argument("--leg-eff", type=float, default=50.9,
               help="50.9 = plant v3-v10 trained on; 40.0 = datasheet DM8009 peak")
ap.add_argument("--wheel-eff", type=float, default=10.0,
               help="10.0 = old contract; 5.5 = M3508 + 15.8:1 output stall")
ap.add_argument("--obs-order", default="contract", choices=["contract", "model"],
               help="order of the 4 leg entries in obs[10:14]/obs[16:20]. v3-v7 were trained\n"
                    "with mjlab preserve_order=False, i.e. MODEL order [rear1_L, front1_L,\n"
                    "rear1_R, front1_R]; v8+ uses the deployment CONTRACT order.")
a = ap.parse_args()

# action dims follow the actuator order, which is the contract order for every version
LEG = ["left_front1_joint", "left_rear1_joint", "right_front1_joint", "right_rear1_joint"]
WHL = ["left_wheel_joint", "right_wheel_joint"]
R = 0.073; DT = 0.001; DEC = 20
KP, KD, WKD = 60.0, 2.0, 1.5
# torque ceilings are the deployment contract; --leg-eff/--wheel-eff select the plant
LEG_EFF, WHL_EFF = a.leg_eff, a.wheel_eff
SCALE_LEG, SCALE_WHL = 0.5, 10.0


OBS_LEG = LEG if True else LEG   # replaced right after the args are parsed


class Runner:
    def __init__(self, xml):
        self.m = mujoco.MjModel.from_xml_path(xml)
        self.d = mujoco.MjData(self.m)
        self.m.opt.timestep = DT
        m, d = self.m, self.d
        def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
        def B(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
        self.qa = {n: m.jnt_qposadr[J(n)] for n in LEG + WHL}
        self.va = {n: m.jnt_dofadr[J(n)] for n in LEG + WHL}
        self.wb = {B("left_wheel"), B("right_wheel")}
        self.site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "imu")
        self.sess = ort.InferenceSession(a.onnx, providers=["CPUExecutionProvider"])
        self.iname = self.sess.get_inputs()[0].name
        self.last = np.zeros(6, np.float32)
        self.tgt = {}
        self.k = 0
        self.reset()

    def reset(self, x=0.0):
        d = self.d
        d.qpos[:] = 0.0; d.qvel[:] = 0.0
        d.qpos[0] = x; d.qpos[2] = R + 0.002; d.qpos[3] = 1.0
        mujoco.mj_forward(self.m, d)
        self.last[:] = 0.0; self.tgt = {}

    def infer(self, cmd, height, jump=0.0):
        m, d = self.m, self.d
        g = d.xmat[self.site].reshape(3, 3).T @ np.array([0.0, 0.0, -1.0])
        o = np.zeros(35, np.float32)
        o[0] = cmd[0]; o[1] = 0.0; o[2] = cmd[1]; o[3] = height * 5.0
        o[4:7] = d.qvel[3:6] * 0.5; o[7:10] = g
        o[10:14] = [d.qpos[self.qa[n]] for n in OBS_LEG]
        o[16:20] = [d.qvel[self.va[n]] * 0.1 for n in OBS_LEG]
        o[20:22] = [d.qvel[self.va[n]] * 0.1 for n in WHL]
        o[22:28] = self.last; o[28] = 1.0; o[32] = jump
        act = self.sess.run(None, {self.iname: o.reshape(1, 35)})[0][0].astype(np.float32)
        self.last = act
        self.tgt = {n: act[i] * SCALE_LEG for i, n in enumerate(LEG)}
        self.tgt.update({n: act[4 + i] * SCALE_WHL for i, n in enumerate(WHL)})

    def step(self, cmd=(0.0, 0.0), height=0.22, jump=0.0, n=1):
        # a CONTINUOUS step counter: the policy must run at 50 Hz no matter how the
        # caller chunks its step() calls (an earlier version re-inferred every single
        # 1 ms physics step in the field phase, i.e. 50x the trained rate)
        d = self.d
        for _ in range(n):
            if self.k % DEC == 0:
                self.infer(np.array(cmd, np.float32), height, jump)
            self.k += 1
            d.qfrc_applied[:] = 0.0
            for n_ in LEG:
                d.qfrc_applied[self.va[n_]] = np.clip(
                    KP * (self.tgt.get(n_, 0.0) - d.qpos[self.qa[n_]]) - KD * d.qvel[self.va[n_]],
                    -LEG_EFF, LEG_EFF)
            for n_ in WHL:
                d.qfrc_applied[self.va[n_]] = np.clip(
                    WKD * (self.tgt.get(n_, 0.0) - d.qvel[self.va[n_]]), -WHL_EFF, WHL_EFF)
            mujoco.mj_step(self.m, d)

    def wheels_down(self):
        for c in self.d.contact:
            if self.m.geom_bodyid[c.geom1] in self.wb or self.m.geom_bodyid[c.geom2] in self.wb:
                return True
        return False

    def pitch(self):
        g = self.d.xmat[self.site].reshape(3, 3).T @ np.array([0.0, 0.0, -1.0])
        return math.degrees(math.asin(np.clip(g[0], -1, 1)))

    def roll(self):
        g = self.d.xmat[self.site].reshape(3, 3).T @ np.array([0.0, 0.0, -1.0])
        return math.degrees(math.asin(np.clip(-g[1], -1, 1)))


rep = {"onnx": os.path.abspath(a.onnx), "scene": os.path.abspath(a.scene),
       "obs_order": a.obs_order}
OBS_LEG = (["left_rear1_joint", "left_front1_joint", "right_rear1_joint",
                  "right_front1_joint"] if a.obs_order == "model" else LEG)
rn = Runner(a.scene)

print("=== A 跑 / run ladder (measured vx from the free joint, 5 s each) ===")
print("  cmd vx | measured | err   | distance | roll  pitch")
run_rows = []
for vx in (0.5, 1.0, 1.5, 2.0, 2.5, 2.8):
    rn.reset()
    rn.step(n=1500)                                   # 1.5 s settle with zero command
    x0 = rn.d.qpos[0]
    rn.step(cmd=(vx, 0.0), n=2000)                  # 2 s of acceleration
    acc = 0.0; ns = 0
    for _ in range(60):                             # steady state: last 3 s
        rn.step(cmd=(vx, 0.0), n=50)
        acc += float(rn.d.qvel[0]); ns += 50
    v = acc / ns                                     # mean instantaneous vx [m/s]
    dist = rn.d.qpos[0] - x0
    row = dict(cmd=vx, measured=round(float(v), 3), err=round(abs(v - vx), 3),
               dist=round(float(dist), 2), roll=round(rn.roll(), 1),
               pitch=round(rn.pitch(), 1))
    run_rows.append(row)
    print("   %4.1f  |  %6.2f  | %5.2f |  %6.2f m | %5.1f %5.1f"
          % (vx, v, abs(v - vx), row["dist"], row["roll"], row["pitch"]))
rep["run"] = run_rows

print("\n=== B 小陀螺 / gyro ladder (body-frame yaw rate, 6 s each) ===")
print("  cmd wz | measured | revs | roll  pitch")
gyro_rows = []
for wz in (2.0, 3.0, 4.5, 6.0, -6.0):
    rn.reset()
    rn.step(n=1500)
    acc = 0.0; mx_r = 0.0; mx_p = 0.0
    for _ in range(120):
        rn.step(cmd=(0.0, wz), n=50)
        acc += rn.d.qvel[5] * 0.05
        mx_r = max(mx_r, abs(rn.roll())); mx_p = max(mx_p, abs(rn.pitch()))
    row = dict(cmd=wz, measured=round(acc / 6.0, 3), revs=round(acc / (2 * math.pi), 2),
               roll=round(mx_r, 1), pitch=round(mx_p, 1))
    gyro_rows.append(row)
    print("   %+5.1f  |  %+6.2f  | %5.2f | %5.1f %5.1f" % (wz, row["measured"], row["revs"], mx_r, mx_p))
rep["gyro"] = gyro_rows

print("\n=== C 跳 / jump ladder (contact ground truth) ===")
print("  target | peak rise | vz_max | air time | landed")
jump_rows = []
for rise in (0.04, 0.06, 0.08, 0.10):
    rn.reset()
    rn.step(n=3000)                                   # 3 s standing
    z0 = rn.d.qpos[2]
    peak = z0; vz = 0.0; air = 0.0
    for _ in range(320):                              # 1.6 s with the flag raised
        rn.step(jump=1.0, n=5)
        peak = max(peak, rn.d.qpos[2]); vz = max(vz, rn.d.qvel[2])
        if not rn.wheels_down():
            air += 0.005
    for _ in range(400):                              # 2 s recovery, flag off
        rn.step(n=5)
    ok = abs(rn.pitch()) < 25 and abs(rn.roll()) < 25 and rn.wheels_down()
    row = dict(target=rise, rise_cm=round((peak - z0) * 100, 2), vz=round(vz, 2),
               air_s=round(air, 3), recovered=bool(ok))
    jump_rows.append(row)
    print("   %.2f m |   %5.1f cm | %5.2f |  %5.3f s | %s"
          % (rise, row["rise_cm"], vz, air, "yes" if ok else "NO"))
rep["jump"] = jump_rows

if not a.skip_field and os.path.exists(a.field_scene):
    print("\n=== D 地图穿越 / traverse the RMUC2026-derived field ===")
    rf = Runner(a.field_scene)
    rf.reset(x=0.0)
    rf.step(n=2000)
    z_start = rf.d.qpos[2]; best_x = rf.d.qpos[0]; max_z = z_start; fell = False
    for i in range(26000):                           # 26 s: enough to cross the whole set
        rf.step(cmd=(0.85, 0.0), height=0.24, n=1)
        best_x = max(best_x, rf.d.qpos[0]); max_z = max(max_z, rf.d.qpos[2])
        if i % 2000 == 0 and i:
            print("     t=%4.1f s x=%6.2f m  z=%.3f  wheel=%5.1f/%5.1f rad/s  pitch=%5.1f  ncon=%d"
                  % (i * 0.001, rf.d.qpos[0], rf.d.qpos[2], rf.d.qvel[rf.va["left_wheel_joint"]],
                     rf.d.qvel[rf.va["right_wheel_joint"]], rf.pitch(), len(rf.d.contact)))
        if rf.d.qpos[2] < -0.35 or abs(rf.pitch()) > 50:
            fell = True; break
    row = dict(distance_m=round(best_x, 2), rise_on_field_m=round(max_z - z_start, 3),
               survived=not fell, final_pitch=round(rf.pitch(), 1))
    print("   travelled %.2f m, climbed %.1f cm, %s (final pitch %.1f deg)"
          % (row["distance_m"], row["rise_on_field_m"] * 100,
             "SURVIVED" if row["survived"] else "fell", row["final_pitch"]))
    rep["field"] = row

best_run = max([r for r in run_rows], key=lambda r: r["measured"] if r["err"] < 0.6 else -1)
print("\nSUMMARY  run %.2f m/s (err %.2f) | gyro %.2f rad/s = %.1f rev/6 s | jump %.1f cm, %.3f s airborne"
      % (best_run["measured"], best_run["err"],
         max(abs(g["measured"]) for g in gyro_rows),
         max(abs(g["revs"]) for g in gyro_rows),
         max(j["rise_cm"] for j in jump_rows), max(j["air_s"] for j in jump_rows)))
json.dump(rep, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote", a.out)
