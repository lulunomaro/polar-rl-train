import sys, json
import numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.TopAbs import TopAbs_ShapeEnum as TE
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf
S = XCAFDoc_ShapeTool
def nm(lab):
    a = TDataStd_Name()
    try:
        if lab.FindAttribute(TDataStd_Name.GetID_s(), a): return a.Get().ToExtString()
    except Exception: pass
    return ""
def box(sh):
    bb = Bnd_Box(); BRepBndLib.Add_s(sh, bb, False)
    mn, mx = bb.CornerMin(), bb.CornerMax()
    return np.array([mn.X(),mn.Y(),mn.Z(),mx.X(),mx.Y(),mx.Z()])
def locT(sh):
    t = sh.Location().Transformation()
    return [round(t.Value(i,4),1) for i in range(1,4)]
doc = TDocStd_Document(TCollection_ExtendedString("X"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
r.ReadFile(sys.argv[1]); r.Transfer(doc)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
root = free.Value(1)
target = sys.argv[2]
comps = TDF_LabelSequence(); S.GetComponents_s(root, comps)
print("root box", np.round(box(S.GetShape_s(root)),1), "children", comps.Length())
for j in range(comps.Length()):
    c = comps.Value(j+1)
    ref = TDF_Label()
    if S.IsReference_s(c): S.GetReferredShape_s(c, ref)
    else: ref = c
    p = nm(ref)
    if target not in p: continue
    sh = S.GetShape_s(c)
    print("LEAF", p[:34], "tag", c.Tag(), "shapeLocT", locT(sh), "box", np.round(box(sh),1))
    e = TopExp_Explorer(sh, TE.TopAbs_SOLID)
    k = 0
    while e.More() and k < 6:
        so = e.Current()
        print("   solid", k, "locT", locT(so), "box", np.round(box(so),1))
        e.Next(); k += 1
    break
