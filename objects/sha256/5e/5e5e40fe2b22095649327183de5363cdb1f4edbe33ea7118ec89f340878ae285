"""Render the chassis mass-property fix so it can be SEEN, not just asserted.

Left  = the plant V11..V13 were trained on: the base COM pinned to (0,0,0), i.e. 16.96 kg of
        chassis sitting exactly at the wheel-axle height, Izz 0.0435 kg*m^2.
Right = the corrected plant: base COM 239 mm above the axle (two independent geometry kernels
        agree, scripts/base_com_check.py) and Izz 0.614 kg*m^2.

Markers: red sphere = base-link COM, blue sphere = whole-robot COM, and a rod from the axle
plane up to each COM so the lever arm that gravity acts on is obvious.
"""
import json, math, os
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:/claude2/fangzhen"
OUT = os.path.join(ROOT, "docs/audit")
POST = os.path.join(ROOT, "robot/out_cc/scene_cc.xml")
PRE_DIR = os.path.join(OUT, "pre_baseinertia")
PRE = os.path.join(PRE_DIR, "scene_cc.xml")
if not os.path.exists(PRE):
    scene = open(POST, encoding="utf-8").read()
    robot = open(os.path.join(PRE_DIR, "rm_vehicle_cc.xml"), encoding="utf-8").read()
    robot = robot.replace('meshdir="meshes/"', 'meshdir="%s"' %
                          os.path.join(ROOT, "robot/out_cc/meshes").replace("\\", "/"))
    open(os.path.join(PRE_DIR, "rm_vehicle_cc.xml"), "w", encoding="utf-8").write(robot)
    open(PRE, "w", encoding="utf-8").write(scene)

BASE = "base_link"


def shot(xml, w=700, h=600, dist=1.32, azim=97.0, elev=11.0):
    spec = mujoco.MjSpec.from_file(xml)
    m0 = mujoco.MjModel.from_xml_path(xml)
    d0 = mujoco.MjData(m0)
    mujoco.mj_resetDataKeyframe(m0, d0, 0)
    mujoco.mj_forward(m0, d0)
    bi = mujoco.mj_name2id(m0, mujoco.mjtObj.mjOBJ_BODY, BASE)
    base_com = np.asarray(d0.xipos[bi], float)
    full_com = np.asarray(d0.subtree_com[1], float)
    cyl = [i for i in range(m0.ngeom)
           if "wheel_col" in (mujoco.mj_id2name(m0, mujoco.mjtObj.mjOBJ_GEOM, i) or "")]
    axle_z = float(np.mean([d0.geom_xpos[i, 2] for i in cyl]))
    mbase = float(m0.body_mass[bi])
    mtotal = float(m0.body_mass.sum())
    izz = float(np.sort(np.linalg.eigvalsh(
        np.asarray(d0.ximat[bi]).reshape(3, 3) @ np.diag(m0.body_inertia[bi])
        @ np.asarray(d0.ximat[bi]).reshape(3, 3).T))[2])
    # Markers sit OUTSIDE the silhouette (offset along X, the horizontal axis of this
    # camera) with a leader line back to the true point: inside the chassis they are
    # invisible even through an X-ray skin.
    OFFX = 0.46
    for i, (pos, col, r) in enumerate([(base_com, (1.0, 0.10, 0.08, 1.0), 0.055),
                                       (full_com, (0.05, 0.35, 1.0, 1.0), 0.065)]):
        mk = np.array([pos[0] + OFFX, pos[1], pos[2]])
        g = spec.worldbody.add_geom()
        g.name = "mark%d" % i
        g.type = mujoco.mjtGeom.mjGEOM_SPHERE
        g.size = [r, 0.0, 0.0]
        g.pos = [float(v) for v in mk]
        g.rgba = col
        g.contype = g.conaffinity = 0
        g.group = 0        # groups >2 are not drawn by the offscreen renderer (that is why the
        lead = spec.worldbody.add_geom()
        lead.name = "lead%d" % i
        lead.type = mujoco.mjtGeom.mjGEOM_CAPSULE
        lead.size = [0.006, 0.0, 0.0]
        lead.fromto = [float(a) for a in pos] + [float(a) for a in mk]
        lead.rgba = (col[0], col[1], col[2], 0.9)
        lead.contype = lead.conaffinity = 0
        lead.group = 0   # first attempt at this figure drew the markers into group 4 and they
        rod = spec.worldbody.add_geom()
        rod.name = "rod%d" % i
        rod.type = mujoco.mjtGeom.mjGEOM_BOX
        rod.size = [0.010, 0.010, max(1e-4, (pos[2] - axle_z) / 2.0)]
        rod.pos = [float(mk[0]), float(mk[1]), axle_z + rod.size[2]]
        rod.rgba = (col[0], col[1], col[2], 0.85)
        rod.contype = rod.conaffinity = 0
        rod.group = 0    # simply were not rendered at all.)
    # the axle plane itself, so the lever arm is measurable by eye
    ax = spec.worldbody.add_geom()
    ax.name = "axleline"
    ax.type = mujoco.mjtGeom.mjGEOM_BOX
    ax.size = [0.62, 0.42, 0.0015]
    ax.pos = [0.0, 0.0, axle_z]
    ax.rgba = (0.1, 0.1, 0.1, 0.55)
    ax.contype = ax.conaffinity = 0
    ax.group = 0
    m = spec.compile()
    # X-ray the CAD skin so the centre-of-mass markers inside the chassis are visible: this is
    # a diagram of mass, not a beauty shot.
    for i in range(m.ngeom):
        if int(m.geom_group[i]) == 2:
            m.geom_rgba[i, 3] = 0.30
        elif int(m.geom_group[i]) == 3:
            m.geom_rgba[i, 3] = 0.0
    d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, 0)
    mujoco.mj_forward(m, d)
    r = mujoco.Renderer(m, width=w, height=h)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = (0.0, 0.0, 0.235)
    cam.distance = dist
    cam.azimuth, cam.elevation = azim, elev
    m.vis.global_.offwidth, m.vis.global_.offheight = w, h
    r.update_scene(d, camera=cam)
    img = Image.fromarray(r.render())
    r.close()
    return img, dict(base_com=base_com, full_com=full_com, axle_z=axle_z,
                     mbase=mbase, mtotal=mtotal, izz=izz)


