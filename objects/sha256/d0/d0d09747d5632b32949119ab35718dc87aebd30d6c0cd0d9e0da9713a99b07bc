import sys, os, math, numpy as np, mujoco
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:/claude2/fangzhen'
def run(plant, kp, kd, sgn, seconds=10.0, dt=0.001, hold_legs=True):
    m = mujoco.MjModel.from_xml_path(os.path.join(ROOT, plant))
    m.opt.timestep = dt
    d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, 0)
    def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
    LEG = ['left_front1_joint', 'left_rear1_joint', 'right_front1_joint', 'right_rear1_joint']
    WHE = ['left_wheel_joint', 'right_wheel_joint']
    AN = {mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}
    FR = {}
    for i in range(m.nu):
        jn = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[i, 0])
        FR[jn] = float(m.actuator_forcerange[i, 1])
    n = int(seconds / dt); worst = 0.0; zmin = 9e9; zmax = -9e9
    for k in range(n):
        d.ctrl[:] = 0.0
        if hold_legs:
            for jn in LEG:
                u = 60.0 * (0.0 - d.qpos[m.jnt_qposadr[J(jn)]]) - 2.0 * d.qvel[m.jnt_dofadr[J(jn)]]
                d.ctrl[AN[jn.replace('_joint', '_ctrl')]] = float(np.clip(u, -FR[jn], FR[jn]))
        # pitch from the base orientation
        R = d.xmat[1].reshape(3, 3)
        gv = R.T @ np.array([0.0, 0.0, -1.0])
        pitch = math.asin(np.clip(gv[0], -1, 1))
        rate = d.qvel[4]
        u = sgn * (kp * pitch + kd * rate)
        for jn in WHE:
            d.ctrl[AN[jn.replace('_joint', '_ctrl')]] = float(np.clip(u, -FR[jn], FR[jn]))
        mujoco.mj_step(m, d)
        worst = max(worst, abs(math.degrees(pitch))); zmin = min(zmin, d.qpos[2]); zmax = max(zmax, d.qpos[2])
        if abs(math.degrees(pitch)) > 45.0: return dict(fell=k * dt, worst=worst, zmin=zmin, zmax=zmax)
    return dict(fell=-1.0, worst=worst, zmin=zmin, zmax=zmax)
for plant in ('robot/out_cc/scene_cc.xml', 'robot/out_cc_linkfix/scene_cc.xml'):
    print('==', plant)
    best = None
    for sgn in (+1, -1):
        for kp in (10, 30, 60, 120, 250):
            for kd in (2, 6, 12, 25, 50):
                r = run(plant, kp, kd, sgn, seconds=6.0)
                if r['fell'] < 0 and (best is None or r['worst'] < best[1]['worst']):
                    best = ((sgn, kp, kd), r)
    if best is None:
        print('   NO (kp,kd,sign) in the grid kept it upright for 6 s')
        for sgn in (+1, -1):
            r = run(plant, 120, 25, sgn, seconds=6.0)
            print('   sign %+d kp=120 kd=25 -> fell at %.2f s, worst tilt %.1f deg, z %.3f..%.3f'
                  % (sgn, r['fell'], r['worst'], r['zmin'], r['zmax']))
    else:
        (sgn, kp, kd), r = best
        print('   STANDS 6 s with sign %+d kp=%g kd=%g : worst tilt %.2f deg, z %.3f..%.3f'
              % (sgn, kp, kd, r['worst'], r['zmin'], r['zmax']))
