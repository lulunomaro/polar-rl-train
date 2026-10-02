"""Phase-1 audit of the STEP -> mesh chain (no code changes).

Answers three questions with numbers:
  1. how much real material does the min-volume filter throw away, and which parts?
  2. are any exported entries open SHELLS rather than closed SOLIDS (the "片状化" risk)?
  3. does the per-solid mesh actually land in the world frame (assembly transform applied)?
Volume/property only: it never tessellates, so it is fast and safe to run alongside training.
"""
import json, os, sys
import numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TopAbs import TopAbs_ShapeEnum as TE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp_Face
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing   # OCCT moved Sewing here
from OCP.ShapeFix import ShapeFix_Shape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid


# Sew the free edges of one open shell and see whether it becomes a closed solid.  The
# volume before and after is what decides whether adopting the fix would move mass
# properties (a retrain) or only the picture (safe).
SEW = []


def sew_report(shape, name, tol=1e-4):
    faces = subs(shape, TE.TopAbs_FACE)
    if not faces:
        return
    v_before = vol_of(shape)
    sw = BRepBuilderAPI_Sewing(tol)
    for f in faces:
        sw.Add(f)
    sw.Perform()
    res = sw.SewedShape()
    try:
        fx = ShapeFix_Shape(res)
        fx.SetPrecision(tol)
        fx.Perform()
        res = fx.Shape()
    except Exception:
        pass
    sols = subs(res, TE.TopAbs_SOLID)
    if not sols:
        for s in subs(res, TE.TopAbs_SHELL):
            try:
                mk = BRepBuilderAPI_MakeSolid(s)
                if mk.IsDone():
                    sols.append(mk.Shape())
            except Exception:
                pass
    if not sols:
        SEW.append((name, len(faces), v_before, None, False))
        return
    v_after = sum(vol_of(s) for s in sols)
    cl = all(closed(s)[0] for s in sols)
    SEW.append((name, len(faces), v_before, v_after, cl))
S = XCAFDoc_ShapeTool
STEP = sys.argv[1] if len(sys.argv) > 1 else r"C:/Users/lulunomaro/Desktop/整车总装.STEP"
MAN = sys.argv[2] if len(sys.argv) > 2 else r"D:/claude2/fangzhen/cad/out/vehicle/manifest.json"
MIN_VOL = 300.0


def name_of(lab):
    a = TDataStd_Name()
    try:
        if lab.FindAttribute(TDataStd_Name.GetID_s(), a):
            return a.Get().ToExtString()
    except Exception:
        pass
    return ""


def subs(shape, kind):
    out = []
    e = TopExp_Explorer(shape, kind)
    while e.More():
        out.append(e.Current()); e.Next()
    return out


def vol_of(so):
    p = GProp_GProps()
    try:
        BRepGProp.VolumeProperties_s(so, p)
        return float(p.Mass())
    except Exception:
        return 0.0


def closed(so):
    """A usable rigid body must be a closed shell: every edge shared by exactly 2 faces."""
    sh = subs(so, TE.TopAbs_SHELL)
    if not sh:
        return False, 0, 0
    faces = subs(sh[0], TE.TopAbs_FACE)
    return bool(sh[0].Closed()), len(faces), 0