def cap(img, lines):
    im = img.copy()
    dr = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("arialbd.ttf", 21)
        fs = ImageFont.truetype("arial.ttf", 17)
    except Exception:
        f = fs = ImageFont.load_default()
    dr.rectangle([0, 0, im.width, 54], fill=(246, 246, 248))
    dr.text((10, 4), lines[0], fill=(15, 15, 15), font=f)
    dr.text((10, 30), lines[1], fill=(60, 60, 60), font=fs)
    return im


info = {}
tiles = []
for tag, xml in (("V11 - V13 (as trained)", PRE), ("CORRECTED (v14 onward)", POST)):
    img, st = shot(xml)
    info[tag] = st
    tiles.append(cap(img, [
        "%s   chassis COM z=%+.3f m (axle z=%+.3f)"
        % (tag, st["base_com"][2], st["axle_z"]),
        "robot COM %+.3f m  |  Izz %.4f kg*m^2  |  %.1f kg"
        % (st["full_com"][2], st["izz"], st["mtotal"])]))
    print(tag, {k: (np.round(v, 4).tolist() if isinstance(v, np.ndarray) else round(v, 4))
                for k, v in st.items()})
W, H = tiles[0].size
sheet = Image.new("RGB", (W * 2 + 18, H + 56), (255, 255, 255))
for i, t in enumerate(tiles):
    sheet.paste(t, (i * (W + 18), 0))
dr = ImageDraw.Draw(sheet)
try:
    fb = ImageFont.truetype("arialbd.ttf", 22)
except Exception:
    fb = ImageFont.load_default()
dr.text((10, H + 12),
        "red = chassis centre of mass, blue = whole-robot centre of mass, rod = the lever arm "
        "gravity acts on about the wheel axle.  The old model put 16.96 kg AT axle height with:",
        fill=(10, 10, 10), font=fb)
dr.text((10, H + 36),
        "1/14th of the true yaw inertia: no balance problem to learn (this IS a self-balancing "
        "two-wheel infantry robot) and a gyro spin that winds up ~14x too easily.  Corrected "
        "from the CAD solids; trimesh vs OpenCascade agree to 8 mm, SCUT wheelbipeV14_2 agrees.",
        fill=(10, 10, 10), font=fb)
p = os.path.join(OUT, "base_com_fix.png")
sheet.save(p)
json.dump({k: {kk: (list(map(float, vv)) if isinstance(vv, np.ndarray) else float(vv))
               for kk, vv in v.items()} for k, v in info.items()},
          open(os.path.join(OUT, "base_com_fix.json"), "w"), indent=1)
print("wrote", p)



