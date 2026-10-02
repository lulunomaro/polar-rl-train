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
wb = {B("left_wheel"), B("right_wheel")}
def touching():
    for g in d.contact:
        if m.geom_bodyid[g.geom1] in wb or m.geom_bodyid[g.geom2] in wb: return True
    return False
def trial(crouch, push, th_c, th_p, kp, kd, eff, t_push=0.30, t_crouch=0.7):
    mujoco.mj_resetDataKeyframe(m, d, 0); d.qvel[:] = 0
    def hold(tc, tt, n):
        for _ in range(n):
            for nm in LEG:
                tgt = tt if "rear" in nm else tc
                d.qfrc_applied[va[nm]] = float(np.clip(kp*(tgt-d.qpos[qa[nm]]) - kd*d.qvel[va[nm]], -eff, eff))
            for nm in WHL: d.qfrc_applied[va[nm]] = float(np.clip(1.5*(0.0-d.qvel[va[nm]]), -10, 10))
            mujoco.mj_step(m, d)
    hold(0,0,900); zs = float(d.qpos[2])
    hold(crouch, th_c, int(t_crouch/0.001))
    hold(push, th_p, int(t_push/0.001))
    pk = float(d.qpos[2]); air = 0.0; vz = 0.0
    for _ in range(1500):
        for nm in LEG:
            d.qfrc_applied[va[nm]] = float(np.clip(kp*(push-d.qpos[qa[nm]]) - kd*d.qvel[va[nm]], -eff, eff))
        for nm in WHL: d.qfrc_applied[va[nm]] = float(np.clip(1.5*(0.0-d.qvel[va[nm]]), -10, 10))
        mujoco.mj_step(m, d)
        pk = max(pk, float(d.qpos[2])); vz = max(vz, float(d.qvel[2]))
        if not touching(): air += 0.001
    return (pk-zs)*100, air*1000, vz
print(" gains            best rise  air(ms)  vz_max   (sweeping crouch/push/thigh)")
for kp, kd, eff, note in ((60,2,30.0,"v4/v5 现状"), (60,2,50.9,"部署合同 ±50.9"), (80,3,50.9,"合同+稍高 kp"), (120,4,54.0,"参考 MJCF ±54")):
    best = (0,0,0); arg = None
    for crouch in (-0.45,-0.6,-0.75,-0.9):
        for push in (0.6,0.75,0.9,1.05,1.2):
            for th_c, th_p in ((0,0),(0.3,-0.3),(0.5,-0.5),(0.6,-0.6)):
                r = trial(crouch, push, th_c, th_p, kp, kd, eff)
                if r[1] > best[1] or (r[1] == best[1] and r[0] > best[0]):
                    best = r; arg = (crouch, push, th_c, th_p)
    print("  kp=%-3d eff=%-5.1f %-12s -> rise %5.1f cm  air %5.0f ms  vz %4.2f m/s   (crouch %+.2f push %+.2f thigh %+.1f->%+.1f)"
          % (kp, eff, note, best[0], best[1], best[2], *arg))
