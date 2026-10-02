"""Classify extracted STEP solids into functional robot groups and find wheel axes.

Usage: python analyze_links.py <manifest_dir> [--report out.txt]
"""
import argparse, collections, json, os, re, sys
import numpy as np
import trimesh

ap = argparse.ArgumentParser()
ap.add_argument("mdir")
ap.add_argument("--report", default="")
ap.add_argument("--wheel-rmin", type=float, default=40.0)
ap.add_argument("--samples", type=int, default=4000)
args = ap.parse_args()

m = json.load(open(os.path.join(args.mdir, "manifest.json"), encoding="utf8"))
S = m["solids"]

# --- 1. keyword classification of the assembly tree -------------------------------
kw = collections.Counter()
for s in S:
    kw[s["product"]] += s["volume_mm3"]

RULES = [
    ("wheel",   r"轮胎|轮毂|轮子|轮辋|胎|tyre|tire|wheel"),
    ("gimbal",  r"鹅颈|云台|yaw|pitch轴|发射"),
    ("leg",     r"髋腿|腿|大腿|小腿|膝关节|髋关节"),
    ("motor",   r"电机|3508|6020|2006|RS02|GM\d|马达"),
    ("armor",   r"装甲|保险杠|外壳|蒙皮"),
    ("frame",   r"横梁|纵梁|井字|铝条|铝柱|板|架|舱|盖|座|支架|安装"),
    ("fastener", r"螺母|螺栓|螺钉|垫圈|垫片|销|轴承|卡簧|挡圈|柱"),
]


def classify(s):
    txt = s["path"] + "|" + s["product"]
    for name, pat in RULES:
        if re.search(pat, txt, re.I):
            return name
    return "other"


def side_of(s):
    p = s["path"]
    if "Mirror" in p or "mirror" in p or "镜像" in p:
        return "R"
    return "L"


def load(s):
    return trimesh.load(os.path.join(args.mdir, "meshes", s["obj"]), process=False)


def wheel_metrics(V):
    """PCA of vertices -> (center, axis(unit), radial std, r_max, thickness along axis)."""
    c = V.mean(0)
    X = V - c
    cov = np.cov(X.T);
    w, vecs = np.linalg.eigh(cov)
    order = np.argsort(w)[::-1]
    vecs = vecs[:, order]
    proj = X @ vecs
    radial = np.hypot(proj[:, 1], proj[:, 2])
    out = []
    for a in range(3):
        u = vecs[:, a]
        h = proj[:, a]
        r = np.linalg.norm(proj - np.outer(h, u), axis=1)
        out.append((np.std(r) / (np.ptp(h) + 1e-9), u, h, r))
    out.sort(key=lambda z: z[0])
    ratio, u, h, r = out[0]
    return dict(center=c.tolist(), axis=u.tolist(), axial_len=float(np.ptp(h)),
                r_mean=float(r.mean()), r_max=float(r.max()),
                roundness=float(np.std(r) / (r.mean() + 1e-9)), thin=float(np.ptp(h) / (2 * r.max() + 1e-9)))


rows = []
wheelish = []
for s in S:
    g = classify(s)
    s["group"] = g
    s["side"] = side_of(s)
    if s["ntris"] < 8:
        continue
    me = load(s)
    V = np.asarray(me.vertices)
    if len(V) > args.samples:
        V = V[np.linspace(0, len(V) - 1, args.samples).astype(int)]
    wm = wheel_metrics(V)
    s["pca"] = {k: wm[k] for k in ("center", "axis", "axial_len", "r_mean", "r_max", "roundness", "thin")}
    if wm["r_max"] > args.wheel_rmin and wm["thin"] < 0.75 and wm["roundness"] < 0.35:
        wheelish.append(s)
    rows.append(s)

grp = collections.OrderedDict()
for s in rows:
    k = (s["group"], s["side"])
    d = grp.setdefault(k, dict(n=0, vol=0.0, lo=[1e9] * 3, hi=[-1e9] * 3, names=collections.Counter()))
    d["n"] += 1
    d["vol"] += s["volume_mm3"]
    d["lo"] = [min(a, b) for a, b in zip(d["lo"], s["bbox_world"][:3])]
    d["hi"] = [max(a, b) for a, b in zip(d["hi"], s["bbox_world"][3:])]
    d["names"][s["product"]] += 1

lines = []
lines.append("solids=%d  tris=%d  union=%s" % (len(S), m["n_tris"], m["union_bbox"]))
lines.append("")
lines.append("== groups (classification x side) ==")
lines.append("%-9s %-3s %-5s %10s  %-42s %s" % ("group","side","n","vol_cm3","bbox_lo","bbox_hi"))
for (g, sd), d in sorted(grp.items(), key=lambda kv: -kv[1]["vol"]):
    lines.append("%-9s %-3s %-5d %10.0f  [%7.1f %7.1f %7.1f] [%7.1f %7.1f %7.1f]" % (
        g, sd, d["n"], d["vol"] / 1000, d["lo"][0], d["lo"][1], d["lo"][2], d["hi"][0], d["hi"][1], d["hi"][2]))

lines.append("")
lines.append("== wheel candidates (PCA cylinder fit) ==")
lines.append("%-6s %-30s %8s %8s %7s %7s  %-34s %s" % (
    "id", "product", "r_max", "r_mean", "thick", "round", "center", "axis"))
for s in sorted(wheelish, key=lambda z: -z["volume_mm3"]):
    p = s["pca"]
    lines.append("%-6s %-30s %8.1f %8.1f %7.1f %7.2f  [%7.1f %7.1f %7.1f] [%6.2f %6.2f %6.2f] %s" % (
        s["id"], s["product"][:30], p["r_max"], p["r_mean"], p["axial_len"], p["roundness"],
        p["center"][0], p["center"][1], p["center"][2],
        p["axis"][0], p["axis"][1], p["axis"][2], s["path"][-40:]))

lines.append("")
lines.append("== top products by volume ==")
prods = collections.OrderedDict()
for s in S:
    d = prods.setdefault(s["product"], dict(n=0, vol=0.0, g=s["group"]))
    d["n"] += 1; d["vol"] += s["volume_mm3"]
for p, d in sorted(prods.items(), key=lambda kv: -kv[1]["vol"])[:60]:
    lines.append("%-46s n=%-4d %9.0f cm3  %s" % (p[:46], d["n"], d["vol"] / 1000, d["g"]))

txt = "\n".join(lines)
out = args.report or os.path.join(args.mdir, "analysis.txt")
open(out, "w", encoding="utf8").write(txt)
json.dump(rows, open(os.path.join(args.mdir, "solids_classified.json"), "w", encoding="utf8"), ensure_ascii=False)
print("wrote", out, "wheel candidates:", len(wheelish))
