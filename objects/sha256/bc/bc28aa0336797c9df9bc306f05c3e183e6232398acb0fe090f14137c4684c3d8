"""Derive the RL terrain parameters from the RMUC2026 7v7 map geometry (CAD-measured).

Inputs (produced by scripts/map_extract.py):
  cad/out_map/map_verts.npy + map_faces.npy  - coarse mesh of the whole field
  cad/out_map/solids.json                    - per-solid bbox + volume

Method: classify mesh triangles by surface inclination.
  * drivable ramps  -> inclined 8..40 deg faces close to the ground  -> slope_deg
  * step risers     -> near-vertical faces below 1.3 m, their z-extent -> step_height_m
  * treads          -> horizontal faces above the first step          -> step_run_m
  * barricades      -> compact low solids from the inventory           -> obstacle_*
Writes cad/out_map/field_dims.json, consumed by rmvehicle/field_cfg.py.
"""
import json, os
import numpy as np

OUT = r"D:/claude2/fangzhen/cad/out_map"
V = np.load(os.path.join(OUT, "map_verts.npy"))
F = np.load(os.path.join(OUT, "map_faces.npy")).astype(np.int64)
solids = json.load(open(os.path.join(OUT, "solids.json"), encoding="utf-8"))
print("mesh: %d verts %d faces | solids: %d" % (len(V), len(F), len(solids)))

span = V.max(0) - V.min(0)
up = int(np.argmin(span))
plan = [i for i in range(3) if i != up]
a_ax, b_ax = plan
print("bbox mm %s -> %s  span %s | up axis = %s"
      % (np.round(V.min(0), 1), np.round(V.max(0), 1), np.round(span, 1), "xyz"[up]))

tri = V[F]
nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
area = 0.5 * np.linalg.norm(nrm, axis=1)
keep = area > 1e-9
tri, nrm, area = tri[keep], nrm[keep] / (2 * area[keep])[:, None], area[keep]
cen = tri.mean(axis=1)
u = np.zeros(3); u[up] = 1.0
tilt = np.degrees(np.arccos(np.clip(np.abs(nrm @ u), 0, 1)))
z0 = V[:, up].min()
zc = (cen[:, up] - z0) / 1000.0
print("\nfaces %d, area %.1f m2" % (len(area), area.sum() / 1e6))
print("area by inclination band:")
for lo, hi in [(0, 3), (3, 8), (8, 20), (20, 32), (32, 45), (45, 60), (60, 80), (80, 90.1)]:
    m = (tilt >= lo) & (tilt < hi)
    print("   %2d-%2d deg : %8.2f m2 (%5.1f%%)" % (lo, hi, area[m].sum() / 1e6,
                                                   100 * area[m].sum() / area.sum()))

low = zc < 1.30
ramp = low & (tilt >= 8) & (tilt <= 40) & (area > 1e4)
rw, ang = area[ramp], tilt[ramp]
order = np.argsort(ang); cw = np.cumsum(rw[order]) / max(1e-9, rw.sum())
def q(pr):
    return float(ang[order][np.searchsorted(cw, pr)]) if rw.sum() else float("nan")
slope_lo, slope_med, slope_hi = q(0.10), q(0.50), q(0.95)
print("\nDRIVABLE RAMP faces: %d, %.2f m2, incline p10=%.1f median=%.1f p95=%.1f deg"
      % (ramp.sum(), rw.sum() / 1e6, slope_lo, slope_med, slope_hi))
if ramp.sum():
    rise = (tri[ramp][:, :, up].max(1) - tri[ramp][:, :, up].min(1)) / 1000.0
    print("   ramp face rise: p25=%.2f median=%.2f p75=%.2f m" % tuple(np.percentile(rise, [25, 50, 75])))
else:
    slope_lo, slope_hi = 12.0, 30.0

