import sys, os, json
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:/claude2/fangzhen'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from leg2d import Kite2D, CAD, wrap, ang
L = Kite2D(CAD, 'ours')
A_P1 = ang(CAD['P1']); A_P2 = ang(CAD['P2'])
fold = wrap(A_P2 - A_P1)
print('kite fold (thigh-crank alignment) at thigh-crank = %+.4f rad = %+.1f deg' % (fold, np.degrees(fold)))
print('  |hip->P1|=%.2f  |hip->P2|=%.2f  (equal -> fold exists)' % (L.r_p1, L.r_c))
# loop-2 parallelogram check
d1 = np.linalg.norm(CAD['P1'] - CAD['knee']); d2 = np.linalg.norm(CAD['P3'] - CAD['Q'])
d3 = np.linalg.norm(CAD['knee'] - CAD['Q']);  d4 = np.linalg.norm(CAD['P1'] - CAD['P3'])
print('loop2 sides: P1-knee=%.2f  Q-P3=%.2f | knee-Q=%.2f  P1-P3=%.2f  -> parallelogram=%s'
      % (d1, d2, d3, d4, abs(d1 - d2) < 0.5 and abs(d3 - d4) < 0.5))
print('  loop2 diagonal |knee-P3| must stay in [%.2f, %.2f] mm' % (abs(L.L4 - L.Rq), L.L4 + L.Rq))

KEYS = ('rear2', 'front2', 'front3', 'front4', 'spring1')
def sweep(th_lo, th_hi, tc_lo, tc_hi, guard=None, n=261):
    acc = dict((k, [1e9, -1e9]) for k in KEYS)
    ext = [1e9, -1e9]; diag = [1e9, -1e9]; ntot = 0; nok = 0; nguard = 0
    for th in np.linspace(th_lo, th_hi, n):
        for tc in np.linspace(tc_lo, tc_hi, n):
            ntot += 1
            if guard is not None and abs(wrap((th - tc) - fold)) < guard:
                nguard += 1; continue
            q = L.qpos_full(th, tc)
            if q is None: continue
            r = q['pts']
            if abs(r['loop1']) > 1e-4 or abs(r['loop2']) > 1e-4: continue
            nok += 1
            dd = np.linalg.norm(r['knee'] - r['P3'])
            diag[0] = min(diag[0], dd); diag[1] = max(diag[1], dd)
            ext[0] = min(ext[0], r['ext']); ext[1] = max(ext[1], r['ext'])
            for k in KEYS:
                v = -q[k]                       # MJCF stores the negated analytic angle
                acc[k][0] = min(acc[k][0], v); acc[k][1] = max(acc[k][1], v)
    s2 = None
    for th in np.linspace(th_lo, th_hi, n):
        for tc in np.linspace(tc_lo, tc_hi, n):
            q = L.qpos_full(th, tc)
            if q is None: continue
            if guard is not None and abs(wrap((th - tc) - fold)) < guard: continue
            v = q['spring2'] / 1000.0
            if s2 is None: s2 = [v, v]
            s2[0] = min(s2[0], v); s2[1] = max(s2[1], v)
    return acc, s2, ext, diag, nok, ntot, nguard
print()
for tag, (a, b, c, dd) in [('full 360 x 360', (-np.pi, np.pi, -np.pi, np.pi)),
                           ('task +-1.30', (-1.3, 1.3, -1.3, 1.3)),
                           ('task +-1.30 + fold guard 0.35', (-1.3, 1.3, -1.3, 1.3)),
                           ('task +-2.00 + fold guard 0.35', (-2.0, 2.0, -2.0, 2.0)),
                           ('full 360 + guard 0.35', (-np.pi, np.pi, -np.pi, np.pi))]:
    guard = 0.35 if 'guard' in tag else None
    acc, s2, ext, diag, nok, ntot, ng = sweep(a, b, c, dd, guard=guard)
    print('%-30s closed %5d/%5d (guard rejects %d)' % (tag, nok, ntot, ng))
    for k in KEYS:
        print('     %-8s [%+7.3f, %+7.3f]' % (k, acc[k][0], acc[k][1]))
    print('     %-8s [%+7.4f, %+7.4f] m' % ('spring2', s2[0], s2[1]))
    print('     leg ext %.1f..%.1f mm ; loop2 diagonal %.1f..%.1f mm' % (ext[0], ext[1], diag[0], diag[1]))
