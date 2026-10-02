import sys, time
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.XCAFPrs import XCAFPrs_DocumentExplorer, XCAFPrs_DocumentNode, XCAFPrs_DocumentExplorerFlags_OnlyLeafNodes
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
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
    return [round(mn.X(),1),round(mn.Y(),1),round(mn.Z(),1),round(mx.X(),1),round(mx.Y(),1),round(mx.Z(),1)]
doc = TDocStd_Document(TCollection_ExtendedString("X"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
t0=time.time(); r.ReadFile(sys.argv[1]); r.Transfer(doc)
print("parse %.1fs" % (time.time()-t0))
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
print("ROOT box", box(S.GetShape_s(free.Value(1))))
exp = XCAFPrs_DocumentExplorer()
exp.Init(doc, XCAFPrs_DocumentExplorerFlags_OnlyLeafNodes, 0)
n = 0
while exp.More():
    node = exp.Current()
    lab = node.Label; ref = node.Ref
    loc = node.AbsoluteLocation
    sh = S.GetShape_s(ref)
    sh2 = sh.Located(TopLoc_Location(loc.Transformation())) if not sh.IsNull() else sh
    if n < 12:
        print("%-30s depth? ref=%s absT=[%s] localbox=%s worldbox=%s" % (nm(ref)[:30], ref.Tag(), ", ".join("%.1f"%loc.Transformation().Value(i,4) for i in range(1,4)), box(sh), box(sh2)))
    n += 1
    exp.Next()
print("leaf nodes:", n, "%.1fs" % (time.time()-t0))

