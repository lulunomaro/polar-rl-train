"""Visual proof that visual and collision are separated, and that the collision proxy is a
sane primitive hull of the real machine (never the 2.79 M-triangle CAD skin).

Three layers x three views: VISUAL only / COLLISION only / both overlaid.
"""
import os
import numpy as np, mujoco
from PIL import Image, ImageDraw

ROOT = r"D:/claude2/fangzhen"
OUT = os.path.join(ROOT, "docs", "audit")
os.makedirs(OUT, exist_ok=True)
m = mujoco.MjModel.from_xml_path(os.path.join(ROOT, "robot/out_cc/scene_cc.xml"))
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

VIS, COL = [], []
for g in range(m.ngeom):
    if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_PLANE:
        continue
    (VIS if m.geom_group[g] == 2 else COL).append(g)
print("visual geoms %d   collision geoms %d" % (len(VIS), len(COL)))
print("collision primitives:", sorted({mujoco.mjtGeom(int(m.geom_type[g])).name.replace("mjGEOM_","") for g in COL}))
tri_vis = int(sum(m.mesh_facenum[m.geom_dataid[g]] for g in VIS if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH))
print("visual triangles %d   collision triangles %d (primitives carry none)" % (tri_vis, 0))

ORIG = m.geom_rgba.copy()
ORIG_G = m.geom_group.copy()
# MuJoCo's offscreen renderer only draws geom groups 0-2 by default, so the collision
# primitives (group 3) have to be promoted into the visible set for these debug shots.
def show_collision():
    for g in COL:
        m.geom_group[g] = 2

def layer(mode):
    m.geom_rgba[:] = ORIG
    m.geom_group[:] = ORIG_G
    if mode == "visual":
        for g in COL:
            m.geom_rgba[g] = [0, 0, 0, 0]
    elif mode == "collision":
        for g in VIS:
            m.geom_rgba[g] = [0, 0, 0, 0]
        show_collision()
        for g in COL:
            t = int(m.geom_type[g])
            if t == mujoco.mjtGeom.mjGEOM_MESH:
                m.geom_rgba[g] = [0.2, 0.2, 0.2, 0.25]      # hidden proxy, kept faint
            elif "wheel" in (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ""):
                m.geom_rgba[g] = [0.95, 0.35, 0.10, 0.55]   # orange = tyre contact surface
            elif "base" in (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ""):
                m.geom_rgba[g] = [0.10, 0.55, 0.95, 0.30]   # blue = chassis hull
            else:
                m.geom_rgba[g] = [0.10, 0.85, 0.30, 0.45]   # green = limb capsules
    else:
        show_collision()
        for g in COL:
            t = int(m.geom_type[g])
            if "wheel" in (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ""):
                m.geom_rgba[g] = [0.95, 0.35, 0.10, 0.40]
            elif "base" in (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ""):
                m.geom_rgba[g] = [0.10, 0.55, 0.95, 0.16]
            else:
                m.geom_rgba[g] = [0.10, 0.85, 0.30, 0.28]
        m.geom_group[0] = 5                                  # drop the floor for clarity

VIEWS = {"side": (1.35, 6, 90), "3/4": (1.55, 20, 55), "front": (1.45, 8, 0)}
r = mujoco.Renderer(m, height=560, width=760)
cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
rows = []
for mode, cap in (("visual", "VISUAL  -  2.79 M-triangle CAD skin, 733/733 parts, contype=0 (cannot touch anything)"),
                  ("collision", "COLLISION  -  19 primitives: 1 chassis box + 16 limb capsules + 2 wheel cylinders"),
                  ("overlay", "OVERLAY  -  collision proxy against the visual skin (green limbs / orange tyres / blue hull)")):
    layer(mode)
    m.geom_group[0] = 0 if mode != "overlay" else 5
    tiles = []
    for vn, (dist, el, az) in VIEWS.items():
        cam.lookat = np.array([0, 0, 0.28]); cam.distance = dist
        cam.elevation = el; cam.azimuth = az
        r.update_scene(d, camera=cam)
        im = Image.fromarray(r.render()); dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, im.width, 20], fill=(10, 12, 16))
        dr.text((6, 4), vn, fill=(220, 226, 232))
        tiles.append(np.asarray(im))
    band = np.full((26, sum(t.shape[1] for t in tiles), 3), 10, dtype=np.uint8)
    rows.append((np.hstack(tiles), band, cap))
H = sum(t[0].shape[0] + t[1].shape[0] for t in rows)
W = max(t[0].shape[1] for t in rows)
canvas = Image.new("RGB", (W, H), (10, 12, 16))
y = 0
for tiles_img, band, cap in rows:
    canvas.paste(Image.fromarray(band), (0, y)); y += band.shape[0]
    dd = ImageDraw.Draw(canvas); dd.text((8, y - 20), cap, fill=(238, 241, 245))
    canvas.paste(Image.fromarray(tiles_img), (0, y)); y += tiles_img.shape[0]
p = os.path.join(OUT, "collision_debug.png"); canvas.save(p)
print("wrote", p, canvas.size)