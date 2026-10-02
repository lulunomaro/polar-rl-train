import sys
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TCollection import TCollection_ExtendedString
from OCP.gp import gp_Trsf
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

S = XCAFDoc_ShapeTool

def nm(lab):
    try:
        a = TDataStd_Name()
        if lab.FindAttribute(TDataStd_Name.GetID_s(), a):
            return a.Get().ToExtString()
    except Exception as e:
        return "ERR:" + str(e)
    return ""

def trsf(t):
    return [[round(t.Value(i, j), 4) for j in range(1, 5)] for i in range(1, 4)]

def dim_of(s):
    try:
        if s.IsNull(): return ""
        bb = Bnd_Box(); BRepBndLib.Add_s(s, bb, False)
        mn, mx = bb.CornerMin(), bb.CornerMax()
        return "[%0.1f %0.1f %0.1f]" % (mx.X()-mn.X(), mx.Y()-mn.Y(), mx.Z()-mn.Z())
    except Exception:
        return "berr"

path = sys.argv[1]
doc = TDocStd_Document(TCollection_ExtendedString("XCAFData"))
r = STEPCAFControl_Reader()
r.SetNameMode(True); r.SetColorMode(True); r.SetLayerMode(True)
print("readfile", r.ReadFile(path), "transfer", r.Transfer(doc))
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
print("free labels", free.Length())
maxdepth = int(sys.argv[2]) if len(sys.argv) > 2 else 2

def dump(lab, depth):
    isasm = S.IsAssembly_s(lab); isref = S.IsReference_s(lab); isshp = S.IsShape_s(lab)
    s = S.GetShape_s(lab)
    print("  " * depth + f"{lab.Tag()} asm={int(isasm)} ref={int(isref)} shp={int(isshp)} name={nm(lab)!r} dim={dim_of(s)}")
    if depth >= maxdepth: return
    comps = TDF_LabelSequence(); S.GetComponents_s(lab, comps)
    for j in range(comps.Length()):
        c = comps.Value(j+1)
        loc = S.GetLocation_s(c).Transformation()
        print("  " * (depth+1) + f"loc={trsf(loc)}")
        dump(c, depth+1)

for i in range(free.Length()):
    print("=== FREE %d ===" % i)
    dump(free.Value(i+1), 0)


