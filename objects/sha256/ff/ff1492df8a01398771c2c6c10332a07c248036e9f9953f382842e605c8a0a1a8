# LINKAGE AUDIT: MJCF closed chain vs the validated analytic kite four-bar.
#  A. pin geometry at qpos0 (XML bodies + connect anchors) vs leg2d.CAD
#  B. does the MJCF reproduce the analytic solution over the workspace (equality gap)?
#  C. are the XML joint RANGES consistent with the mechanism, or do they clip it?
#  D. transmission ratio crank -> shank, similarity ratio
import sys, os, json, math
import numpy as np, mujoco
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:/claude2/fangzhen'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from leg2d import Kite2D, CAD, REF

XML = os.path.join(ROOT, 'robot/out_cc/rm_vehicle_cc.xml')
m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
L = Kite2D(CAD, 'ours')

def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
def B(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
qa = lambda n: m.jnt_qposadr[J(n)]
SIDE = 'left'
KEYS = ('rear1', 'front1', 'rear2', 'front2', 'front3', 'front4', 'spring1', 'spring2')
adr = dict((k, qa('%s_%s_joint' % (SIDE, k))) for k in KEYS)
lim = dict((k, m.jnt_range[J('%s_%s_joint' % (SIDE, k))]) for k in KEYS)

print('== A. pins at qpos0: XML vs CAD (mm, hip-relative, leg plane x-z) ==')
mujoco.mj_resetData(m, d); mujoco.mj_forward(m, d)
hip = d.xpos[B(SIDE + '_rear1')][[0, 2]] * 1000.0
def pin_global(body, local):
    b = B(body)
    return (d.xpos[b] + d.xmat[b].reshape(3, 3) @ np.asarray(local, float))[[0, 2]] * 1000.0
def org(name):
    return d.xpos[B(name)][[0, 2]] * 1000.0
rows = []
rows.append(('knee', org(SIDE + '_rear2'), CAD['knee'] + hip))
rows.append(('axle', org(SIDE + '_wheel'), CAD['axle'] + hip))
rows.append(('P2', org(SIDE + '_front2'), CAD['P2'] + hip))
rows.append(('APEX', org(SIDE + '_front3'), CAD['apex'] + hip))
rows.append(('P3', org(SIDE + '_front4'), CAD['P3'] + hip))
rows.append(('S1', org(SIDE + '_spring1'), CAD['S1'] + hip))
for e in range(m.neq):
    n1 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.eq_obj1id[e])
    if not n1.startswith(SIDE): continue
    ed = np.asarray(m.eq_data[e])
    nm = {SIDE + '_front3': 'P1', SIDE + '_front4': 'Q', SIDE + '_spring2': 'S2'}[n1]
    rows.append((nm, pin_global(n1, ed[0:3]), CAD[nm] + hip))
worst = 0.0
for nm, got, want in rows:
    dev = got - want
    worst = max(worst, np.abs(dev).max())
    print('   %-5s xml=(%8.2f,%8.2f)  cad=(%8.2f,%8.2f)  dev=(%+.3f,%+.3f)'
          % (nm, got[0], got[1], want[0], want[1], dev[0], dev[1]))
print('   worst pin deviation = %.3f mm -> %s' % (worst, 'OK' if worst < 1.0 else 'MISMATCH'))
print('   lengths: crank=%.2f thigh=%.2f shank=%.2f coupler(P2-A)=%.2f (A-P1)=%.2f R3=%.2f L4=%.2f Rq=%.2f'
      % (L.r_c, L.a, L.b, L.L2, L.L3, L.R3, L.L4, L.Rq))
print('   similarity lambda=r_c/thigh=%.4f (SJTU 0.1134/0.21=%.4f)  kite r_P1/r_c=%.4f'
      % (L.r_c / L.a, 0.1134 / 0.21, L.r_p1 / L.r_c))
json.dump(dict(lim=dict((k, list(v)) for k, v in lim.items())), open(os.path.join(ROOT, 'docs/audit/_audit_lim.json'), 'w'))

# ---------------------------------------------------------------- B. workspace closure
# MuJoCo hinges about +Y, leg2d angles are measured x->z, so qpos_MJ = -qpos_analytic.
print()
print('== B. MJCF vs analytic over the driven workspace (equality gap, mm) ==')
HINGES = ('rear1', 'front1', 'rear2', 'front2', 'front3', 'front4', 'spring1')
def pose_q(th, tc):
    q = L.qpos_full(th, tc)
    if q is None: return None
    v = dict((k, -q[k]) for k in HINGES)
    return v, q
