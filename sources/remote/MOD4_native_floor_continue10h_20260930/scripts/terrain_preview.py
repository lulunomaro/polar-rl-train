"""Render the RMUC2026 curriculum terrain that RL trains on, with no physics involved.

The user's requirement is "强化学习要适配这个地图" (the RL has to fit THIS map), so the
terrain has to be inspectable as a picture, not just as a config.  This builds exactly the
TerrainGeneratorCfg the field task uses (dimensions from cad/out_map/field_dims.json, which
scripts/map_field_dims.py measured out of RMUC2026_V2.0.0.stp) and renders

  1. an isometric overview of the whole 7-column x 5-row curriculum grid, and
  2. one close view per column,

so each feature can be compared with the map CAD by eye.
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

NUM_ROWS = int(os.environ.get("RM_TERRAIN_ROWS", "5"))
SIZE = 8.0
dims = load_dims()
cfg = rmuc2026_terrain(num_rows=NUM_ROWS, size_m=SIZE, curriculum=True, dims=dims)
names = list(cfg.sub_terrains.keys())
print("columns:", names)

spec = mujoco.MjSpec()
# the grid is ~96 x 68 m, so one torch would leave most of it black: light it from four
# corners plus a strong headlight, and give it a sky so the horizon reads.
for lp in ((60, -60, 70), (-60, -60, 70), (-60, 60, 70), (60, 60, 70)):
    spec.worldbody.add_light(pos=lp, dir=(-lp[0] / 90.0, -lp[1] / 90.0, -0.95),
                             diffuse=(0.85, 0.85, 0.82), specular=(0.2, 0.2, 0.2),
                             cutoff=85, exponent=8)
gen = TerrainGenerator(cfg)
gen.compile(spec)
m = spec.compile()
m.vis.headlight.ambient[:] = (0.62, 0.62, 0.66)
m.vis.headlight.diffuse[:] = (0.75, 0.75, 0.72)
m.vis.headlight.specular[:] = (0.15, 0.15, 0.15)
m.vis.global_.azimuth, m.vis.global_.elevation = 40.0, 32.0
# the renderer cannot allocate a bigger image than the model's offscreen framebuffer
m.vis.global_.offwidth = 1600
m.vis.global_.offheight = 1100
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
geoms = [i for i in range(m.ngeom)]
xs = np.array([d.geom_xpos[i] for i in geoms])
print("terrain geoms:", len(geoms), "x range", xs[:, 0].min(), xs[:, 0].max(),
      "y range", xs[:, 1].min(), xs[:, 1].max())
# where did the generator actually put the columns?  cluster the geom centres along each
# axis and keep the axis that shows 7 distinct bands -- that is the column direction.
cen = np.array([d.geom_xpos[i] for i in geoms])
bands = {}
for ax in (0, 1):
    u = np.unique(np.round(cen[:, ax] / (SIZE / 2.0)) * (SIZE / 2.0))
    bands[ax] = u
# ask the generator itself where each (row, col) patch went -- exact, no guessing
POS = {}
for r_ in range(NUM_ROWS):
    for c_ in range(len(names)):
        POS[(r_, c_)] = gen._get_sub_terrain_position(r_, c_)
colax = 0 if abs(POS[(0, 1)][0] - POS[(0, 0)][0]) > abs(POS[(1, 0)][0] - POS[(0, 0)][0]) else 1
print("column axis = %d; column 0 centre %s, column 1 centre %s"
      % (colax, np.round(POS[(0, 0)], 1), np.round(POS[(0, 1)], 1)))
cx, cy = float(np.mean(xs[:, 0])), float(np.mean(xs[:, 1]))
span = max(xs[:, 0].max() - xs[:, 0].min(), xs[:, 1].max() - xs[:, 1].min())


def render(w, h, lookat, dist, azim, elev):
    r = mujoco.Renderer(m, width=w, height=h)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = lookat
    cam.distance = dist
    cam.azimuth, cam.elevation = azim, elev
    m.vis.map.fogstart, m.vis.map.fogend = 400.0, 900.0   # fog lives in <map>, not <global>
    r.update_scene(d, camera=cam)
    img = Image.fromarray(r.render())
    r.close()
    return img


def font(sz):
    for f in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


# ---- 1. overview
ov = render(1500, 1000, (cx, cy, 0.0), span * 2.6, 35.0, 55.0)
dr = ImageDraw.Draw(ov)
dr.rectangle([0, 0, ov.width, 34], fill=(250, 250, 252))
dr.text((10, 6), "RMUC2026 7v7 field terrain for RL  |  %d columns x %d rows, %s m each, "
                 "difficulty grows upward" % (len(names), NUM_ROWS, SIZE), fill=(15, 15, 15),
        font=font(20))
ov.save(os.path.join(OUT, "terrain_2026_overview.png"))
print("wrote docs/audit/terrain_2026_overview.png")

# ---- 2. one close view per column
tiles = []
for j, nm in enumerate(names):
    # column centres: the generator lays columns along x, rows along y (see _get_sub_terrain_position)
    # _get_sub_terrain_position returns the CORNER, so add half a patch to aim properly
    pc = np.mean([POS[(r_, j)] for r_ in range(NUM_ROWS)], axis=0) + np.array([SIZE / 2.0,
                                                                              SIZE / 2.0, 0.0])
    look = (float(pc[0]), float(pc[1]), 0.10)
    img = render(460, 360, look, SIZE * 2.1, 35.0, 38.0)
    t = Image.new("RGB", (img.width, img.height + 26), (255, 255, 255))
    t.paste(img, (0, 26))
    d2 = ImageDraw.Draw(t)
    d2.text((6, 4), "%d/%d %s" % (j + 1, len(names), nm), fill=(10, 10, 10), font=font(17))
    tiles.append(t)
    print("  column %-12s centre (%+.1f, %+.1f)" % (nm, pc[0], pc[1]))
cols = 4
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (tiles[0].width * cols + 18 * (cols - 1),
                          tiles[0].height * rows + 18 * (rows - 1)), (255, 255, 255))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * (t.width + 18), (i // cols) * (t.height + 18)))
sheet.save(os.path.join(OUT, "terrain_2026_columns.png"))
print("wrote docs/audit/terrain_2026_columns.png")


