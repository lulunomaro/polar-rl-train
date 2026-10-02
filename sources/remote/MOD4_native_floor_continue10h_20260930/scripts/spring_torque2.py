import sys, os, numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:/claude2/fangzhen'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from leg2d import Kite2D, CAD, wrap
L = Kite2D(CAD, 'ours')
K, SPRINGREF = 6000.0, 0.0583333
FOLD = wrap(np.arctan2(CAD['P2'][1], CAD['P2'][0]) - np.arctan2(CAD['P1'][1], CAD['P1'][0]))
print('kite fold at thigh-crank = %+.4f rad (%.1f deg)' % (FOLD, np.degrees(FOLD)))
def Llen(th, tc):
    q = L.qpos_full(th, tc)
    return None if q is None else q['pts']['spring']
def tau(th, tc, h=1e-5):
    ln = Llen(th, tc)
    if ln is None: return None
    a1 = Llen(th - h, tc); a2 = Llen(th + h, tc); b1 = Llen(th, tc - h); b2 = Llen(th, tc + h)
    if None in (a1, a2, b1, b2): return None
    q = (ln - L.Lspr0) / 1000.0
    F = K * (SPRINGREF - q)                      # N of extension thrust
    dth = (a2 - a1) / (2 * h) / 1000.0           # m/rad
    dtc = (b2 - b1) / (2 * h) / 1000.0
    return ln, q, F, F * dth, F * dtc
print()
print('  thigh  crank    delta |  spring mm   q mm    F N | tau_thigh tau_crank | knee(rad)')
for th, tc in ((0.0, 0.0), (0.097, 0.222), (0.3, 0.0), (0.6, 0.0), (0.9, 0.0), (1.2, 0.0),
               (1.5, 0.0), (1.8, 0.0), (2.0, 0.0), (2.2, 0.0), (2.4, 0.0), (2.5, 0.0),
               (2.53, 0.0), (-0.6, 0.0), (-1.2, 0.0), (-1.8, 0.0)):
    r = tau(th, tc)
    if r is None:
        print('  %+5.2f %+5.2f  %+6.2f | chain cannot close' % (th, tc, th - tc)); continue
    ln, q, F, tt, tcq = r
    kn = L.qpos_full(th, tc)['rear2']
    print('  %+5.2f %+5.2f  %+6.2f | %8.2f %+7.2f %+7.1f | %+8.2f  %+8.2f | %+6.3f %s'
          % (th, tc, th - tc, ln, 1000 * q, F, tt, tcq, kn, 'OVER 40' if max(abs(tt), abs(tcq)) > 40 else ''))
print()
print('== tau(delta) profile: the spring drives the leg toward the fold ==')
for dl in np.arange(0.0, 2.6, 0.2):
    r = tau(dl, 0.0)
    if r is None: print('   delta %+0.2f cannot close' % dl); continue
    ln, q, F, tt, tcq = r
    print('   delta=%+0.2f  L=%7.2f mm  F=%+6.1f N  tau_thigh=%+7.2f  tau_crank=%+7.2f N*m' % (dl, ln, F, tt, tcq))
