"""Side-by-side visual comparison of OUR closed-chain leg against the SJTU/SCUT
reference leg: real mesh renders at three crank angles + the linkage schematic drawn
from the validated analytic solver, and the SJTU PDF's own diagrams extracted at full
resolution."""
import os, sys, numpy as np, mujoco
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD
REF = dict(knee=np.array([-210.0, 0.0]), axle=np.array([6.61, -124.83]),
           P2=np.array([112.65, 13.05]), P1=np.array([-113.40, -0.01]),
           apex=np.array([3.86, -66.90]), P3=np.array([-161.19, 46.97]),
           Q=np.array([-257.79, 46.97]), S1=np.array([2.36, -44.94]),
           S2=np.array([-162.42, -22.92]))
OUT = r"D:/claude2/fangzhen/docs/crops"; os.makedirs(OUT, exist_ok=True)
PAIRS = [("ours", r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml", CAD, "key"),
         ("ref",  r"D:/claude2/fangzhen/refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/wheelbipeV14_2/mjcf/scene.xml", REF, None)]
CRANKS = (-0.45, 0.0, 0.45)

def render(tag, xml, pts, keymode):
    m = mujoco.MjModel.from_xml_path(xml); d = mujoco.MjData(m)
    if keymode == "key":
        k = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "stand")
        mujoco.mj_resetDataKeyframe(m, d, k)
    else:
        # reference scene: start from its own keyframe if any, else lift the base
        if m.nkey: mujoco.mj_resetDataKeyframe(m, d, 0)
        d.qpos[2] = max(d.qpos[2], 0.62)
    def J(n): return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
    legs = [k for k in ("front1", "rear1", "rear2", "front2", "front3", "front4", "spring1", "spring2")]
    adr = {}
    for side in ("left", "right"):
        for k in legs:
            j = J("%s_%s_joint" % (side, k))
            if j >= 0: adr[(side, k)] = m.jnt_qposadr[j]
    L = Kite2D(pts, tag)
    r = mujoco.Renderer(m, 420, 460)
    cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.azimuth, cam.elevation = (0.0 if tag == "ours" else 180.0), -6.0
    imgs, figs = [], []
    for tc in CRANKS:
        mujoco.mj_resetData(m, d)
        if keymode == "key":
            mujoco.mj_resetDataKeyframe(m, d, mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "stand"))
        elif m.nkey:
            mujoco.mj_resetDataKeyframe(m, d, 0)
        q = L.qpos_full(0.0, tc)
        for side in ("left", "right"):
            for k, v in ((kk, q[kk]) for kk in legs):
                a = adr.get((side, k))
                if a is not None:
                    d.qpos[a] = v / 1000.0 if k == "spring2" else -v
        mujoco.mj_forward(m, d)
        cam.lookat[:] = [0.0, -0.22 if tag == 'ours' else 0.22, 0.12]; cam.distance = 0.95
        r.update_scene(d, camera=cam); imgs.append(r.render())
        fig = plt.figure(figsize=(3.1, 3.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
        plot_skel(ax, L, tc, tag)
        fig.savefig(os.path.join(OUT, "skel_%s_%+0.2f.png" % (tag, tc)), dpi=110); plt.close(fig)
    return imgs

ORDER = ["knee", "axle", "P3", "Q", "apex", "P1", "P2", "S1", "S2"]
def plot_skel(ax, L, tc, tag):
    for tt in (-0.35, 0.0, 0.35) if tag == "ours" else (0.0,):
        q = L.qpos_full(tt, tc); r = q["pts"]
        a = 0.35 + 0.3 * (tt + 0.35) / 0.7
        seg = [(np.zeros(2), r["P2"], "front1 crank"), (r["P2"], r["apex"], "front2"),
               (r["apex"], r["P1"], "front3"), (r["P1"], np.zeros(2), "front3->thigh"),
               (r["apex"], r["P3"], "front3 arm"), (r["P3"], r["Q"], "front4"),
               (r["Q"], r["knee"], "shank part"), (np.zeros(2), r["knee"], "thigh"),
               (r["knee"], r["axle"], "shank"), (r["S1"], r["S2"], "gas spring")]
        for p0, p1, nm in seg:
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], "-", lw=1.6, alpha=a,
                    color="0.35" if nm in ("thigh", "shank", "shank part") else "tab:blue")
        for k in ORDER:
            ax.plot(r[k][0], r[k][1], "o", ms=4, color="tab:red", alpha=a)
        ax.plot(r["axle"][0], r["axle"][1], "o", ms=14, mfc="none", mec="k", alpha=a)
    ax.plot([0], [0], "s", ms=6, color="k"); ax.text(4, 6, "hip", fontsize=8)
    ax.set_xlim(-330, 190); ax.set_ylim(-330, 110); ax.set_aspect("equal")
    ax.set_title("%s  crank=%+.2f rad" % (tag, tc), fontsize=9)
    ax.grid(alpha=.25)

res = {}
for tag, xml, pts, keymode in PAIRS:
    try:
        res[tag] = render(tag, xml, pts, keymode)
    except Exception as ex:
        print("!! render failed for", tag, type(ex).__name__, ex)
from PIL import Image
W = 460; H = 420
rows = []
for tag in ("ours", "ref"):
    if tag not in res: continue
    strip = []
    for i, im in enumerate(res[tag]):
        base = Image.fromarray(im)
        sk = Image.open(os.path.join(OUT, "skel_%s_%+0.2f.png" % (tag, CRANKS[i]))).resize((W // 2, H))
        combo = Image.new("RGB", (W + W // 2, H), "white")
        combo.paste(base, (0, 0)); combo.paste(sk, (W, 0))
        strip.append(combo)
    rows.append((tag, strip))
w = max(s.width for t, ss in rows for s in ss); h = sum(sum(s.height for s in ss[:1]) for t, ss in rows)
tot = Image.new("RGB", (w * 3 + 20, h * len(rows) + 30), "white")
y = 10
for tag, strip in rows:
    x = 10
    for s in strip:
        tot.paste(s, (x, y)); x += s.width + 10
    y += strip[0].height + 10
tot.save(os.path.join(OUT, "leg_compare_render_vs_skel.png"))
print("wrote", os.path.join(OUT, "leg_compare_render_vs_skel.png"), tot.size)

# extract the SJTU PDF's own diagrams at native resolution
import pymupdf
doc = pymupdf.open(r"C:/Users/lulunomaro/Desktop/RM2025串联腿平衡步兵机械开源 -上海交通大学 交龙战队 (1).pdf")
for pno in (5, 6, 7, 9, 10):
    p = doc[pno - 1]
    for i, info in enumerate(p.get_image_info(xrefs=True)):
        pix = pymupdf.Pixmap(doc, info["xref"])
        if pix.n - pix.alpha > 3: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        if pix.width < 200 or pix.height < 150: continue
        fn = os.path.join(OUT, "sjtu_p%02d_img%d_%dx%d.png" % (pno, i, pix.width, pix.height))
        pix.save(fn); print("  ", fn)
