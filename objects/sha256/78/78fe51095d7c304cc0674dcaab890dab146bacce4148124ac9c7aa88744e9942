"""Verify the joint axes directly from the STEP B-rep: collect every cylindrical face
whose radius looks like a shaft/bearing bore, transform its axis into the robot frame
and cluster it around the hip / knee / wheel joint centres."""
import json, math, os, sys
import numpy as np
import yaml
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TopAbs import TopAbs_ShapeEnum as TE, TopAbs_Orientation as OR
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_SurfaceType as ST

step = sys.argv[1] if len(sys.argv) > 1 else r"C:/Users/lulunomaro/Desktop/整车总装.STEP"
spec = yaml.safe_load(open(sys.argv[2] if len(sys.argv) > 2 else
                           r"D:/claude2/fangzhen/robot/vehicle.spec.yaml", encoding="utf-8"))
Rf = np.array(spec["frame"]["rot"])
origin = np.array(spec["frame"]["origin_cad"], float)

doc = TDocStd_Document(TCollection_ExtendedString("XCAFData"))
rdr = STEPCAFControl_Reader()
rdr.SetNameMode(True)
assert rdr.ReadFile(step)
rdr.Transfer(doc)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
S = XCAFDoc_ShapeTool
free = TDF_LabelSequence()
tool.GetFreeShapes(free)

names = {}
from OCP.TDataStd import TDataStd_Name
def nm(lab):
    a = TDataStd_Name()
    try:
        if lab.FindAttribute(TDataStd_Name.GetID_s(), a):
            return a.Get().ToExtString()
    except Exception:
        pass
    return ""

def mat(t):
    m = np.eye(4)
    for i in range(3):
        for j in range(4):
            m[i, j] = t.Value(i + 1, j + 1)
    return m

rows = []
def walk(lab, acc, path, depth):
    own = nm(lab)
    ref = TDF_Label()
    isref = False
    try:
        isref = S.IsReference_s(lab)
        if isref:
            S.GetReferredShape_s(lab, ref)
    except Exception:
        pass
    disp = (nm(ref) if (isref and not ref.IsNull()) else own) or own or "?"
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
                rad = ad.Cylinder().Radius()
                ax = ad.Cylinder().Axis()
                if 4.0 < rad < 40.0:
                    d = np.array([ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z()])
                    loc = np.array([ax.Location().X(), ax.Location().Y(), ax.Location().Z()])
                    Mw = A4 @ M
                    d2 = Mw[:3, :3] @ d
                    l2 = Mw[:3, :3] @ loc + Mw[:3, 3]
                    rows.append((float(rad), d2 / np.linalg.norm(d2), l2, "/".join(p2[-3:])))
        except Exception:
            pass
        e.Next()

A4 = np.eye(4); A4[:3, :3] = Rf; A4[:3, 3] = -Rf @ origin
walk(free.Value(1), np.eye(4), [], 0)
print("cylindrical faces with 4-40 mm radius:", len(rows))

J = {"hip": (0.0, -223.85, 212.1), "knee": (-200.7, -223.85, 150.3),
     "wheel": (-0.9, -270.25, 0.0), "hipR": (0.0, 223.85, 212.1),
     "kneeR": (-200.7, 223.85, 150.3), "wheelR": (-0.9, 270.25, 0.0)}
for tag, c in J.items():
    c = np.array(c)
    sel = [r for r in rows if np.linalg.norm(r[2] - c) < 60.0]
    if not sel:
        print("%-6s : none within 60 mm" % tag); continue
    D = np.array([s[1] for s in sel])
    D = D * np.sign(D @ np.array([0.0, 1.0, 0.0]))[:, None]
    mean = D.mean(0); mean /= np.linalg.norm(mean)
    dev = np.degrees(np.arccos(np.clip(np.abs(D @ np.array([0, 0, 1.0])), 0, 1)))
    print("%-6s : n=%2d  mean axis=%s   |axis.Y| = %.3f   angle-to-Y: med %.1f deg, p90 %.1f deg"
          % (tag, len(sel), np.round(mean, 3), abs(mean[1]), np.median(dev), np.percentile(dev, 90)))
    for s in sorted(sel, key=lambda x: -x[0])[:4]:
        print("        r=%5.2f mm axis=%s at %s  %s" % (s[0], np.round(s[1], 2),
                                                        np.round(s[2], 0), s[3][:58]))
