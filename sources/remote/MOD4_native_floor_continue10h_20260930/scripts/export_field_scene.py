"""Build the deployment field scene as ONE smooth heightfield from the dimensions measured
out of RMUC2026_V2.0.0.stp.

Why a heightfield and not separate boxes: the box version had a 5 cm lip and a small
horizontal gap where the spawn pad met the ramp, and the policy (trained on mjlab's
heightfield/primitive terrain) ground-truth-slipped there.  A single continuous profile
removes that artefact, so a failure in the demo means the policy, not the scene."""
import json, math, os, struct
import numpy as np
from scipy.ndimage import gaussian_filter1d

MAP = r"D:/claude2/fangzhen/cad/out_map"
OUT_DIR = r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle_cc/mjcf"
dims = json.load(open(os.path.join(MAP, "field_dims.json"), encoding="utf-8"))
slope = math.radians(float(np.clip(np.mean(dims["slope_deg"]) + 3.0, 10.0, 25.0)))
step_h = float(np.clip(np.mean(dims["step_height_m"]), 0.04, 0.18))
step_r = float(np.clip(np.mean(dims["step_run_m"]), 0.22, 0.45))
bar_h = float(np.clip(np.mean(dims["obstacle_height_m"]), 0.05, 0.30))
bar_w = float(np.clip(np.mean(dims["obstacle_width_m"]), 0.25, 0.80))
LX, LY, gs = 24.0, 6.0, 0.05
nx = int(LX / gs) + 1; ny = int(LY / gs) + 1
x = np.arange(nx) * gs
prof = np.zeros(nx)
rise = 0.62
x0 = 4.0                                   # ramp foot
ln = rise / math.tan(slope)
m = (x >= x0) & (x < x0 + ln); prof[m] = (x[m] - x0) * math.tan(slope)
x1 = x0 + ln; m = (x >= x1) & (x < x1 + 2.0); prof[m] = rise          # platform
x2 = x1 + 2.0
n_st = int(round(rise / step_h))
for i in range(n_st):                                                # stairs down
    xx = x2 + i * step_r
    prof[(x >= xx) & (x < xx + step_r)] = rise - (i + 1) * step_h
x3 = x2 + n_st * step_r
xb = x3 + 3.0                                                        # barricade
prof[(x >= xb) & (x < xb + bar_w)] = np.maximum(prof[(x >= xb) & (x < xb + bar_w)], bar_h)
prof = np.clip(prof, 0, None)
prof = gaussian_filter1d(prof, 1.0)                                  # de-lip the edges
H = np.tile(prof, (ny, 1))
hmax = float(H.max())
print("profile: slope %.1f deg, ramp %.2f m long / %.2f m rise, %d steps %.1f/%.1f cm, "
      "barricade %.0f cm at x=%.1f m"
      % (math.degrees(slope), ln, rise, n_st, step_h * 100, step_r * 100, bar_h * 100, xb))
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "..", "meshes"), exist_ok=True)
hf = np.clip(H / max(1e-9, hmax), 1e-3, 1.0).astype("<f4")
with open(os.path.join(OUT_DIR, "..", "meshes", "field.hf"), "wb") as fh:
    fh.write(struct.pack("<ii", ny, nx)); fh.write(np.ascontiguousarray(hf).tobytes())
np.savetxt(os.path.join(MAP, "field_profile.txt"), prof)
xml = """<mujoco model="rm_vehicle_cc on the RMUC2026-derived field">
  <include file="rm_vehicle.xml"/>
  <visual><global offwidth="1280" offheight="720"/>
    <headlight diffuse="0.7 0.7 0.7" ambient="0.35 0.35 0.35" specular="0.2 0.2 0.2"/></visual>
  <asset>
    <hfield name="field" size="%.3f %.3f %.4f 0.0001" nrow="%d" ncol="%d" file="../meshes/field.hf"/>
    <texture type="skybox" builtin="gradient" rgb1="0.55 0.6 0.68" rgb2="0.25 0.28 0.33" width="256" height="256"/>
    <texture type="2d" name="grid" builtin="checker" rgb1="0.45 0.5 0.56" rgb2="0.6 0.65 0.7" width="256" height="256"/>
    <material name="fieldmat" texture="grid" texuniform="true" texrepeat="0.2 0.2" reflectance="0.0"/>
  </asset>
  <worldbody>
    <geom name="ground_plane" type="plane" size="0 0 0.05" material="fieldmat" contype="1"
          conaffinity="255" friction="1.6 0.02 0.002" rgba="0.5 0.55 0.62 1" pos="0 0 -0.05"/>
    <geom name="field" type="hfield" hfield="field" pos="%.3f %.3f 0" material="fieldmat"
          contype="1" conaffinity="255" friction="1.6 0.02 0.002"/>
    <light pos="6 -3 8" dir="-0.2 0.2 -1" diffuse="0.9 0.9 0.9" specular="0.2 0.2 0.2"/>
  </worldbody>
</mujoco>
""" % (LX / 2, LY / 2, hmax, ny, nx, 10.0, -LY / 2)
open(os.path.join(OUT_DIR, "scene_field.xml"), "w", encoding="utf-8", newline="\n").write(xml)
print("world x of each feature: ramp foot %.2f, platform %.2f, stairs %.2f, barricade %.2f"
      % (x0 - 2.0, x1 - 2.0, x2 - 2.0, xb - 2.0))
print("wrote %s (max height %.2f m, grid %dx%d)" % (os.path.join(OUT_DIR, "scene_field.xml"), hmax, ny, nx))
import mujoco
m2 = mujoco.MjModel.from_xml_path(os.path.join(OUT_DIR, "scene_field.xml"))
print("compiles: nq=%d nv=%d neq=%d ngeom=%d hfield nrow/ncol=%d/%d"
      % (m2.nq, m2.nv, m2.neq, m2.ngeom, m2.hfield_nrow[0], m2.hfield_ncol[0]))
