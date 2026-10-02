"""Enumerate every revolute kinematic pair inside one leg, straight from the STEP B-rep.

Collects all cylindrical faces (bearing bores / shafts) in the leg subtree, projects
each cylinder axis onto the x-z plane of the robot frame (the leg plane, all axes are
lateral +/-Y), and clusters axes that coincide.  For each cluster it reports which
*distinct parts* share that axis: an axis used by parts from more than one rigid group
is a real revolute joint.
"""
import json, os, sys, collections
import numpy as np
import yaml
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
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_SurfaceType as ST

STEP = r"C:/Users/lulunomaro/Desktop/整车总装.STEP"
spec = yaml.safe_load(open(r"D:/claude2/fangzhen/robot/vehicle.spec.yaml", encoding="utf-8"))
Rf = np.array(spec["frame"]["rot"]); A4 = np.eye(4)
A4[:3, :3] = Rf; A4[:3, 3] = -Rf @ np.array(spec["frame"]["origin_cad"], float)
S = XCAFDoc_ShapeTool

doc = TDocStd_Document(TCollection_ExtendedString("XCAFData"))
rdr = STEPCAFControl_Reader(); rdr.SetNameMode(True)
assert rdr.ReadFile(STEP); rdr.Transfer(doc)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)

def nm(lab):
    a = TDataStd_Name()
    try:
        if lab.FindAttribute(TDataStd_Name.GetID_s(), a):
            return a.Get().ToExtString()
    except Exception:
        return ""
    return ""

def mat(t):
    m = np.eye(4)
    for i in range(3):
        for j in range(4):
            m[i, j] = t.Value(i + 1, j + 1)
    return m

faces = []          # (axis_xz, radius, dir, path, topgroup)
def walk(lab, acc, path, depth):
    own = nm(lab); ref = TDF_Label(); isref = False
    try:
        isref = S.IsReference_s(lab)
        if isref:
            S.GetReferredShape_s(lab, ref)
    except Exception:
        pass
    disp = (nm(ref) if (isref and not ref.IsNull()) else own) or "?"
    p2 = path + [disp]
    try:
        M = acc if depth == 0 else acc @ mat(S.GetLocation_s(lab).Transformation())
    except Exception:
        M = acc
    asm = None
    try:
        if S.IsAssembly_s(lab):
            asm = lab
        elif not ref.IsNull() and S.IsAssembly_s(ref):
            asm = ref
    except Exception:
        pass
    if asm is not None:
        comps = TDF_LabelSequence()
        try:
            S.GetComponents_s(asm, comps)
        except Exception:
            pass
        if comps.Length():
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
    e = TopExp_Explorer(shape, TE.TopAbs_FACE)
    while e.More():
        try:
            face = TopoDS.Face_s(e.Current())
            ad = BRepAdaptor_Surface(face)
            if ad.GetType() == ST.GeomAbs_Cylinder:
                r = ad.Cylinder().Radius()
                ax = ad.Cylinder().Axis()
                d = np.array([ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z()])
                loc = np.array([ax.Location().X(), ax.Location().Y(), ax.Location().Z()])
                Mw = A4 @ M
                d2 = Mw[:3, :3] @ d
                l2 = Mw[:3, :3] @ loc + Mw[:3, 3]
                if 3.0 < r < 45.0 and abs(d2[1]) > 0.98:      # lateral axis only
                    faces.append((l2[[0, 2]], float(l2[1]), r, "/".join(p2[1:3]),
                                  p2[-1]))
        except Exception:
            pass
        e.Next()

# left leg subtree only
def is_left(path):
    return path.startswith("24    髋腿")
walk(free.Value(1), np.eye(4), [], 0)
sel = [f for f in faces if is_left(f[3])]
print("lateral cylindrical faces in the LEFT leg:", len(sel))

# cluster axes by x-z position
clusters = []
for f in sel:
    for c in clusters:
        if np.linalg.norm(np.array(c["xz"]) - f[0]) < 4.0:
            c["items"].append(f); c["xz"] = np.mean([i[0] for i in c["items"]], axis=0)
            break
    else:
        clusters.append({"xz": list(f[0]), "items": [f]})
clusters.sort(key=lambda c: -len(c["items"]))
print("distinct lateral axes:", len(clusters))
print()
print("  x-z (mm)      parts  radii            sub-assemblies sharing this axis")
for c in clusters:
    parts = {i[4] for i in c["items"]}
    subs = sorted({i[3].split("/")[-1] for i in c["items"]})
    rr = sorted({round(i[2], 1) for i in c["items"]})
    xz = np.array(c["xz"])
    tag = ""
    for name, p in (("HIP", (0.0, 212.1)), ("KNEE", (-200.7, 150.3)), ("WHEEL", (-0.9, 0.0))):
        if np.linalg.norm(xz - np.array(p)) < 12:
            tag = "  <== " + name
    print("  (%7.1f,%7.1f)  %4d   %-14s %s%s"
          % (xz[0], xz[1], len(parts), ",".join(str(x) for x in rr)[:14],
             " | ".join(subs)[:70], tag))
