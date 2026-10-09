"""Read-only audit of supplied RM terrain, original B-Rep, and delivered mesh.

Writes only this audit directory. No training, launch, asset, or budget writes.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import trimesh
from scipy.signal import find_peaks
from scipy.optimize import minimize_scalar
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_Label
from OCP.collections import Sequence_TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_BSplineCurve

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
font = Path("C:/Windows/Fonts/msyh.ttc")
fontManager.addfont(str(font))
plt.rcParams["font.family"] = FontProperties(fname=str(font)).get_name()
plt.rcParams["axes.unicode_minus"] = False
source = json.loads((ROOT / "rmuc2026_training/reports/source.json").read_text())
origin = np.array(source["cad_origin_m"])
parts = json.loads((ROOT / "rmuc2026_work/extracted/parts.json").read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def load_part(n):
    with np.load(ROOT / f"rmuc2026_work/extracted/part_{n:03}.npz") as a:
        return trimesh.Trimesh(a["vertices"] * .001 - origin, a["faces"], process=False)


with np.load(ROOT / "rmuc2026_training/data/arena_collision.npz") as a:
    collision = trimesh.Trimesh(a["vertices"], a["faces"], process=False)


def height(mesh, xy):
    xy = np.asarray(xy)
    loc, rid, _ = mesh.ray.intersects_location(
        np.c_[xy, np.full(len(xy), 2.)], np.tile([0., 0., -1.], (len(xy), 1)),
        multiple_hits=True)
    z = np.full(len(xy), -np.inf)
    np.maximum.at(z, rid, loc[:, 2])
    z[~np.isfinite(z)] = np.nan
    return z


# Read original terrain B-Rep without remeshing or rewriting the source subset.
subset = ROOT / "rmuc2026_work/terrain_subset.stp"
subset_sha = sha(subset)
r = STEPCAFControl_Reader()
r.SetNameMode(True)
assert int(r.ReadFile(str(subset))) == 1
doc = TDocStd_Document(TCollection_ExtendedString("RM read-only audit"))
assert r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
roots = Sequence_TDF_Label()
st.GetFreeShapes(roots)
wanted = {"BREP_192", "BREP_220", "BREP_424", "BREP_1", "BREP_3", "BREP_5", "BREP_7"}
shapes = {}


def walk(label, parent):
    loc = parent.Multiplied(st.GetLocation_s(label))
    definition = label
    if st.IsReference_s(label):
        definition = TDF_Label()
        st.GetReferredShape_s(label, definition)
    a = TDataStd_Name()
    name = a.Get().ToExtString() if definition.FindAttribute(TDataStd_Name.GetID_s(), a) else ""
    kids = Sequence_TDF_Label()
    st.GetComponents_s(definition, kids)
    if kids.Length():
        for k in range(1, kids.Length() + 1):
            walk(kids.Value(k), loc)
    elif name in wanted:
        shapes[name] = st.GetShape_s(definition).Moved(loc)


for k in range(1, roots.Length() + 1):
    walk(roots.Value(k), TopLoc_Location())
assert set(shapes) == wanted


def section_curves(name, world_y):
    plane = gp_Pln(gp_Pnt(0, (world_y + origin[1]) * 1000, 0), gp_Dir(0, 1, 0))
    sec = BRepAlgoAPI_Section(shapes[name], plane, False)
    sec.ComputePCurveOn1(True)
    sec.Approximation(True)
    sec.Build()
    assert sec.IsDone()
    ex = TopExp_Explorer(sec.Shape(), TopAbs_EDGE)
    curves = []
    while ex.More():
        curves.append(BRepAdaptor_Curve(TopoDS.Edge(ex.Current())))
        ex.Next()
    return curves


def point(curve, t):
    p = curve.Value(float(t))
    return np.array([p.X(), p.Y(), p.Z()]) * .001 - origin


result = {"scope": "Static geometry audit; no new GPU, SDK, PPO, hardware measurement or training change.",
          "cad": source, "original_cad_sha256_rechecked": sha(Path(source["source"])),
          "terrain_subset_sha256": subset_sha,
          "delivered_collision_sha256": sha(ROOT / "rmuc2026_training/data/arena_collision.npz"),
          "rough": [], "outer_curbs": [], "correction": {
              "human_arrow_target": "Central island outer left/right continuous curb strips and transitions",
              "old_part383_inner_lip_is_different_feature": True}}
assert result["original_cad_sha256_rechecked"] == source["sha256"]

fig, axs = plt.subplots(2, 1, figsize=(13, 7.5), layout="constrained")
for ax, (n, name, y) in zip(axs, [(181, "BREP_220", 6.45), (153, "BREP_192", -6.45)]):
    curves = section_curves(name, y)
    curved = [c for c in curves if c.GetType() == GeomAbs_BSplineCurve]
    assert len(curved) == 1
    c = curved[0]
    ts = np.linspace(c.FirstParameter(), c.LastParameter(), 20001)
    p = np.array([point(c, t) for t in ts])
    ii = np.argsort(p[:, 0]); p = p[ii]; ts = ts[ii]
    peaks, _ = find_peaks(p[:, 2], prominence=.025)
    troughs, _ = find_peaks(-p[:, 2], prominence=.025)

    def extrema(indices, sign):
        rows = []
        for i in indices:
            lo, hi = sorted([ts[max(i - 4, 0)], ts[min(i + 4, len(ts) - 1)]])
            opt = minimize_scalar(lambda t: sign * point(c, t)[2], bounds=(lo, hi), method="bounded",
                                  options={"xatol": 1.e-9})
            rows.append(point(c, opt.x))
        return np.array(rows)

    pk = extrema(peaks, -1)
    tr = extrema(troughs, 1)
    local_height = float((pk[:, 2].max() - tr[:, 2].min()) * np.cos(np.deg2rad(1.5)))
    xy = p[::10, :2]
    delivered = height(collision, xy)
    original_mesh = height(load_part(n), xy)
    row = {"part": n, "brep": name, "section_world_y_m": y,
           "cad_exact_peak_count": len(pk), "cad_exact_trough_count": len(tr),
           "cad_exact_peaks_m": pk.tolist(), "cad_exact_troughs_m": tr.tolist(),
           "cad_exact_peak_spacing_mm": (np.diff(pk[:, 0]) * 1000).tolist(),
           "cad_exact_peak_to_trough_normal_mm": local_height * 1000,
           "cad_exact_peak_to_trough_vertical_mm": float((pk[:, 2].max() - tr[:, 2].min()) * 1000),
           "cad_section_span_x_mm": float(np.ptp(p[:, 0]) * 1000),
           "delivered_vs_exact_section_max_abs_mm": float(np.nanmax(np.abs(delivered - p[::10, 2])) * 1000),
           "original_tessellation_vs_exact_section_max_abs_mm": float(np.nanmax(np.abs(original_mesh - p[::10, 2])) * 1000),
           "scope_error_note": "These are finite line samples, not a complete Hausdorff or SDK collision proof."}
    result["rough"].append(row)
    ax.plot((p[:, 0] - p[0, 0]) * 1000, (p[:, 2] - tr[:, 2].min()) * 1000, label="原始CAD B-Rep剖面", lw=1.8)
    ax.plot((xy[:, 0] - p[0, 0]) * 1000, (delivered - tr[:, 2].min()) * 1000,
            label="交付碰撞网格", lw=.9, alpha=.8)
    ax.scatter((pk[:, 0] - p[0, 0]) * 1000, (pk[:, 2] - tr[:, 2].min()) * 1000, s=14, color="#d95721")
    ax.set_title(f"{'蓝侧' if n == 181 else '红侧'}起伏路 / part {n}；沿X跨凸起，y={y:g}m")
    ax.set_xlabel("沿横断面距离 / mm")
    ax.set_ylabel("相对谷底竖直高度 / mm")
    ax.grid(alpha=.2); ax.legend(loc="lower right")
fig.savefig(HERE / "rough_profiles.png", dpi=160)
plt.close(fig)

# Profiles across the arrowed outer curb, both sides. Use actual ray surface,
# and retain original B-Rep edges to distinguish a vertical curb from inner chamfer.
fig, axs = plt.subplots(3, 2, figsize=(13, 9), layout="constrained")
for j, y in enumerate([-2., 0., 2.]):
    for k, side in enumerate(["left", "right"]):
        xs = np.linspace(-4.25, -3.55, 1401) if side == "left" else np.linspace(3.55, 4.25, 1401)
        z = height(collision, np.c_[xs, np.full(len(xs), y)])
        ax = axs[j, k]
        ax.plot(xs, z * 1000, lw=2, color="#1569a5", label="交付碰撞表面")
        source_names = ["BREP_5", "BREP_7"] if side == "left" else ["BREP_1", "BREP_3"]
        for source_name in source_names:
            for c in section_curves(source_name, y):
                a, b = point(c, c.FirstParameter()), point(c, c.LastParameter())
                if min(a[2], b[2]) > .14:
                    ax.plot([a[0], b[0]], [a[2] * 1000, b[2] * 1000], color="#e57225", lw=1)
        inner_x = -3.7 if side == "left" else 3.7
        curb_x = -3.92 if side == "left" else 3.92
        outer_x = -4.1 if side == "left" else 4.1
        h = height(collision, [[inner_x, y], [curb_x, y], [outer_x, y]])
        row = {"side": side, "world_y_m": y,
               "samples": dict(zip(["inside", "curb_top", "outside"],
                                   [{"x_m": x, "z_m": float(v)} for x, v in zip([inner_x, curb_x, outer_x], h)])),
               "curb_minus_inside_mm": float((h[1] - h[0]) * 1000),
               "curb_minus_outside_mm": float((h[1] - h[2]) * 1000),
               "sample_positions_not_whole_perimeter_extrema": True}
        result["outer_curbs"].append(row)
        ax.set_title(f"{'左' if side == 'left' else '右'}外缘，世界y={y:g}m；内侧高差{row['curb_minus_inside_mm']:.2f}mm")
        ax.set_xlabel("世界X / m"); ax.set_ylabel("世界Z / mm")
        ax.set_ylim(130, 370); ax.grid(alpha=.2)
fig.suptitle("用户箭头对应中央高地外缘：橙色为原CAD结构边，蓝色为实际交付碰撞顶面", fontsize=14)
fig.savefig(HERE / "outer_curb_sections.png", dpi=170)
plt.close(fig)

# Map showing outer curb vs previous, separate, inner lip at part383.
mesh = trimesh.util.concatenate([load_part(n) for n in [0, 1, 2, 4, 82, 383, 280, 281]])
tri = mesh.triangles; keep = mesh.face_normals[:, 2] > .15
from matplotlib.collections import PolyCollection
fig, ax = plt.subplots(figsize=(8, 9), layout="constrained")
t = tri[keep]; h = t[:, :, 2].mean(1); order = np.argsort(h)
ax.add_collection(PolyCollection(t[order, :, :2], array=h[order], cmap="terrain", clim=(-.05, .45),
                                 edgecolors="#777777", linewidths=.08))
ax.plot([-3.905, -3.905], [-2.35, 2.35], color="#e94730", lw=5, label="用户所指外缘连续坎（示意定位）")
ax.plot([3.945, 3.945], [-2.35, 2.35], color="#e94730", lw=5)
ax.plot([-2.00723, -1.957668], [0, 0], color="#1c4a9e", lw=6, label="之前量的49.56mm内侧倒角（不同位置）")
for y in [-2., 0., 2.]:
    ax.plot([-4.25, -3.55], [y, y], "k--", lw=1)
    ax.plot([3.55, 4.25], [y, y], "k--", lw=1)
ax.set_xlim(-5.3, 5.3); ax.set_ylim(-5.7, 5.7); ax.set_aspect("equal")
ax.set_xlabel("世界X / m"); ax.set_ylabel("世界Y / m")
ax.set_title("外缘连续坎与内侧台面倒角的位置区分")
ax.legend(loc="upper right", fontsize=9); ax.grid(alpha=.2)
fig.savefig(HERE / "curb_locations.png", dpi=170)
plt.close(fig)

result["source_unchanged_after_read"] = sha(subset) == subset_sha
assert result["source_unchanged_after_read"]
(HERE / "GEOMETRY_AUDIT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"rough": result["rough"], "outer_curbs": result["outer_curbs"],
                  "source_unchanged": result["source_unchanged_after_read"]}, ensure_ascii=False, indent=2))
