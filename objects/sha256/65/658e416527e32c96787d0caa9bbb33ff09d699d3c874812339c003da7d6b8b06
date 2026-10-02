import json, os, sys
import numpy as np, mujoco, PIL.Image as I
from PIL import ImageDraw
ROOT = r'D:/claude2/fangzhen'
VIZ = os.path.join(ROOT, 'docs/viz')
M = json.load(open(os.path.join(VIZ, 'model.json'), encoding='utf-8'))
for cand in ['scene_cc.xml', 'rm_vehicle_cc.xml']:
    xp = os.path.join(ROOT, 'robot/out_cc_linkfix', cand)
    if os.path.exists(xp):
        break
m = mujoco.MjModel.from_xml_path(xp)
d = mujoco.MjData(m)
print('xml', xp, 'nq', m.nq, 'nmesh', m.nmesh, 'ngeom', m.ngeom)
names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
print('joints', names)
opt = mujoco.MjvOption(); opt.geomgroup[:] = 1; opt.geomgroup[0] = 0
S = 760
r = mujoco.Renderer(m, S, S)
def shot(q, tag, az, el):
    d.qpos[:] = 0
    for k, v in q.items():
        if k == '__root__':
            d.qpos[0:7] = v
        elif k in names:
            a = m.jnt_qposadr[names.index(k)]
            d.qpos[a] = v
    mujoco.mj_forward(m, d)
    cam = mujoco.MjvCamera(); cam.lookat = [-0.05, 0, 0.24]; cam.distance = 1.25
    cam.azimuth = az; cam.elevation = el
    r.update_scene(d, camera=cam, scene_option=opt)
    im = I.fromarray(r.render())
    dr = ImageDraw.Draw(im); dr.text((8, 6), tag, fill=(255, 255, 255))
    p = os.path.join(VIZ, 'check', 'mujoco_' + tag.split()[0] + '.png')
    im.save(p)
    lo = d.geom_xpos.min(axis=0); hi = d.geom_xpos.max(axis=0)
    print(f'  {tag}: extent {np.round(hi-lo,3)} m  -> {p}')
    return p
os.makedirs(os.path.join(VIZ, 'check'), exist_ok=True)
shot(M['poses'][0]['q'], 'q0', 206, 16)
shot(M['poses'][5]['q'], 'crank', 206, 16)
shot(M['poses'][3]['q'], 'kneeup', 206, 16)
shot(M['poses'][2]['q'], 'crouch', 206, 16)
# side-by-side
ims = [I.open(os.path.join(VIZ, 'check', f'mujoco_{k}.png')) for k in ('q0', 'crank', 'kneeup', 'crouch')]
w, h = ims[0].size
out = I.new('RGB', (w*2, h*2+26), (16, 16, 20))
for i, im in enumerate(ims):
    out.paste(im, ((i % 2)*w, (i//2)*(h+13)))
ImageDraw.Draw(out).text((8, h*2+10),
    'MuJoCo renders robot/out_cc_linkfix/rm_vehicle_cc.xml - the reference the browser viewer must match',
    fill=(230, 240, 255))
out.save(os.path.join(VIZ, 'check', 'mujoco_reference.png'))
print('saved mujoco_reference.png')
