import sys, json, os, time
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
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
r.ReadFile(sys.argv[1]); r.Transfer(doc)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
print("ROOT box", box(S.GetShape_s(free.Value(1))))
maxd = int(sys.argv[2]) if len(sys.argv)>2 else 3
def tr(lab, depth, path):
    own = nm(lab)
    ref = TDF_Label(); isref = S.IsReference_s(lab)
    if isref: S.GetReferredShape_s(lab, ref)
    prod = nm(ref) if (isref and not ref.IsNull()) else own
    asm = lab
    if not S.IsAssembly_s(lab) and not ref.IsNull() and S.IsAssembly_s(ref): asm = ref
    sh = S.GetShape_s(lab)
    loc = S.GetLocation_s(lab).Transformation()
    L = [[round(loc.Value(i,j),1) for j in range(1,5)] for i in range(1,4)]
    print("  "*depth + "%s | box=%s | locT=%s" % (prod[:40], box(sh) if sh is not None and not sh.IsNull() else None, L[0][3] and [L[0][3],L[1][3],L[2][3]]))
    if depth >= maxd: return
    if S.IsAssembly_s(asm):
        comps = TDF_LabelSequence(); S.GetComponents_s(asm, comps)
        for j in range(comps.Length()):
            tr(comps.Value(j+1), depth+1, path+[prod])
for i in range(free.Length()):
    tr(free.Value(i+1), 0, [])
