"""Ours vs theirs: the linkage skeleton, both drawn from the validated analytic model,
same scale, three crank angles each."""
import sys, os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
sys.path.insert(0, r"D:/claude2/fangzhen/scripts")
from leg2d import Kite2D, CAD
REF = dict(knee=np.array([-210.0, 0.0]), axle=np.array([6.61, -124.83]),
           P2=np.array([112.65, 13.05]), P1=np.array([-113.40, -0.01]),
           apex=np.array([3.86, -66.90]), P3=np.array([-161.19, 46.97]),
           Q=np.array([-257.79, 46.97]), S1=np.array([2.36, -44.94]),
           S2=np.array([-162.42, -22.92]))
HIP = np.zeros(2)
SEGS = [("thigh (rear1)", "hip", "knee", "k", 3.0), ("shank (rear2)", "knee", "axle", "k", 3.0),
        ("crank (front1)", "hip", "P2", "tab:blue", 2.2), ("front2", "P2", "apex", "tab:blue", 2.2),
        ("front3", "apex", "P1", "tab:red", 2.2), ("front3 arm", "apex", "P3", "tab:red", 2.2),
        ("front4", "P3", "Q", "tab:green", 2.2), ("gas spring", "S1", "S2", "0.45", 1.6),
        ("thigh pin P1", "hip", "P1", "tab:red", 1.2),
        ("hip->axle (leg line)", "hip", "axle", "tab:purple", 1.0)]
fig, axes = plt.subplots(1, 2, figsize=(13.5, 7.4), sharex=True, sharey=True)
for ax, (pts, title, lam) in zip(axes, ((CAD, "OURS  整车总装.STEP  (lambda=%.3f)" % (np.linalg.norm(CAD["P1"]) / np.linalg.norm(CAD["knee"])), 0),
                                        (REF, "SJTU/SCUT reference wheelbipeV14_2 (lambda=%.3f)" % (np.linalg.norm(REF["P1"]) / np.linalg.norm(REF["knee"])), 1))):
    L = Kite2D(pts, "x")
    for tc, st in ((-0.45, ":"), (0.0, "-"), (0.45, ":")):
        r = L.solve(0.0, tc)
        for nm, a, b, c, w in SEGS:
            pa = HIP if a == "hip" else r[a]; pb = r[b]
            ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color=c, ls=st, lw=w if st == "-" else 1.4,
                    alpha=1.0 if st == "-" else 0.55, label=nm if tc == 0.0 else None)
        ax.plot(r["axle"][0], r["axle"][1], "o", ms=30, mfc="none", mec="k", alpha=0.5 if st == "-" else 0.3)
        for k in ("P1", "P2", "apex", "P3", "Q", "knee", "S1", "S2"):
            ax.plot(r[k][0], r[k][1], ".", ms=7, color="crimson" if st == "-" else "0.5")
    r = L.solve(0.0, 0.0)
    ax.plot(*HIP, "ks", ms=9); ax.annotate("hip (both motors)", HIP, xytext=(18, 14), textcoords="offset points", fontsize=9)
    ax.annotate("P1 = hip + %.3f*(knee-hip)\n-> on the thigh centre line" % (np.linalg.norm(pts["P1"]) / np.linalg.norm(pts["knee"])),
                r["P1"], xytext=(-150, -30), textcoords="offset points", fontsize=8, color="tab:red",
                arrowprops=dict(arrowstyle="->", color="tab:red", lw=.8))
    ax.annotate("APEX = hip + %.3f*(axle-hip)\n-> the *similar* image of the axle" % (np.linalg.norm(pts["apex"]) / np.linalg.norm(pts["axle"])),
                r["apex"], xytext=(24, -6), textcoords="offset points", fontsize=8, color="tab:blue",
                arrowprops=dict(arrowstyle="->", color="tab:blue", lw=.8))
    ax.annotate("knee (passive)", r["knee"], xytext=(-96, 26), textcoords="offset points", fontsize=8,
                arrowprops=dict(arrowstyle="->", color="k", lw=.8))
    ax.annotate("wheel axle", r["axle"], xytext=(10, 30), textcoords="offset points", fontsize=8,
                arrowprops=dict(arrowstyle="->", color="k", lw=.8))
    ax.annotate("Q (front4->shank)", r["Q"], xytext=(-40, -46), textcoords="offset points", fontsize=8,
                arrowprops=dict(arrowstyle="->", color="tab:green", lw=.8))
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal"); ax.grid(alpha=.25); ax.legend(fontsize=7.5, loc="lower left")
axes[0].set_xlim(-330, 200); axes[0].set_ylim(-340, 130)
fig.suptitle("相似连杆 / kite four-bar leg: solid = CAD zero pose, dotted = crank -0.45 / +0.45 rad", fontsize=11)
fn = r"D:/claude2/fangzhen/docs/crops/leg_skeleton_compare.png"
fig.savefig(fn, dpi=115, bbox_inches="tight"); print("wrote", fn)
