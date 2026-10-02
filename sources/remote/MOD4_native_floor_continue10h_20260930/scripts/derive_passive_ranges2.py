import sys, os, json
import numpy as np
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'D:/claude2/fangzhen'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from leg2d import Kite2D, CAD, wrap
L = Kite2D(CAD, 'ours')
KEYS = ('rear2', 'front2', 'front3', 'front4', 'spring1')
rows = []
for th in np.arange(-np.pi, np.pi + 1e-9, np.pi / 180):
    for tc in np.arange(-np.pi, np.pi + 1e-9, np.pi / 180):
        q = L.qpos_full(th, tc)
        if q is None: continue
        r = q['pts']
        d2 = np.linalg.norm(r['knee'] - r['P3'])          # loop-2 diagonal, mm
        d1 = np.linalg.norm(r['P1'] - r['P2'])            # kite diagonal, mm
        v = dict((k, -q[k]) for k in KEYS)
        v['spring2'] = q['spring2'] / 1000.0
        v['delta'] = wrap(th - tc); v['d1'] = d1; v['d2'] = d2
        v['ext'] = r['ext']
        rows.append(v)
print('poses: %d' % len(rows))
# monotonicity of the knee vs delta
for dl in np.arange(-3.14, 3.15, 0.2):
    sel = [r for r in rows if abs(r['delta'] - dl) < 0.01]
    if not sel: print('  delta %+0.2f  (no pose)' % dl); continue
    k = np.mean([r['rear2'] for r in sel]); d2 = np.mean([r['d2'] for r in sel]); d1 = np.mean([r['d1'] for r in sel])
    print('  delta=%+0.2f  knee=%+0.3f  loop2 diag=%6.1f mm  kite diag=%6.1f mm' % (dl, k, d2, d1))
print()
print('loop2 diag range %.1f .. %.1f mm  (singular at 27.9 and 161.9)' % (min(r['d2'] for r in rows), max(r['d2'] for r in rows)))
print('kite  diag range %.1f .. %.1f mm  (singular at 0)' % (min(r['d1'] for r in rows), max(r['d1'] for r in rows)))
for lo, hi in ((45.0, 150.0), (40.0, 155.0), (50.0, 145.0)):
    sel = [r for r in rows if lo <= r['d2'] <= hi and r['d1'] >= 30.0]
    acc = dict((k, [1e9, -1e9]) for k in KEYS + ('delta', 'ext'))
    for r in sel:
        for k in acc:
            acc[k][0] = min(acc[k][0], r[k]); acc[k][1] = max(acc[k][1], r[k])
    print('guard diag in [%g,%g] and kite diag >= 30 mm: %d poses (%.1f%%)' % (lo, hi, len(sel), 100.0 * len(sel) / len(rows)))
    for k in KEYS: print('    %-8s [%+7.3f, %+7.3f]' % (k, acc[k][0], acc[k][1]))
    print('    delta    [%+7.3f, %+7.3f]   ext %.1f..%.1f mm' % (acc['delta'][0], acc['delta'][1], acc['ext'][0], acc['ext'][1]))
    s2 = [r['spring2'] for r in sel]
    print('    spring2  [%+7.4f, %+7.4f] m' % (min(s2), max(s2)))
