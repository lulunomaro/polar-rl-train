"""Draw the RMUC2026 curriculum terrain as height maps and cross-sections.

Why not a 3D screenshot: the grid is ~96 x 68 m of heightfields and a perspective camera
makes it impossible to read the step heights that actually matter.  This reads the height
values straight out of the compiled terrain, so what you see IS what the wheels touch:

  top    a 7 x 5 mosaic, one cell per (column, row) sub-terrain, coloured by height
         (rows = difficulty, so the gradient down each column is the curriculum)
  bottom one longitudinal cross-section per column, at the hardest row, with the vertical
         scale exaggerated 3x and the CAD-derived dimension printed on it

Dimensions come from cad/out_map/field_dims.json, measured out of RMUC2026_V2.0.0.stp by
scripts/map_field_dims.py.
"""
import os, sys
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:/claude2/fangzhen"
sys.path.insert(0, os.path.join(ROOT, "train/rmvehicle/src"))
OUT = os.path.join(ROOT, "docs/audit")
from mjlab.terrains import TerrainGenerator  # noqa: E402
from rmvehicle.field_cfg import rmuc2026_terrain, load_dims  # noqa: E402

NUM_ROWS = 5
SIZE = 8.0
dims = load_dims()
cfg = rmuc2026_terrain(num_rows=NUM_ROWS, size_m=SIZE, curriculum=True, dims=dims)
names = list(cfg.sub_terrains.keys())
spec = mujoco.MjSpec()
gen = TerrainGenerator(cfg)
gen.compile(spec)
m = spec.compile()
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)

cells = {}
for i in range(m.ngeom):
    if int(m.geom_type[i]) != int(mujoco.mjtGeom.mjGEOM_HFIELD):
        continue
    hid = int(m.geom_dataid[i])        # per-type geom index: for an hfield this is the
    nr, nc = int(m.hfield_nrow[hid]), int(m.hfield_ncol[hid])
    adr = int(m.hfield_adr[hid])
    z = np.asarray(m.hfield_data[adr:adr + nr * nc], float).reshape(nr, nc)
    z = z * float(m.hfield_size[hid][2])   # stored normalised; scale by the top height
    pos = np.asarray(d.geom_xpos[i], float)
    cells[(round(pos[0], 2), round(pos[1], 2))] = z
print("hfield patches:", len(cells))
xs = sorted({k[0] for k in cells})
ys = sorted({k[1] for k in cells})
print("x bands", len(xs), "y bands", len(ys))
# the generator lays columns along the axis that has len(sub_terrains) bands
if len(ys) == len(names):
    colax, colkeys = 1, ys
elif len(xs) == len(names):
    colax, colkeys = 0, xs
else:
    colax, colkeys = (1 if len(ys) > len(xs) else 0), (ys if len(ys) > len(xs) else xs)
    print("WARN expected %d column bands, found %d/%d; using the finer axis"
          % (len(names), len(xs), len(ys)))
rowkeys = xs if colax == 1 else ys
print("column axis %d with %d bands" % (colax, len(colkeys)))


