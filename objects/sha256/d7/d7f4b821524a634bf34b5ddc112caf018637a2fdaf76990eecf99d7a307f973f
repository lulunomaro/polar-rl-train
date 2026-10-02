"""Independent cross-check of the corrected base-link mass properties.

build_cc.py used to force the chassis centre of mass to (0,0,0) (an anchor bug), and now
computes com=(0, 0.9, 239.1) mm with a 14-18x larger inertia tensor.  Before trusting that,
recompute the same centre of mass from the TESSELLATED meshes that are actually rendered,
using trimesh instead of OpenCascade's GProp.  Two independent geometry kernels agreeing
means the parallel-axis fix is real and not an artefact of bad per-solid data.

Also reports how many base solids are NOT watertight - those are the shells whose GProp
volume can lie, and they are the same 片状化 leftovers that still need sewing.
"""
import json, os, re, sys
import numpy as np
import trimesh
import yaml

ROOT = r"D:/claude2/fangzhen"
CAD = os.path.join(ROOT, "cad")
spec = yaml.safe_load(open(os.path.join(ROOT, "robot/vehicle.spec.yaml"), encoding="utf-8"))
MAN = json.load(open(os.path.join(CAD, "out/vehicle/manifest.json"), encoding="utf-8"))
solids = MAN["solids"] if "solids" in MAN else None
by_key = {"%s|%s" % (s["id"], s["product"]): s for s in solids}
by_id = {s["id"]: s for s in solids}
rows = json.load(open(os.path.join(ROOT, "robot/out_cc/visual_manifest_cc.json"),
                      encoding="utf-8"))


def rho_of(text):
    for rule in spec["density_rules"]:
        if re.search(rule["match"], text, re.I):
            return float(rule["rho"])
    return float(spec["density_rules"][-1]["rho"])


def com_from_triangles(V, F):
    """Volume centroid of a closed triangle soup (tetrahedron decomposition about origin)."""
    v0 = V[F[:, 0]].astype(np.float64)
    v1 = V[F[:, 1]].astype(np.float64)
    v2 = V[F[:, 2]].astype(np.float64)
    vol = np.einsum("ij,ij->i", v0, np.cross(v1, v2)) / 6.0
    c = (v0 + v1 + v2) / 4.0
    tot = vol.sum()
    if abs(tot) < 1e-9:
        return None, 0.0
    return (c * vol[:, None]).sum(0) / tot, tot


sel = [r for r in rows if r["body"] == "base"]
print("base rows in the visual manifest:", len(sel))
num = np.zeros(3); den = 0.0
num_occ = np.zeros(3); den_occ = 0.0
bad = []
notw = 0
for r in sel:
    s = by_id.get(r["id"])
    if s is None:
        bad.append(("nomanifest", r["id"], "")); continue
    p = os.path.join(CAD, "out", r["_dir"], "meshes", r["used"])
    try:
        me = trimesh.load(p, process=False)
    except Exception as e:
        bad.append(("load", r["id"], str(e)[:40])); continue
    rho = rho_of(s["path"] + "|" + s["product"]) / 1e9      # kg/mm^3
    if not me.is_watertight:
        notw += 1
    cm, vol = com_from_triangles(np.asarray(me.vertices), np.asarray(me.faces))
    if cm is None or vol <= 0:
        bad.append(("degenerate", r["id"], "")); continue
    dm = vol * rho
    num += dm * cm; den += dm
    num_occ += s["volume_mm3"] * rho * np.array(s["com_world"], float)
    den_occ += s["volume_mm3"] * rho
print("mesh-based COM  %s mm   (mass %.2f kg)" % (np.round(num / den, 1), den))
print("GProp-based COM %s mm   (mass %.2f kg)" % (np.round(num_occ / den_occ, 1), den_occ))
print("difference      %s mm" % np.round(num / den - num_occ / den_occ, 2))
print("not watertight: %d / %d   unusable: %d" % (notw, len(sel), len(bad)))
for b in bad[:10]:
    print("   !", b)

