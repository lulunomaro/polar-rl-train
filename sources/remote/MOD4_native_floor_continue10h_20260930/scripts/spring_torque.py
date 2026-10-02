import sys, os, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:/claude2/fangzhen'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from leg2d import Kite2D, CAD
L = Kite2D(CAD, 'ours')
K, PRELOAD, L0 = 6000.0, 350.0, L.Lspr0 - 350.0 / 6000.0
print('spring: installed length L0=%.2f mm, free length %.2f mm, k=%.0f N/m' % (L.Lspr0, 1000 * L0, K))
def torques(th, tc, h=1e-5):
    def Llen(th, tc):
        q = L.qpos_full(th, tc)
        return None if q is None else q['pts']['spring']
    out = []
    for i, base in enumerate((th, tc)):
        a = Llen(*(base - [th, tc][i] + 0 for _ in [0]) ) if False else None
    a1 = Llen(th - h, tc); a2 = Llen(th + h, tc); b1 = Llen(th, tc - h); b2 = Llen(th, tc + h)
    if None in (a1, a2, b1, b2): return None
    F = K * (Llen(th, tc) - L0) / 1000.0        # N of thrust (positive = extending)
    dLdth = (a2 - a1) / (2 * h) / 1000.0        # m/rad
    dLdtc = (b2 - b1) / (2 * h) / 1000.0
    return F, -F * dLdth, -F * dLdtc, Llen(th, tc)
print()
print('  thigh  crank |  spring len   thrust F |  tau_thigh  tau_crank | |tau| vs 40 N*m limit')
for th, tc in ((0.0, 0.0), (0.097, 0.222), (0.117, 0.230), (0.2, 0.2), (0.0, 0.3),
               (0.3, 0.0), (-0.3, 0.0), (0.0, -0.3), (0.5, 0.5), (1.0, 1.0), (-0.5, 0.5)):
    r = torques(th, tc)
    if r is None: print('   chain cannot close'); continue
    F, tt, tcq, ln = r
    print('  %+5.2f %+5.2f | %8.2f mm  %7.1f N |  %+7.2f   %+7.2f |  %s'
          % (th, tc, ln, F, tt, tcq, 'OVER 40' if max(abs(tt), abs(tcq)) > 40 else 'ok'))
print()
print('== where can the 40 N*m hip motors hold the spring? scan ==')
best = []
for th in np.arange(-1.2, 1.21, 0.05):
    for tc in np.arange(-1.2, 1.21, 0.05):
        r = torques(th, tc)
        if r is None: continue
        F, tt, tcq, ln = r
        if abs(tt) < 25 and abs(tcq) < 25:
            best.append((abs(tt) + abs(tcq), th, tc, ln, F, tt, tcq))
best.sort()
print('   poses with both hip torques < 25 N*m: %d' % len(best))
for b in best[:8]:
    print('   th=%+.2f tc=%+.2f  spring %.1f mm  F=%.0f N  tau_thigh=%+.1f tau_crank=%+.1f' % (b[1], b[2], b[3], b[4], b[5], b[6]))
