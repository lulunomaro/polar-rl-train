"""Side-by-side visual comparison, proven camera setup, our closed-chain leg vs the
SJTU/SCUT reference leg at identical crank angles (analytic IK drives both)."""
import os, sys, numpy as np, mujoco
from PIL import Image, ImageDraw
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD
REF = dict(knee=np.array([-210.0, 0.0]), axle=np.array([6.61, -124.83]),
           P2=np.array([112.65, 13.05]), P1=np.array([-113.40, -0.01]),
           apex=np.array([3.86, -66.90]), P3=np.array([-161.19, 46.97]),
           Q=np.array([-257.79, 46.97]), S1=np.array([2.36, -44.94]),
           S2=np.array([-162.42, -22.92]))
OUT = r"D:/claude2/fangzhen/docs/crops"
LEGS = ("front1", "rear1", "rear2", "front2", "front3", "front4", "spring1", "spring2")
CASES = [("OURS  rm_vehicle_cc (from 整车总装.STEP)", r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml", CAD, 0.075, 0.16, 1.05, 0.0),
         ("SJTU  wheelbipeV14_2 (reference)", r"D:/claude2/fangzhen/refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/wheelbipeV14_2/mjcf/scene_compare.xml", REF, None, 0.45, 1.05, 180.0)]
tiles = []
for tag, xml, pts, basez, lz, dist, az in CASES:
    m = mujoco.MjModel.from_xml_path(xml); d = mujoco.MjData(m); L = Kite2D(pts, tag)
    def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
    adr = {}
    for side in ("left", "right"):
        for k in LEGS:
            j = J("%s_%s_joint" % (side, k))
            if j >= 0: adr[(side, k)] = m.jnt_qposadr[j]
    r = mujoco.Renderer(m, 470, 560)
    vopt = mujoco.MjvOption(); vopt.geomgroup[:] = (1, 1, 1, 1, 0, 1)
    cam = mujoco.MjvCamera(); cam.distance = dist; cam.azimuth = az; cam.elevation = -6
    for tc in (-0.45, 0.0, 0.45):
        mujoco.mj_resetData(m, d)
        if basez is not None: d.qpos[2] = basez
        q = L.qpos_full(0.0, tc)
        for (side, k), a in adr.items():
            d.qpos[a] = q[k] / 1000.0 if k == "spring2" else -q[k]
        mujoco.mj_forward(m, d)
        cam.lookat = [0.0, 0.0, lz]
        r.update_scene(d, camera=cam, scene_option=vopt)
        im = Image.fromarray(r.render()); dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, im.width, 22], fill=(255, 255, 255))
        dr.text((5, 6), "%s   crank %+0.2f rad" % (tag, tc), fill=(0, 0, 0))
        tiles.append(im)
W, H = tiles[0].size
sheet = Image.new("RGB", (W * 3 + 20, H * 2 + 30), "white")
for i, t in enumerate(tiles):
    row, col = divmod(i, 3); sheet.paste(t, (col * (W + 10), row * (H + 10) + 26))
ImageDraw.Draw(sheet).text((6, 6), "side view; both legs driven by the SAME analytic closed-chain IK", fill=(0, 0, 0))
fn = os.path.join(OUT, "leg_side_compare.png"); sheet.save(fn); print("wrote", fn, sheet.size)
