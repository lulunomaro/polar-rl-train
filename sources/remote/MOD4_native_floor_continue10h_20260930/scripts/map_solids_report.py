import json, numpy as np
S = json.load(open(r"D:/claude2/fangzhen/cad/out_map/solids.json", encoding="utf-8"))
A = np.array([s["lo"] for s in S], float); B = np.array([s["hi"] for s in S], float)
D = (B - A) / 1000.0
vol = np.array([s.get("vol_mm3", 0.0) for s in S], float) / 1e9
fill = np.array([s.get("fill_ratio", 0.0) for s in S], float)
print("solids:", len(S), " up axis: ", "xyz"[int(np.argmin(B.max(0) - A.min(0)))])
span = B.max(0) - A.min(0)
up = int(np.argmin(span)); print("span m:", np.round(span/1000, 2), "up =", "xyz"[up])
hh = D[:, up]; ax = [i for i in range(3) if i != up]
run = np.maximum(D[:, ax[0]], D[:, ax[1]])
big = (D[:, ax[0]] * D[:, ax[1]] > 0.04)
print("\nheight histogram of solids (m):")
for lo, hi in [(0,0.02),(0.02,0.05),(0.05,0.1),(0.1,0.2),(0.2,0.35),(0.35,0.6),(0.6,1.0),(1.0,4.0)]:
    m = (hh >= lo) & (hh < hi)
    print("   %.2f-%.2f m : %4d solids, area>0.04m2: %3d, median fill %.2f"
          % (lo, hi, m.sum(), (m & big).sum(), np.median(fill[m]) if m.sum() else -1))
wedge = big & (hh > 0.04) & (fill < 0.75) & (fill > 0.25)
box = big & (hh > 0.04) & (fill > 0.85)
print("\nwedge-like (ramp candidates):", wedge.sum(), " box-like:", box.sum())
if wedge.sum():
    sl = np.degrees(np.arctan2(hh[wedge], run[wedge]))
    print("   ramp slope deg: p5=%.1f p25=%.1f p50=%.1f p75=%.1f p95=%.1f" % tuple(np.percentile(sl, [5,25,50,75,95])))
    print("   ramp height  m: p25=%.3f p50=%.3f p75=%.3f" % tuple(np.percentile(hh[wedge], [25,50,75])))
    print("   ramp run     m: p25=%.3f p50=%.3f p75=%.3f" % tuple(np.percentile(run[wedge], [25,50,75])))
if box.sum():
    print("   box height m: p25=%.3f p50=%.3f p75=%.3f p95=%.3f" % tuple(np.percentile(hh[box], [25,50,75,95])))
    print("   box run  m: p25=%.3f p50=%.3f p75=%.3f" % tuple(np.percentile(run[box], [25,50,75])))
print("\nmax height of any solid: %.3f m ; total ground footprint: %.1f m2" % (hh.max(), (D[:,ax[0]]*D[:,ax[1]]).sum()))