def font(sz, bold=False):
    for f in (("arialbd.ttf" if bold else "arial.ttf"), "arial.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def cmap(v):
    """blue (low) -> green -> red (high), matching MuJoCo's height colouring."""
    v = float(np.clip(v, 0, 1))
    if v < 0.5:
        t = v / 0.5
        return (int(30 + 60 * t), int(70 + 130 * t), int(220 - 150 * t))
    t = (v - 0.5) / 0.5
    return (int(90 + 165 * t), int(200 - 140 * t), int(70 - 40 * t))


zall = np.concatenate([z.ravel() for z in cells.values()])
gz, gmax = float(zall.min()), float(zall.max())
print("global height range %.3f .. %.3f (raw units)" % (gz, gmax))

CELL = 150
gap = 8
sheet = Image.new("RGB", (len(colkeys) * (CELL + gap) + 40,
                          (len(rowkeys) + 1) * (CELL + gap) + 300), (255, 255, 255))
dr = ImageDraw.Draw(sheet)
dr.text((12, 8), "RMUC2026 7v7 field, the terrain RL actually trains on  "
                 "(height map, blue low -> red high)", fill=(10, 10, 10), font=font(24, True))
dr.text((12, 38), "columns = the map features measured out of RMUC2026_V2.0.0.stp; "
                  "rows = curriculum difficulty (top row = easiest, bottom = hardest)",
        fill=(70, 70, 70), font=font(18))
top = 66
for j, cy in enumerate(colkeys):
    dr.text((12 + j * (CELL + gap), top - 4), names[j] if j < len(names) else "?",
            fill=(10, 10, 10), font=font(15, True))
    for r_, rx in enumerate(rowkeys):
        key = (rx, cy) if colax == 1 else (cy, rx)
        z = cells.get(key)
        x0 = 12 + j * (CELL + gap)
        y0 = top + 22 + r_ * (CELL + gap)
        if z is None:
            dr.rectangle([x0, y0, x0 + CELL, y0 + CELL], outline=(220, 220, 220))
            continue
        zz = (z - gz) / max(1e-9, gmax - gz)
        rgb = np.zeros(zz.shape + (3,), dtype=np.uint8)
        for a in range(zz.shape[0]):
            for b in range(zz.shape[1]):
                rgb[a, b] = cmap(zz[a, b])
        im = Image.fromarray(rgb, "RGB")
        sheet.paste(im.resize((CELL, CELL), Image.NEAREST), (x0, y0))
        dr.rectangle([x0, y0, x0 + CELL, y0 + CELL], outline=(120, 120, 120))

# ---- cross-sections of the hardest row
prof_y = top + 22 + len(rowkeys) * (CELL + gap) + 26
dr.text((12, prof_y - 24), "longitudinal cross-section of the hardest row "
                          "(vertical scale x3; the numbers are the CAD-measured feature size)",
        fill=(10, 10, 10), font=font(19, True))
labels = {
    "flat": "平地竞技场 8x8 m",
    "ramp_up": "坡道 9.4-25 deg",
    "ramp_down": "下坡 9.4-25 deg",
    "stairs_up": "台阶 2-22 cm, 踏面 15-108 cm",
    "stairs_down": "下台阶 2-22 cm",
    "obstacles": "掩体 7.4-41.6 cm 高, 20-109 cm 宽",
    "rough": "起伏 +-2 cm",
}
PH = 150
for j, cy in enumerate(colkeys):
    key = (rowkeys[-1], cy) if colax == 1 else (cy, rowkeys[-1])
    z = cells.get(key)
    x0 = 12 + j * (CELL + gap)
    y0 = prof_y
    dr.rectangle([x0, y0, x0 + CELL, y0 + PH], outline=(200, 200, 200))
    if z is None:
        continue
    mid = z[z.shape[0] // 2] if colax == 1 else z[:, z.shape[1] // 2]
    lo, hi = float(mid.min()), float(mid.max())
    pts = []
    for k, v in enumerate(mid):
        px = x0 + k * (CELL / max(1, len(mid) - 1.0))
        t = 0.0 if hi <= lo else (float(v) - lo) / (hi - lo)
        pts.append((px, y0 + PH - 12 - t * (PH - 30)))
    pts.append((x0 + CELL, y0 + PH - 12)); pts.append((x0, y0 + PH - 12))
    dr.polygon(pts, fill=(150, 190, 235), outline=(30, 60, 120))
    nm = names[j] if j < len(names) else ""
    dr.text((x0 + 2, y0 + PH + 2), nm, fill=(40, 40, 40), font=font(13, True))
    dr.text((x0 + 2, y0 + PH + 18), labels.get(nm, ""), fill=(90, 90, 90), font=font(11))
p = os.path.join(OUT, "terrain_2026_sections.png")
sheet.save(p)
print("wrote", p, sheet.size)


