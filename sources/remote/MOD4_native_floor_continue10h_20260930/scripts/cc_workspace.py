"""Derive the passive-joint ranges for OUR zero-pose convention over the full
actuated workspace (both hip axes can turn 360 deg in this design).  Exact, from the
validated analytic solver -> feeds scripts/build_cc.py."""
import sys, numpy as np
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD
L = Kite2D(CAD, "ours")
keys = ("rear2", "front2", "front3", "front4", "spring1", "spring2")
acc = {k: [1e9, -1e9] for k in keys}
ext = [1e9, -1e9]; height = [1e9, -1e9]; n_ok = 0; n_tot = 0
TH = np.arange(-np.pi, np.pi + 1e-9, np.pi / 90)      # 1 deg steps, +-180 deg hip
TC = np.arange(-np.pi, np.pi + 1e-9, np.pi / 90)
for th in TH:
    for tc in TC:
        n_tot += 1
        q = L.qpos_full(th, tc)
        if q is None:
            continue
        r = q["pts"]
        if abs(r["loop1"]) > 1e-4 or abs(r["loop2"]) > 1e-4:
            continue
        n_ok += 1
        for k in keys:
            acc[k][0] = min(acc[k][0], q[k]); acc[k][1] = max(acc[k][1], q[k])
        ext[0] = min(ext[0], r["ext"]); ext[1] = max(ext[1], r["ext"])
        height[0] = min(height[0], r["axle"][1]); height[1] = max(height[1], r["axle"][1])
print("closure reachable in %d/%d driven poses (%.1f%%)" % (n_ok, n_tot, 100.0 * n_ok / n_tot))
print("leg extension |hip->axle| = %.1f .. %.1f mm ; axle height above hip = %.1f .. %.1f mm"
      % (ext[0], ext[1], height[0], height[1]))
print("\nfull-workspace passive ranges (rad) -- too generous, they include singular folds:")
for k in keys:
    print("   %-8s [%+.3f, %+.3f]" % (k, acc[k][0], acc[k][1]))

# The operating envelope that actually matters: the wheel must stay roughly under the
# hip (|axle_x| < 120 mm) and the leg must be long enough to clear the chassis.
acc2 = {k: [1e9, -1e9] for k in keys}
n2 = 0
for th in TH:
    for tc in TC:
        q = L.qpos_full(th, tc)
        if q is None: continue
        r = q["pts"]
        if abs(r["loop1"]) > 1e-4 or abs(r["loop2"]) > 1e-4: continue
        if abs(r["axle"][0]) > 120.0 or r["ext"] < 150.0: continue
        n2 += 1
        for k in keys:
            acc2[k][0] = min(acc2[k][0], q[k]); acc2[k][1] = max(acc2[k][1], q[k])
print("\nOPERATING envelope (|axle_x|<120 mm, ext>150 mm): %d poses" % n2)
for k in keys:
    print("   %-8s [%+.3f, %+.3f] rad = [%+.1f, %+.1f] deg"
          % (k, acc2[k][0], acc2[k][1], np.degrees(acc2[k][0]), np.degrees(acc2[k][1])))
print("\nrecommended MJCF PASSIVE_RNG (15%% margin, rounded outward):")
out = {}
for k, nm in (("rear2", "shank"), ("front2", "link2"), ("front3", "link3"),
              ("front4", "link4"), ("spring1", "spring1")):
    lo, hi = acc2[k]; w = hi - lo
    out[nm] = (round(lo - 0.15 * w - 0.05, 2), round(hi + 0.15 * w + 0.05, 2))
lo, hi = acc2["spring2"]
slide = (round(lo - 0.15 * (hi - lo) - 0.005, 3), round(hi + 0.15 * (hi - lo) + 0.005, 3))
for k, v in out.items(): print("   %-8s %s," % (k, v))
print("   SPRING_SLIDE %s   (m)" % (slide,))
