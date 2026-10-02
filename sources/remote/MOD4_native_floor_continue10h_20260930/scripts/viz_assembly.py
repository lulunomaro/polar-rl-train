"""Render top/front/side scatter views of an extracted STEP assembly.

Usage: python viz_assembly.py <manifest_dir> <out.png> [--groups path2|product|id|color]
"""
import argparse, collections, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh

ap = argparse.ArgumentParser()
ap.add_argument("mdir")
ap.add_argument("out")
ap.add_argument("--groups", default="path2", help="path2 | product | color | id")
ap.add_argument("--samples", type=int, default=1200)
ap.add_argument("--maxsolids", type=int, default=6000)
args = ap.parse_args()

m = json.load(open(os.path.join(args.mdir, "manifest.json"), encoding="utf8"))
sols = m["solids"][:args.maxsolids]


def group_key(s):
    if args.groups == "product":
        return s["product"]
    if args.groups == "id":
        return s["id"]
    if args.groups == "color":
        return str(s.get("color"))
    parts = s["path"].split("/")
    return "/".join(parts[:2]) if len(parts) > 1 else parts[0]


groups = collections.OrderedDict()
P = []
for s in sols:
    k = group_key(s)
    g = groups.setdefault(k, [0, 0.0])
    g[0] += 1
    g[1] += s["volume_mm3"]
    try:
        me = trimesh.load(os.path.join(args.mdir, "meshes", s["obj"]), process=False)
    except Exception:
        continue
    if len(me.faces) == 0:
        continue
    tri = np.asarray(me.faces)
    verts = np.asarray(me.vertices)
    n = min(args.samples, len(tri))
    idx = np.linspace(0, len(tri) - 1, n).astype(int)
    a, b, c = verts[tri[idx, 0]], verts[tri[idx, 1]], verts[tri[idx, 2]]
    r1 = np.random.rand(n, 1)
    r2 = np.random.rand(n, 1)
    mask = r1 + r2 > 1
    r1[mask] = 1 - r1[mask]
    r2[mask] = 1 - r2[mask]
    pts = a * (1 - r1 - r2) + b * r1 + c * r2
    P.append((k, pts))

byp = collections.defaultdict(list)
for k, pts in P:
    byp[k].append(pts)
names = list(groups.keys())
print("groups: %d, solids: %d" % (len(names), len(sols)))
cmap = matplotlib.colormaps.get_cmap("tab20")
if len(names) > 20:
    cmap2 = matplotlib.colormaps.get_cmap("hsv")
    cols = [cmap2(i / max(1, len(names))) for i in range(len(names))]
else:
    cols = [cmap(i / 20) for i in range(len(names))]
colmap = dict(zip(names, cols))

views = [("top  X-Y", 0, 1), ("front X-Z", 0, 2), ("side Y-Z", 1, 2)]
fig, axes = plt.subplots(1, 3, figsize=(24, 8))
allpts = np.vstack([p for _, p in P]) if P else np.zeros((1, 3))
for ax, (title, i, j) in zip(axes, views):
    for gi, k in enumerate(names):
        pts = np.vstack(byp[k]) if byp.get(k) else None
        if pts is None or not len(pts):
            continue
        ax.scatter(pts[:, i], pts[:, j], s=1.0, c=[colmap[k]], linewidths=0)
        cen = pts.mean(0)
        ax.text(cen[i], cen[j], str(gi), fontsize=8, color="k", ha="center", va="center",
                bbox=dict(fc="white", ec="none", alpha=0.6, pad=0.6))
    ax.set_title(title + "  (mm)", fontsize=11)
    ax.set_aspect("equal")
    ax.grid(alpha=0.25)
    ax.set_xlabel("xyz"[i])
    ax.set_ylabel("xyz"[j])
    lo, hi = allpts[:, i].min() - 20, allpts[:, i].max() + 20
    ax.set_xlim(lo, hi)
    lo, hi = allpts[:, j].min() - 20, allpts[:, j].max() + 20
    ax.set_ylim(lo, hi)
fig.savefig(args.out, dpi=100, bbox_inches="tight")

fig2, ax2 = plt.subplots(figsize=(15, max(2.0, 0.20 * len(names))))
ax2.axis("off")
open(args.out + ".groups.txt", "w", encoding="utf8").write("\n".join("%d\t%s\tn=%d\tvol=%.0fcm3" % (i, k, groups[k][0], groups[k][1] / 1000) for i, k in enumerate(names)))
ax2.text(0.0, 1.0, "see " + args.out + ".groups.txt for names", va="top", fontsize=8)
fig2.savefig(args.out + ".legend.png", dpi=110, bbox_inches="tight")
print("wrote", args.out)
print("bbox_min", allpts.min(0).round(1), "bbox_max", allpts.max(0).round(1))



