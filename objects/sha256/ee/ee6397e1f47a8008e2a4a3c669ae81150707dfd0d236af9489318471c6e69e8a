import sys, os, numpy as np, mujoco, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:/claude2/fangzhen'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from leg2d import Kite2D, CAD, wrap
VAR = os.path.join(ROOT, 'robot/out_cc_linkfix/rm_vehicle_cc.xml')
OLD = os.path.join(ROOT, 'robot/out_cc/rm_vehicle_cc.xml')
L = Kite2D(CAD, 'ours')
for tag, path in (('BASELINE', OLD), ('LINKFIX', VAR)):
    m = mujoco.MjModel.from_xml_path(path)
    d = mujoco.MjData(m)
    print('== %s: nq=%d nv=%d nu=%d neq=%d ntendon=%d' % (tag, m.nq, m.nv, m.nu, m.neq, m.ntendon))
    for t in range(m.ntendon):
        print('   tendon %d limited=%s range=%s' % (t, m.tendon_limited[t], m.tendon_range[t]))
    rows = []
    for j in range(m.njnt):
        n = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j)
        if n.startswith('left_') and not n.startswith('left_rear1') and not n.startswith('left_front1') and not n.startswith('left_wheel'):
            lo, hi = m.jnt_range[j]
            rows.append((n, lo, hi))
    print('   passive ranges: ' + ', '.join('%s[%+.3f,%+.3f]' % (n.replace('_joint','').replace('left_',''), lo, hi) for n, lo, hi in rows))
# ---- the real test: over the tendon-legal workspace, does any passive joint get clipped?
m = mujoco.MjModel.from_xml_path(VAR); d = mujoco.MjData(m)
def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
KEYS = ('rear2', 'front2', 'front3', 'front4', 'spring1', 'spring2')
adr = dict((k, m.jnt_qposadr[J('left_%s_joint' % k)]) for k in KEYS)
lim = dict((k, m.jnt_range[J('left_%s_joint' % k)]) for k in KEYS)
tlo, thi = m.tendon_range[0]
print()
print('== sweep the FULL 360x360 driven workspace against the LINKFIX stops ==')
n = 0; nlegal = 0; clip = dict((k, 0) for k in KEYS); need = dict((k, [1e9, -1e9]) for k in KEYS)
gap_worst = 0.0
for th in np.arange(-np.pi, np.pi + 1e-9, np.pi / 120):
    for tc in np.arange(-np.pi, np.pi + 1e-9, np.pi / 120):
        n += 1
        q = L.qpos_full(th, tc)
        if q is None: continue
        dmj = (-th) - (-tc)                       # MJCF q_rear1 - q_front1
        if dmj < tlo or dmj > thi: continue       # the tendon stops it: never reaches the chain
        nlegal += 1
        vals = dict((k, -q[k]) for k in ('rear2', 'front2', 'front3', 'front4', 'spring1'))
        vals['spring2'] = q['spring2'] / 1000.0
        for k in KEYS:
            need[k][0] = min(need[k][0], vals[k]); need[k][1] = max(need[k][1], vals[k])
            if vals[k] < lim[k][0] - 1e-9 or vals[k] > lim[k][1] + 1e-9: clip[k] += 1
        for k in KEYS: d.qpos[adr[k]] = vals[k]
        d.qpos[m.jnt_qposadr[J('left_rear1_joint')]] = -th
        d.qpos[m.jnt_qposadr[J('left_front1_joint')]] = -tc
        mujoco.mj_forward(m, d)
        for e in range(m.neq):
            o1 = int(m.eq_obj1id[e]); o2 = int(m.eq_obj2id[e]); ed = np.asarray(m.eq_data[e])
            if not mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, o1).startswith('left'): continue
            a1 = d.xpos[o1] + d.xmat[o1].reshape(3, 3) @ ed[0:3]
            a2 = d.xpos[o2] + d.xmat[o2].reshape(3, 3) @ ed[3:6]
            gap_worst = max(gap_worst, 1000 * np.linalg.norm(a1 - a2))
print('   poses: %d total, %d inside the tendon stop (%.1f%%)' % (n, nlegal, 100.0 * nlegal / n))
print('   worst equality gap over them: %.5f mm' % gap_worst)
for k in KEYS:
    print('   %-8s needed [%+7.3f, %+7.3f]  stop [%+7.3f, %+7.3f]  clipped poses: %d'
          % (k, need[k][0], need[k][1], lim[k][0], lim[k][1], clip[k]))