def apply(v, sgn2):
    mujoco.mj_resetData(m, d)
    for k in HINGES: d.qpos[adr[k]] = v[k]
    d.qpos[adr['spring2']] = sgn2 * v['s2']
    mujoco.mj_forward(m, d)
    gaps = []
    for e in range(m.neq):
        o1, o2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e])
        ed = np.asarray(m.eq_data[e])
        a1 = d.xpos[o1] + d.xmat[o1].reshape(3, 3) @ ed[0:3]
        a2 = d.xpos[o2] + d.xmat[o2].reshape(3, 3) @ ed[3:6]
        gaps.append(1000.0 * np.linalg.norm(a1 - a2))
    return np.array(gaps)
for sgn2 in (+1.0, -1.0):
    v, q = pose_q(0.3, 0.4); v['s2'] = (q['spring2']) / 1000.0
    print('   spring2 sign %+d -> left gaps %s mm' % (sgn2, np.round(apply(v, sgn2)[:3], 5)))
def s2val(q): return (q['spring2']) / 1000.0
g_p = apply(dict(pose_q(0.3, 0.4)[0], s2=s2val(pose_q(0.3, 0.4)[1])), +1.0)[2]
g_n = apply(dict(pose_q(0.3, 0.4)[0], s2=s2val(pose_q(0.3, 0.4)[1])), -1.0)[2]
SGN2 = +1.0 if g_p < g_n else -1.0
print('   chosen spring2 sign = %+d (gap %s vs %s mm)' % (SGN2, min(g_p, g_n), max(g_p, g_n)))
TH = np.arange(-1.30, 1.301, 0.05)
TC = np.arange(-1.30, 1.301, 0.05)
worst = 0.0; nok = 0; ntot = 0
for th in TH:
    for tc in TC:
        r = pose_q(th, tc)
        if r is None: continue
        ntot += 1
        g = apply(dict(r[0], s2=s2val(r[1])), SGN2).max()
        worst = max(worst, g); nok += (g < 0.01)
print('   poses closing to <0.01 mm: %d/%d ; worst gap = %.5f mm' % (nok, ntot, worst))

# ---------------------------------------------------------------- C. limit clipping
print()
print('== C. XML joint ranges vs the mechanism ==')
def rng(k):
    lo, hi = lim[k]
    if lo == 0.0 and hi == 0.0: return -1e9, 1e9      # autolimits: no range = unlimited
    return lo, hi
for k in KEYS:
    lo, hi = rng(k)
    print('   %-8s XML [%s]' % (k, 'unlimited' if hi > 1e8 else '%+.3f, %+.3f' % (lo, hi)))
need = dict((k, [1e9, -1e9]) for k in KEYS)
viol = dict((k, 0) for k in KEYS); over = dict((k, 0.0) for k in KEYS)
inside = 0
for th in TH:
    for tc in TC:
        r = pose_q(th, tc)
        if r is None: continue
        v = dict(r[0]); v['spring2'] = SGN2 * s2val(r[1])
        bad = False
        for k in KEYS:
            need[k][0] = min(need[k][0], v[k]); need[k][1] = max(need[k][1], v[k])
            lo, hi = rng(k)
            if v[k] < lo - 1e-9 or v[k] > hi + 1e-9:
                viol[k] += 1; over[k] = max(over[k], max(lo - v[k], v[k] - hi)); bad = True
        if not bad: inside += 1
print('   driven poses fully inside the XML limits: %d/%d (%.1f%%)' % (inside, ntot, 100.0 * inside / ntot))
print('   %-8s %24s %20s %s' % ('joint', 'needed (mechanism)', 'XML limit', 'clipped'))
for k in KEYS:
    lo, hi = rng(k)
    print('   %-8s [%+8.3f, %+8.3f]  %s  %5d  max over %.3f rad'
          % (k, need[k][0], need[k][1], ('unlimited' if hi > 1e8 else '[%+7.3f,%+7.3f]' % (lo, hi)), viol[k], over[k]))

# ---------------------------------------------------------------- D. trained stance
print()
print('== D. trained stance / height band ==')
for (f1, r1, tag) in ((0.222, 0.097, 'left '), (0.230, 0.117, 'right')):
    v, q = pose_q(r1, f1)
    v = dict(v); v['spring2'] = SGN2 * s2val(q)
    print('   %s thigh=%+.3f crank=%+.3f -> ext %.1f mm, axle %.1f mm below hip, gap %.4f mm'
          % (tag, r1, f1, q['pts']['ext'], -q['pts']['axle'][1], apply(dict(v, s2=v['spring2']), SGN2).max()))
    for k in KEYS:
        lo, hi = rng(k)
        if hi > 1e8: continue
        margin = min(v[k] - lo, hi - v[k])
        print('       %-8s %+8.4f  XML [%+.3f,%+.3f]  margin %+.4f%s' % (k, v[k], lo, hi, margin, '   <-- TIGHT' if margin < 0.08 else ''))
