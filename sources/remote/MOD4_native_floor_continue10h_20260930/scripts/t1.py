import sys
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
S = XCAFDoc_ShapeTool
def nm(lab):
    a = TDataStd_Name()
    return a.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), a) else ""
def box(sh):
    bb = Bnd_Box(); BRepBndLib.Add_s(sh, bb, False)
    mn, mx = bb.CornerMin(), bb.CornerMax()
    return [round(mn.X(),1),round(mn.Y(),1),round(mn.Z(),1),round(mx.X(),1),round(mx.Y(),1),round(mx.Z(),1)]
doc = TDocStd_Document(TCollection_ExtendedString("X"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
r.ReadFile(sys.argv[1]); r.Transfer(doc)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
root = free.Value(1)
print("ROOT", nm(root), box(S.GetShape_s(root)))
comps = TDF_LabelSequence(); S.GetComponents_s(root, comps)
print("n comps", comps.Length())
for j in range(min(comps.Length(), 8)):
    c = comps.Value(j+1)
    ref = TDF_Label(); S.GetReferredShape_s(c, ref) if S.IsReference_s(c) else None
    print(" comp", c.Tag(), "name=", nm(c), "refname=", nm(ref) if ref else "", "shapebox=", box(S.GetShape_s(c)), "loc=", [[round(S.GetLocation_s(c).Transformation().Value(i,k),1) for k in range(1,5)] for i in range(1,4)])

