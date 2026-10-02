
# Interactive MuJoCo viewer / offscreen capture for the RL plant (the exact MJCF v16/v17 trains on).
#   python scripts/mj_view.py                     window: robot PD-held at the stance pose
#   python scripts/mj_view.py --png p.png         offscreen capture, no window (for agents / CI)
#   python scripts/mj_view.py --pose 0            use the CAD assembly pose (qpos = 0) instead
import argparse, json, math, os, time
import numpy as np
import mujoco

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFXML = os.path.join(ROOT, 'robot', 'out_cc_linkfix', 'scene_cc.xml')
VIZJSON = os.path.join(ROOT, 'docs', 'viz', 'model.json')
HIPJ = ('left_rear1', 'left_front1', 'right_rear1', 'right_front1')
WHLJ = ('left_wheel', 'right_wheel')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xml', default=DEFXML)
    ap.add_argument('--png', default=None)
    ap.add_argument('--pose', type=int, default=1)
    ap.add_argument('--base-z', dest='base_z', type=float, default=None)
    ap.add_argument('--keyframe', action='store_true', help='use the scene keyframe (stand) instead of the analytic pose')
    ap.add_argument('--no-auto-z', dest='auto_z', action='store_false', help='do not drop the base until the wheels touch')
    ap.add_argument('--no-balance', dest='balance', action='store_false', help='pure position hold (the robot will tip over: it is a 2-wheel balancer)')
    ap.add_argument('--bp', type=float, default=3.0, help='pitch P gain (m/s per rad)')
    ap.add_argument('--br', type=float, default=1.6, help='pitch rate gain (m/s per rad/s)')
    ap.add_argument('--wk', type=float, default=6.0, help='wheel velocity PD gain (N.m per rad/s)')
    ap.add_argument('--kvx', type=float, default=1.2, help='forward velocity gain (m/s per m/s)')
    ap.add_argument('--kx', type=float, default=0.6, help='x position gain (m/s per m)')
    ap.add_argument('--ki', type=float, default=2.5, help='pitch integral gain (the CoM sits ~45 mm behind the axle, so a P-only balancer drifts back)')
    ap.add_argument('--seconds', type=float, default=4.0)
    ap.add_argument('--steps', type=int, default=0, help='fixed number of sim steps (overrides --seconds; use ~30 for a clean static shot)')
    ap.add_argument('--kp', type=float, default=60.0)
    ap.add_argument('--kd', type=float, default=2.0)
    ap.add_argument('--wkd', type=float, default=0.6)
    ap.add_argument('--width', type=int, default=1280)
    ap.add_argument('--px', type=int, default=760)
    ap.add_argument('--az', type=float, default=-35.0)
    ap.add_argument('--el', type=float, default=-12.0)
    ap.add_argument('--dist', type=float, default=1.35)
    a = ap.parse_args()

    m = mujoco.MjModel.from_xml_path(a.xml)
    m.vis.global_.offwidth = a.width
    m.vis.global_.offheight = a.px
    poses = json.load(open(VIZJSON, encoding='utf-8'))['poses']
    pose = poses[a.pose]
    d = mujoco.MjData(m)
    if a.keyframe:
        if m.nkey < 1:
            raise SystemExit('this xml has no keyframe: %s' % a.xml)
        mujoco.mj_resetDataKeyframe(m, d, 0)
        mujoco.mj_forward(m, d)
        print('  spawned on keyframe, base z=%.4f' % d.qpos[2])
    if not a.keyframe:
        r0 = pose['q'].get('__root__') or [0, 0, 0.073, 1, 0, 0, 0]
        d.qpos[:7] = r0
        for jn, val in pose['q'].items():
            if jn == '__root__':
                continue
            i = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jn)
            if i < 0:
                raise SystemExit('joint %s missing from %s' % (jn, os.path.basename(a.xml)))
            d.qpos[m.jnt_qposadr[i]] = val
        if a.base_z is not None:
            d.qpos[2] = a.base_z
        mujoco.mj_forward(m, d)
        if a.auto_z:
            wr = 0.073
            zs = [d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n + '_joint'.replace('_joint', ''))][2] for n in ()]
            ax = min(d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, 'left_wheel')][2],
                     d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, 'right_wheel')][2])
            drop = ax - wr
            d.qpos[2] -= drop
            mujoco.mj_forward(m, d)
            print('  auto-z: wheel axle was %.4f m -> base lowered %.1f mm so the tyres touch (axle %.4f m)' % (ax, drop * 1000, ax - drop))

    aid = {}
    for i in range(m.nu):
        aid[mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i)] = i
    hips = []
    for nm in HIPJ:
        j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, nm + '_joint')
        hips.append((nm + '_ctrl', m.jnt_qposadr[j], m.jnt_dofadr[j], d.qpos[m.jnt_qposadr[j]]))
    whls = [(nm + '_ctrl', m.jnt_dofadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, nm + '_joint')]) for nm in WHLJ]
    print('plant %s' % os.path.basename(a.xml))
    print('  bodies %d  joints %d  qpos %d  nu %d  geoms %d  meshes %d' % (
        m.nbody, m.njnt, m.nq, m.nu, m.ngeom, m.nmesh))
    print('  pose %d: %s' % (a.pose, pose['label']))
    print('  hip hold targets: %s' % ', '.join('%s=%+.3f' % (n.replace('_ctrl', ''), q) for n, _, _, q in hips))

    def euler_yx(q):
        w, x, y, z = q
        roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
        return roll, pitch

    iterm = [0.0]

    def hold():
        for nm, qa, da, q0 in hips:
            d.ctrl[aid[nm]] = a.kp * (q0 - d.qpos[qa]) - a.kd * d.qvel[da]
        roll, pitch = euler_yx(d.qpos[3:7])
        for nm, da in whls:
            if a.balance:
                # Segway balance: lean back (pitch<0) -> drive back; plus velocity+position feedback so it
                # holds one spot instead of cruising away on a steady lean.
                iterm[0] = max(-1.5, min(1.5, iterm[0] + pitch * m.opt.timestep))
                vref = a.bp * pitch + a.br * d.qvel[4] + a.ki * iterm[0] - a.kvx * d.qvel[0] - a.kx * d.qpos[0]
                d.ctrl[aid[nm]] = a.wk * (vref / 0.073 - d.qvel[da])
            else:
                d.ctrl[aid[nm]] = -a.wkd * d.qvel[da]

    if a.png:
        r = mujoco.Renderer(m, height=a.px, width=a.width)
        cam = mujoco.MjvCamera()
        cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        cam.lookat[:] = [-0.03, 0.0, 0.20]
        cam.distance = a.dist
        cam.azimuth = a.az
        cam.elevation = a.el
        base = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, 'base_link')
        zs = []
        n = a.steps if a.steps > 0 else None
        t_end = time.time() + a.seconds
        i = 0
        while True:
            hold()
            mujoco.mj_step(m, d)
            zs.append(d.qpos[2])
            i += 1
            if n is not None:
                if i >= n:
                    break
            elif time.time() >= t_end:
                break
        roll, ptch = euler_yx(d.qpos[3:7])
        print('  settle: base z %.4f .. %.4f m | final x %+.3f y %+.3f m | pitch %+.2f deg | |qvel| %.3f' % (
            min(zs), max(zs), d.qpos[0], d.qpos[1], np.degrees(ptch), np.abs(d.qvel).max()))
        cam.lookat[:] = d.xpos[base]
        cam.lookat[2] += 0.08
        r.update_scene(d, camera=cam)
        img = r.render()
        from PIL import Image
        Image.fromarray(img).save(a.png)
        print('  wrote %s   base z=%.4f' % (a.png, d.qpos[2]))
        r.close()
        return

    import mujoco.viewer as mv
    base = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, 'base_link')
    with mv.launch_passive(m, d) as v:
        # point the viewer camera AT the robot, otherwise you get an empty floor and think nothing loaded
        v.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        v.cam.trackbodyid = base
        v.cam.distance = 1.15
        v.cam.elevation = -14
        v.cam.azimuth = -35
        t_end = time.time() + a.seconds if a.seconds > 0 else None
        while v.is_running():
            hold()
            mujoco.mj_step(m, d)
            v.sync()
            if t_end and time.time() > t_end:
                break
    print('viewer closed')


if __name__ == '__main__':
    main()
