"""Derive the REAL hip travel from the linkage geometry, not from a guess.

Kite2D.solve() returns None exactly when the similar-link four-bar cannot close (the
thigh/shank fold out, or the coupler crosses a dead centre).  Scanning that boundary gives
the true mechanical workspace of the two hip-axis drives, which is what a 机械限位 can sit
against.  Everything outside it is physically impossible for this leg.
"""
import os, sys
import numpy as np
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD

L = Kite2D(CAD, "ws")
G = np.deg2rad
grid = np.arange(-np.pi, np.pi + 1e-9, G(1.0))
ok = np.zeros((len(grid), len(grid)), bool)
for i, th in enumerate(grid):
    for j, cr in enumerate(grid):
        ok[i, j] = L.qpos_full(th, cr) is not None
print("closure map %dx%d at 1 deg, %d of %d pose pairs close" %
      (len(grid), len(grid), ok.sum(), ok.size))

print("\n== thigh travel, over all crank angles that close ==")
rows = []
for i, th in enumerate(grid):
    if ok[i].any():
        rows.append((th, ok[i].sum()))
if rows:
    lo = min(r[0] for r in rows); hi = max(r[0] for r in rows)
    print("   thigh  reachable from %+7.3f to %+7.3f rad  (%+.1f deg .. %+.1f deg)" %
          (lo, hi, np.degrees(lo), np.degrees(hi)))
print("== crank travel, per held thigh angle (the knee-drive stroke) ==")
for th_deg in (-40, -20, 0, 20, 40, 60):
    i = int(round((G(th_deg) + np.pi) / G(1.0)))
    if 0 <= i < len(grid) and ok[i].any():
        cols = np.where(ok[i])[0]
        # contiguous?
        a, b = grid[cols[0]], grid[cols[-1]]
        print("   thigh %+4d deg -> crank %+7.3f .. %+7.3f rad (%+6.1f .. %+6.1f deg), "
              "%d of %d deg closed, contiguous=%s" %
              (th_deg, a, b, np.degrees(a), np.degrees(b), len(cols), len(grid),
               bool(np.all(np.diff(cols) == 1))))
print("\n== thigh travel, per held crank angle ==")
for cr_deg in (-40, -20, 0, 20, 40, 60):
    j = int(round((G(cr_deg) + np.pi) / G(1.0)))
    if 0 <= j < len(grid) and ok[:, j].any():
        rs = np.where(ok[:, j])[0]
        a, b = grid[rs[0]], grid[rs[-1]]
        print("   crank %+4d deg -> thigh %+7.3f .. %+7.3f rad (%+6.1f .. %+6.1f deg), "
              "%d of %d deg closed, contiguous=%s" %
              (cr_deg, a, b, np.degrees(a), np.degrees(b), len(rs), len(grid),
               bool(np.all(np.diff(rs) == 1))))
# stance height across the closure set: what does the leg actually reach?
best = (9e9, -9e9)
for th in np.arange(-np.pi, np.pi, G(2.0)):
    for cr in np.arange(-np.pi, np.pi, G(2.0)):
        q = L.qpos_full(th, cr)
        if q is None:
            continue
        d = -q["pts"]["axle"][1]
        best = (min(best[0], d), max(best[1], d))
print("\nhip->axle distance across the whole closable workspace: %.1f .. %.1f mm"
      "   (thigh %.1f + shank %.1f = %.1f mm fully folded/extended)" %
      (best[0], best[1], np.linalg.norm(CAD["knee"]),
       np.linalg.norm(CAD["axle"] - CAD["knee"]),
       np.linalg.norm(CAD["knee"]) + np.linalg.norm(CAD["axle"] - CAD["knee"])))