vert = low & (tilt > 75)
zv = (tri[vert][:, :, up].max(1) - tri[vert][:, :, up].min(1)) / 1000.0 if vert.sum() else np.zeros(0)
zv = zv[zv > 0.015]
if len(zv):
    print("STEP RISER faces: %d, height p10=%.3f median=%.3f p75=%.3f p95=%.3f m"
          % (len(zv), *np.percentile(zv, [10, 50, 75, 95])))
step_lo = float(np.clip(np.percentile(zv, 10) if len(zv) else 0.05, 0.02, 0.10))
step_hi = float(np.clip(np.percentile(zv, 90) if len(zv) else 0.15, step_lo + 0.02, 0.22))

# Tread depth: the CAD floor is one huge triangulated plane, so measuring horizontal
# face extent is meaningless.  Instead use the ramp geometry itself: a face that rises
# `rise` over an incline of `slope` has horizontal run rise/tan(slope).
if ramp.sum():
    rise_p = np.percentile((tri[ramp][:, :, up].max(1) - tri[ramp][:, :, up].min(1)) / 1000.0,
                           [25, 50, 75])
    runs = rise_p / np.tan(np.radians([slope_hi, slope_med, slope_lo]))
    step_run = float(np.clip(np.median(runs), 0.15, 1.20))
    run_lo = float(np.clip(runs.min() * 0.8, 0.15, 1.0))
    run_hi = float(np.clip(runs.max() * 1.2, step_run, 1.6))
    print("TREAD from ramp geometry: rise %s m over %s deg -> run %s m"
          % (np.round(rise_p, 3), [round(slope_hi, 1), round(slope_med, 1), round(slope_lo, 1)],
             np.round(runs, 3)))
else:
    step_run, run_lo, run_hi = 0.35, 0.25, 0.50

foot = []
for so in solids:
    lo3 = np.array(so["lo"], float); hi3 = np.array(so["hi"], float)
    d = (hi3 - lo3) / 1000.0
    if not (0.05 <= d[up] <= 1.3):
        continue
    if max(d[a_ax], d[b_ax]) < 2.5 and min(d[a_ax], d[b_ax]) < 2.5:
        foot.append((d[up], max(d[a_ax], d[b_ax]), min(d[a_ax], d[b_ax])))
foot = np.array(foot) if foot else np.array([[0.1, 0.5, 0.3]])
print("\nlow compact solids (barricade candidates): %d, height p25=%.3f p90=%.3f m, "
      "width p25=%.3f p90=%.3f m" % (len(foot), np.percentile(foot[:, 0], 25),
                                     np.percentile(foot[:, 0], 90),
                                     np.percentile(foot[:, 1], 25),
                                     np.percentile(foot[:, 1], 90)))
dims = dict(
  field_size_m=[round(float(span[a_ax] / 1000), 2), round(float(span[b_ax] / 1000), 2)],
  height_range_m=[0.0, round(float(span[up] / 1000), 3)],
  slope_deg=[round(float(slope_lo), 1), round(float(slope_hi), 1)],
  step_height_m=[round(step_lo, 3), round(step_hi, 3)],
  step_run_m=[round(run_lo, 3), round(run_hi, 3)],
  obstacle_height_m=[round(float(max(0.03, np.percentile(foot[:, 0], 25))), 3),
                     round(float(min(0.45, np.percentile(foot[:, 0], 90))), 3)],
  obstacle_width_m=[round(float(max(0.20, np.percentile(foot[:, 1], 25))), 3),
                    round(float(min(1.60, np.percentile(foot[:, 1], 90))), 3)],
  roughness_m=0.02,
  platform_height_m=round(float(np.percentile(zc, 99.5)), 3),
  up_axis="xyz"[up],
  ramp_faces_m2=round(float(rw.sum() / 1e6), 2),
  source="RMUC2026_V2.0.0.stp",
)
json.dump(dims, open(os.path.join(OUT, "field_dims.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("\nwrote field_dims.json:")
for k, v in dims.items():
    print("   %-20s %s" % (k, v))
