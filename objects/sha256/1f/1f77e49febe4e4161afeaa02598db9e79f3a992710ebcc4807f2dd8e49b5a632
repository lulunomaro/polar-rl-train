"""Model showcase video for the corrected closed-chain plant.

Pure kinematics: every joint angle comes from scripts/leg2d.py (the analytic similar-link
solution that scripts/cc_gaps.py proves reproduces the MJCF to 0.0000 mm).  No policy is
involved, so nothing here can be mistaken for an RL result.

  1. turntable 360 deg at the CAD stand pose
  2. crank sweep  3. thigh sweep  (base height recomputed so the tyres stay on the floor)
"""
import os, sys, imageio, mujoco, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD

ROOT = r"D:/claude2/fangzhen"
XML = os.path.join(ROOT, "robot", "out_cc", "scene_cc.xml")
OUT = os.path.join(ROOT, "docs", "videos", "model_showcase_fixed.mp4")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
FPS = 24
SEC = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
R_WHEEL, HIP_Z = 0.073, 0.2121

m = mujoco.MjModel.from_xml_path(XML)
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
FREE = m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "floating_base")]
L = Kite2D(CAD, "showcase")
KEYS = ("rear1", "front1", "rear2", "front2", "front3", "front4", "spring1", "spring2")
ADR = {s: {k: m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT,
              "%s_%s_joint" % (s, k))] for k in KEYS} for s in ("left", "right")}

def pose(thigh, crank):
    q = L.qpos_full(thigh, crank)
    assert q is not None, "pose outside the linkage workspace (thigh=%+.2f crank=%+.2f)" % (thigh, crank)
    mujoco.mj_resetData(m, d)
    for s in ("left", "right"):
        for k in KEYS:
            d.qpos[ADR[s][k]] = q[k] / 1000.0 if k == "spring2" else -q[k]
    d.qpos[FREE + 2] = R_WHEEL - HIP_Z - q["pts"]["axle"][1] / 1000.0
    d.qpos[FREE + 3] = 1.0
    d.qvel[:] = 0.0
    mujoco.mj_forward(m, d)
    gap = 0.0
    for e in range(m.neq):
        o1, o2 = int(m.eq_obj1id[e]), int(m.eq_obj2id[e]); ed = m.eq_data[e]
        p1 = d.xpos[o1] + d.xmat[o1].reshape(3, 3) @ ed[0:3]
        p2 = d.xpos[o2] + d.xmat[o2].reshape(3, 3) @ ed[3:6]
        gap = max(gap, 1000 * np.linalg.norm(p1 - p2))
    return gap

r = mujoco.Renderer(m, height=700, width=1244)
cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
cam.lookat = np.array([0.0, 0.0, 0.28])

def frame(azim, elev, dist, cap, gap):
    cam.azimuth, cam.elevation, cam.distance = azim, elev, dist
    r.update_scene(d, camera=cam)
    im = Image.fromarray(r.render())
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, im.width, 30], fill=(14, 16, 20))
    dr.text((12, 8), cap, fill=(236, 240, 244))
    dr.rectangle([0, im.height - 24, im.width, im.height], fill=(14, 16, 20))
    dr.text((12, im.height - 18),
            "analytic closed-chain pose (leg2d.Kite2D)   loop gap %.4f mm   base z %+.4f m   "
            "733/733 CAD solids   2.79 M triangles   20.00 kg" % (gap, d.qpos[FREE + 2]),
            fill=(198, 206, 214))
    return np.asarray(im)

w = imageio.get_writer(OUT, fps=FPS, codec="libx264", quality=8,
                       macro_block_size=None, ffmpeg_params=["-pix_fmt", "yuv420p"])
n = int(SEC * FPS)
g = pose(0.0, 0.0)
print("segment 1 turntable, gap %.4f mm" % g)
for i in range(n):
    w.append_data(frame(i * 360.0 / n, 14, 1.75,
        "RM2025 serial-leg infantry - MuJoCo plant AFTER the mesh fix  (stand pose)", g))
print("segment 2 crank sweep")
for i in range(n):
    t = i / float(n - 1)
    cr = -0.50 + 1.00 * (0.5 - 0.5 * np.cos(2 * np.pi * t))
    g = pose(0.0, cr)
    w.append_data(frame(58, 12, 1.55,
        "crank sweep (knee drive) at thigh = 0.00 rad :  crank %+0.2f rad" % cr, g))
print("segment 3 thigh sweep")
for i in range(n):
    t = i / float(n - 1)
    th = -0.40 + 0.80 * (0.5 - 0.5 * np.cos(2 * np.pi * t))
    g = pose(th, 0.0)
    w.append_data(frame(238, 12, 1.55,
        "thigh sweep (hip drive) at crank = 0.00 rad :  thigh %+0.2f rad" % th, g))
w.close()
print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")