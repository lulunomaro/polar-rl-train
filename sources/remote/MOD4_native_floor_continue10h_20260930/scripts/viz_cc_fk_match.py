"""Prove the browser viewer's FK now equals MuJoCo's FK for the same qpos."""
import json, os, sys
sys.path.insert(0, r'D:/claude2/fangzhen/scripts')
import numpy as np, mujoco
from viz_cc_render import body_frames
ROOT = r'D:/claude2/fangzhen'; VIZ = os.path.join(ROOT, 'docs/viz')
M = json.load(open(os.path.join(VIZ, 'model.json'), encoding='utf-8'))
m = mujoco.MjModel.from_xml_path(os.path.join(ROOT, 'robot/out_cc_linkfix/scene_cc.xml'))
d = mujoco.MjData(m)
names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
MJ = {}
for b in range(m.nbody):
    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b)
    if nm: MJ[nm] = b
worst_all = 0.0
for pi in (0, 1, 2, 3, 4, 5):
    q = M['poses'][pi]['q']
    d.qpos[:] = 0
    d.qpos[0:7] = q['__root__']
    for k, v in q.items():
        if k in names:
            d.qpos[m.jnt_qposadr[names.index(k)]] = v
    mujoco.mj_forward(m, d)
    W = body_frames(M, q)
    errs = []
    for b in M['bodies']:
        j = MJ.get(b['name'])
        if j is None: continue
        e = np.linalg.norm(W[b['id']][:3, 3] - d.xpos[j])
        errs.append((e, b['name']))
    errs.sort(reverse=True)
    worst_all = max(worst_all, errs[0][0])
    print(f"pose {pi} {M['poses'][pi]['label'][:34]:36s} worst |viewer-MJCF| = {errs[0][0]*1000:8.4f} mm on {errs[0][1]}"
          f"   (2nd {errs[1][0]*1000:.4f} mm on {errs[1][1]})")
print()
print('worst over all poses: %.4f mm ->' % (worst_all*1000), 'MATCH' if worst_all < 1e-6 else 'MISMATCH')
