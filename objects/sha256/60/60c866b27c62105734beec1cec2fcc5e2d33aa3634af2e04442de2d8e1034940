"""Publication-quality stills of the closed-chain plant (visuals only; no policy).

Usage:  python scripts/render_hero.py [outprefix]
Writes  docs/audit/hero_<name>.png  and a combined contact sheet.
"""
import os, sys, numpy as np, mujoco
from PIL import Image, ImageDraw
ROOT = r"D:\claude2\fangzhen"
OUT = os.path.join(ROOT, "docs", "audit")
os.makedirs(OUT, exist_ok=True)
XML = os.path.join(ROOT, "robot", "out_cc", "scene_cc.xml")
m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)
W, H = 1100, 820
r = mujoco.Renderer(m, height=H, width=W)
CEN = np.array([0.0, 0.0, 0.30])
# (label, look-at, distance, elevation, azimuth)   azimuth 90 = -y side, 270 = +y side
SHOTS = [
    ("A_side_left",   CEN, 1.55, 4, 90),
    ("B_34_front",    CEN, 1.70, 20, 55),
    ("C_side_right",  CEN, 1.55, 4, 270),
    ("D_34_rear",     CEN, 1.75, 18, 235),
    ("E_top",         CEN, 1.35, 78, 40),
    ("F_leg_closeup", np.array([-0.10, -0.24, 0.16]), 0.62, 10, 68),
]
def shoot(label, look, dist, elev, azim, cap):
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat = look; cam.distance = dist; cam.elevation = elev; cam.azimuth = azim
    r.update_scene(d, camera=cam)
    img = r.render()
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, W, 26], fill=(18, 20, 24))
    dr.text((10, 7), cap, fill=(235, 238, 242))
    im.save(os.path.join(OUT, "hero_%s.png" % label))
    return np.asarray(im)
tiles = [shoot(*s, s[0].replace("_", " ") +
              "   |  593 chassis solids + 140 leg solids = 733 CAD parts, "
              "2.79 M triangles, 20.00 kg") for s in SHOTS]
def grid(imgs, cols, name):
    rows = (len(imgs) + cols - 1) // cols
    while len(imgs) < rows * cols:
        imgs.append(np.full_like(imgs[0], 20))
    g = np.vstack([np.hstack(imgs[i * cols:(i + 1) * cols]) for i in range(rows)])
    Image.fromarray(g).save(os.path.join(OUT, name))
    print("wrote", name, g.shape)
grid(tiles, 2, "hero_sheet.png")
grid(tiles[:2] + tiles[4:6] + tiles[2:4] + tiles[6:8], 2, "hero_small.png") if len(tiles) > 6 else None
print("ngeom", m.ngeom, "visual tris", sum(m.mesh_facenum))