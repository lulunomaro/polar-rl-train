
# Render any MJCF to a PNG with MuJoCo, holding the actuated joints at the model's own neutral
# (qpos0) or keyframe, with the wheels auto-dropped onto the floor.  Used to eyeball orientation
# (is the leg upside down?) after any MJCF -> USD round trip.
import argparse, math, os, time
import numpy as np
import mujoco

ap = argparse.ArgumentParser()
ap.add_argument('--xml', required=True)
ap.add_argument('--png', required=True)
ap.add_argument('--steps', type=int, default=60)
ap.add_argument('--kp', type=float, default=400.0)
ap.add_argument('--kd', type=float, default=20.0)
ap.add_argument('--dist', type=float, default=1.6)
ap.add_argument('--az', type=float, default=-38.0)
ap.add_argument('--el', type=float, default=-10.0)
ap.add_argument('--width', type=int, default=1000)
ap.add_argument('--px', type=int, default=640)
a = ap.parse_args()

m = mujoco.MjModel.from_xml_path(a.xml)
m.vis.global_.offwidth = a.width
m.vis.global_.offheight = a.px
d = mujoco.MjData(m)
if m.nkey > 0:
    mujoco.mj_resetDataKeyframe(m, d, 0)
    src = 'keyframe 0'
else:
    d.qpos[:] = m.qpos0
    d.qvel[:] = 0.0
    src = 'qpos0'
mujoco.mj_forward(m, d)
# auto-z: drop the base until the lowest wheel/tire collider touches z=0
wheels = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n) for n in
          ('left_wheel', 'right_wheel', 'left_wheel_spin', 'right_wheel_spin')]
wheels = [w for w in wheels if w >= 0]
if wheels:
    az = min(d.xpos[w][2] for w in wheels)
    wr = 0.0
    for g in range(m.ngeom):
        if m.geom_bodyid[g] in wheels and m.geom_type[g] in (2, 5):   # sphere / cylinder
            wr = max(wr, float(m.geom_size[g][0]))
    if wr > 0:
        d.qpos[2] -= (az - wr)
        mujoco.mj_forward(m, d)
    print('wheel radius %.4f m, axle now at z=%.4f' % (wr, min(d.xpos[w][2] for w in wheels)))
adr = []
for i in range(m.nu):
    jid = int(m.actuator_trnid[i, 0])
    adr.append((i, m.jnt_qposadr[jid], m.jnt_dofadr[jid], mujoco.mj_id2name(m, 5, i)))
q0 = d.qpos.copy()
for k in range(a.steps):
    for i, qa, da, nm in adr:
        if 'wheel' in (nm or ''):
            d.ctrl[i] = -0.05 * d.qvel[da]
        else:
            d.ctrl[i] = a.kp * (q0[qa] - d.qpos[qa]) - a.kd * d.qvel[da]
    mujoco.mj_step(m, d)
print('source=%s  base z=%.4f  pitch=%+.2f deg' % (
    src, d.qpos[2], math.degrees(math.asin(max(-1, min(1, 2 * (d.qpos[3] * d.qpos[5] - d.qpos[6] * d.qpos[4])))))))
for n in ('chassis', 'base_link', 'left_thigh', 'left_shin', 'left_wheel'):
    b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
    if b >= 0:
        print('   %-12s world z %.4f  xyz %s' % (n, d.xpos[b][2], np.round(d.xpos[b], 3)))
r = mujoco.Renderer(m, height=a.px, width=a.width)
cam = mujoco.MjvCamera()
cam.type = mujoco.mjtCamera.mjCAMERA_FREE
cam.lookat[:] = [d.qpos[0], 0.0, max(0.15, d.qpos[2] * 0.55)]
cam.distance = a.dist
cam.azimuth = a.az
cam.elevation = a.el
r.update_scene(d, camera=cam)
from PIL import Image
Image.fromarray(r.render()).save(a.png)
print('wrote', a.png)
r.close()
