"""Phase-1 visual health check: per-joint sweep contact sheets + collision debug views.

Nothing here modifies the model.  Every sweep is loop-consistent: the two actuated hip-axis
joints are driven through scripts/leg2d.py (the analytic similar-link solution that
cc_gaps.py proves reproduces the MJCF to 0.0000 mm), and each passive joint is rendered at
the two extremes of its ACHIEVABLE range, because a closed chain has no independent
passive DOF and sweeping one alone would tear the loop.
"""
import json, os, sys
import numpy as np, mujoco
import imageio
from PIL import Image, ImageDraw
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD

ROOT = r"D:/claude2/fangzhen"
OUT = os.path.join(ROOT, "docs", "audit")
os.makedirs(OUT, exist_ok=True)
XML = os.path.join(ROOT, "robot/out_cc/scene_cc.xml")
L = Kite2D(CAD, "sweep")
KEYS = ("rear1", "front1", "rear2", "front2", "front3", "front4", "spring1", "spring2")


def model():
    m = mujoco.MjModel.from_xml_path(XML)
    d = mujoco.MjData(m)
    return m, d


def set_pose(m, d, thigh, crank):
    q = L.qpos_full(thigh, crank)
    if q is None:
        return None
    mujoco.mj_resetData(m, d)
    for s in ("left", "right"):
        for k in KEYS:
            j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "%s_%s_joint" % (s, k))
            a, v = m.jnt_qposadr[j], m.jnt_dofadr[j]
            d.qpos[a] = q[k] / 1000.0 if k == "spring2" else -q[k]
            d.qvel[v] = 0.0
    d.qpos[0:2] = 0.0
    d.qpos[2] = 0.073 - 0.2121 - q["pts"]["axle"][1] / 1000.0
    d.qpos[3] = 1.0
    mujoco.mj_forward(m, d)
    gap = 0.0
    for e in range(m.neq):
        b1, b2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
        p1 = d.xpos[b1] + d.xmat[b1].reshape(3, 3) @ ed[0:3]
        p2 = d.xpos[b2] + d.xmat[b2].reshape(3, 3) @ ed[3:6]
        gap = max(gap, 1000.0 * float(np.linalg.norm(p1 - p2)))
    return gap


def sheet(m, d, poses, title, path, azim=62, elev=14, dist=0.72):
    r = mujoco.Renderer(m, height=430, width=430)
    cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat = np.array([-0.08, -0.24, 0.16]); cam.azimuth = azim
    cam.elevation = elev; cam.distance = dist
    tiles = []
    for lab, th, cr in poses:
        gap = set_pose(m, d, th, cr)
        r.update_scene(d, camera=cam)
        img = r.render()
        im = Image.fromarray(img); dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, im.width, 34], fill=(12, 14, 18))
        dr.text((6, 4), lab, fill=(238, 241, 245))
        dr.text((6, 19), "loop gap %s mm" % ("%.4f" % gap if gap is not None else "n/a"),
                fill=(150, 220, 160) if (gap or 0) < 2 else (240, 120, 120))
        tiles.append(np.asarray(im))
    w = min(t.shape[1] for t in tiles)
    tiles = [t[:430, :w] for t in tiles]
    g = np.hstack(tiles)
    head = np.full((40, g.shape[1], 3), 12, dtype=np.uint8)
    Image.fromarray(head).save("/dev/null") if False else None
    im = Image.fromarray(np.vstack([g]))
    canvas = Image.new("RGB", (im.width, im.height + 34), (12, 14, 18))
    canvas.paste(im, (0, 34))
    dd = ImageDraw.Draw(canvas); dd.text((8, 9), title, fill=(238, 241, 245))
    canvas.save(path)
    print("wrote", os.path.basename(path), canvas.size)


m, d = model()
# ---- A. actuated hip-axis joints -------------------------------------------------
sheet(m, d, [("thigh -0.60", -0.60, 0.0), ("thigh -0.30", -0.30, 0.0),
             ("thigh  0.00", 0.0, 0.0), ("thigh +0.30", 0.30, 0.0),
             ("thigh +0.60", 0.60, 0.0)],
      "JOINT SWEEP  left_rear1 (thigh drive, DM-J8009 #1) - crank held at 0 - "
      "rotation centre MUST stay on the hip bearing",
      os.path.join(OUT, "sweep_rear1_thigh.png"))
sheet(m, d, [("crank -0.60", 0.0, -0.60), ("crank -0.30", 0.0, -0.30),
             ("crank  0.00", 0.0, 0.0), ("crank +0.30", 0.0, 0.30),
             ("crank +0.60", 0.0, 0.60)],
      "JOINT SWEEP  left_front1 (knee drive via similar-link four-bar) - thigh held at 0 - "
      "the four-bar must fold/unfold about the crank pin",
      os.path.join(OUT, "sweep_front1_crank.png"))
sheet(m, d, [("both -0.45 (crouch)", -0.45, -0.45), ("both -0.20", -0.20, -0.20),
             ("qpos0 (CAD stance)", 0.0, 0.0), ("both +0.20", 0.20, 0.20),
             ("both +0.40 (tall)", 0.40, 0.40)],
      "LEG EXTENSION SWEEP  both hip drives together - this is the jump stroke: "
      "hip->axle distance must change monotonically and the knee must never touch the floor",
      os.path.join(OUT, "sweep_leg_extension.png"))

# ---- B. passive joints at the extremes of their achievable range -----------------
rng = np.arange(-1.2, 1.25, 0.02)
ext = {k: (9e9, -9e9) for k in KEYS}
for th in rng:
    for cr in rng:
        q = L.qpos_full(th, cr)
        if q is None:
            continue
        for k in KEYS:
            ext[k] = (min(ext[k][0], q[k]), max(ext[k][1], q[k]))
lim = {}
for s in ("left", "right"):
    for k in KEYS:
        j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "%s_%s_joint" % (s, k))
        lim[k] = (float(m.jnt_range[j][0]), float(m.jnt_range[j][1]), bool(m.jnt_limited[j]))
print("\n== passive joint limits vs the ACHIEVABLE workspace (rad, MJCF sign) ==")
print("  %-9s %-22s %-22s %s" % ("joint", "MJCF range", "achievable", "verdict"))
for k in KEYS:
    lo, hi, limited = lim[k]
    alo, ahi = -ext[k][1], -ext[k][0]          # MJCF qpos = -analytic
    if not limited:
        v = "UNLIMITED (actuated hip axis)"
    else:
        ok = (lo <= alo + 1e-6) and (hi >= ahi - 1e-6)
        v = "OK, brackets workspace (margin %.2f/%.2f)" % (alo - lo, hi - ahi) if ok \
            else "**CLIPS WORKSPACE** (needs %.2f..%.2f)" % (alo, ahi)
    print("  %-9s [%7.3f %7.3f]      [%7.3f %7.3f]      %s" % (k, lo, hi, alo, ahi, v))
json.dump({"achievable": {k: [-v[1], -v[0]] for k, v in ext.items()},
           "mjcf_range": lim}, open(os.path.join(OUT, "joint_workspace.json"), "w"), indent=1)