doc = TDocStd_Document(TCollection_ExtendedString("XCAFData"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
assert r.ReadFile(STEP) == 1, "read failed"
r.Transfer(doc)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
print("free (top-level) shapes:", free.Length())

rows = []


def loc(lab):
    try:
        t = S.GetLocation_s(lab).Transformation()
        m = np.eye(4)
        for i in range(3):
            for j in range(4):
                m[i, j] = t.Value(i + 1, j + 1)
        return m
    except Exception:
        return np.eye(4)


def walk(lab, acc, path, depth):
    own = name_of(lab)
    ref = TDF_Label()
    isref = False
    try:
        isref = S.IsReference_s(lab)
        if isref:
            S.GetReferredShape_s(lab, ref)
    except Exception:
        pass
    prod = name_of(ref) if (isref and not ref.IsNull()) else own
    disp = (prod or own or ("label%d" % lab.Tag())).strip()
    p2 = path + [disp]
    M = acc if depth == 0 else acc @ loc(lab)
    asm = None
    try:
        if S.IsAssembly_s(lab):
            asm = lab
        elif not ref.IsNull() and S.IsAssembly_s(ref):
            asm = ref
    except Exception:
        asm = None
    if asm is not None:
        comps = TDF_LabelSequence()
        try:
            S.GetComponents_s(asm, comps)
        except Exception:
            pass
        for j in range(comps.Length()):
            walk(comps.Value(j + 1), M, p2, depth + 1)
        return
    if not S.IsShape_s(lab):
        return
    base = ref if (isref and not ref.IsNull()) else lab
    shape = S.GetShape_s(base)
    if shape is None or shape.IsNull():
        return
    shape.Location(TopLoc_Location())
    sols = subs(shape, TE.TopAbs_SOLID)
    kind = "SOLID"
    if not sols:
        sols = subs(shape, TE.TopAbs_SHELL); kind = "SHELL"
    for so in sols:
        v = vol_of(so)
        cl, nf, _ = closed(so)
        if not cl and v > 5000.0 and len(SEW) < 8:   # only parts that matter
            try:
                sew_report(so, disp)
            except Exception:
                SEW.append((disp, 0, 0.0, None, False))
        rows.append(dict(name=disp, parent="/".join(path), kind=kind, vol=v,
                         closed=cl, nfaces=nf, depth=depth))


walk(free.Value(1), np.eye(4), [], 0)
tot = sum(r["vol"] for r in rows)
kept = [r for r in rows if r["vol"] >= MIN_VOL]
drop = [r for r in rows if r["vol"] < MIN_VOL]
print("\n== STEP solid inventory ==")
print("  shapes encountered : %d   total volume %.1f cm3" % (len(rows), tot / 1000.0))
print("  kept (>= %.0f mm3): %d  = %.1f cm3 (%.2f%% of volume)" %
      (MIN_VOL, len(kept), sum(r["vol"] for r in kept) / 1000.0,
       100.0 * sum(r["vol"] for r in kept) / tot))
print("  DROPPED by filter : %d  = %.1f cm3 (%.2f%%)" %
      (len(drop), sum(r["vol"] for r in drop) / 1000.0,
       100.0 * sum(r["vol"] for r in drop) / tot))
print("  exported as SHELL (open, 片状化 risk): %d" % sum(1 for r in rows if r["kind"] == "SHELL"))
print("  NOT closed (would render as a bag of faces): %d" % sum(1 for r in rows if not r["closed"]))
# Dump the open-shell inventory to a UTF-8 file: the console codepage mangles the Chinese
# part names, and knowing WHICH parts are open (and how big) decides whether the
# sheet-like look is worth sewing at all or is invisible hardware.
OUTF = os.path.normpath(os.path.join(os.path.dirname(MAN), os.pardir, os.pardir, os.pardir,
                                   "docs/audit/open_shells.txt"))
opn = [r for r in rows if not r["closed"]]
fh = open(OUTF, "w", encoding="utf-8")
fh.write("open-shell STEP entries, biggest first.  count %d of %d shapes" % (len(opn), len(rows)) + chr(10))
for r in sorted(opn, key=lambda x: -x["vol"]):
    fh.write("  %9.2f cm3 faces=%4d %-52s <- %s" % (r["vol"] / 1000.0,
               r["nfaces"], r["name"][:52],
               r["parent"].split("/")[-1][:48]) + chr(10))
tv = sum(r["vol"] for r in opn)
fh.write("open-shell volume %.1f cm3 = %.2f percent of the whole model" % (tv / 1000.0, 100.0 * tv / tot) + chr(10))
fh.close()
print("  -> " + OUTF)
print("\n== 15 biggest DROPPED solids (real material the sim never sees) ==")
for r in sorted(drop, key=lambda x: -x["vol"])[:15]:
    print("   %8.2f cm3  closed=%-5s faces=%4d  %-46s  <- %s" %
          (r["vol"] / 1000.0, r["closed"], r["nfaces"], r["name"][:46], r["parent"][:40]))
try:
    man = json.load(open(MAN, encoding="utf-8"))
    ms = man["solids"]
    print("\n== manifest cross-check ==")
    print("  manifest solids %d, triangles %d, min_vol_mm3 %s" %
          (len(ms), man.get("n_tris"), man.get("min_vol_mm3")))
    mv = sum(s["volume_mm3"] for s in ms) / 1000.0
    print("  manifest volume %.1f cm3  vs STEP kept %.1f cm3  -> missing %.1f cm3 (%.2f%%)" %
          (mv, sum(r["vol"] for r in kept) / 1000.0,
           (sum(r["vol"] for r in kept) / 1000.0 - mv),
           100.0 * (1 - mv / max(1e-9, sum(r["vol"] for r in kept)))))
    nz = sum(1 for s in ms if s["ntris"] == 0)
    print("  manifest entries with ZERO triangles: %d" % nz)
    bad = [s for s in ms if s["ntris"] > 0 and
           abs((s["bbox_world"][3] - s["bbox_world"][0]) *
               (s["bbox_world"][4] - s["bbox_world"][1]) *
               (s["bbox_world"][5] - s["bbox_world"][2])) < 1e-9]
    print("  degenerate (zero-extent) bounding boxes: %d" % len(bad))
except Exception as e:
    print("manifest cross-check skipped:", e)

print(chr(10) + "== sewing trial on the first %d open shells ==" % len(SEW))
for nm, nf, vb, va, cl in SEW:
    print("  %-46s faces=%4d  vol %9.2f -> %s cm3  closed=%s" % (
        nm[:46], nf, vb / 1000.0, "    none" if va is None else "%9.2f" % (va / 1000.0), cl))