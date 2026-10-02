import sys, time
import numpy as np
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
    try:
        if lab.FindAttribute(TDataStd_Name.GetID_s(), a): return a.Get().ToExtString()
    except Exception: pass
    return ""
def box(sh):
    bb = Bnd_Box(); BRepBndLib.Add_s(sh, bb, False)
    mn, mx = bb.CornerMin(), bb.CornerMax()
    return np.array([mn.X(),mn.Y(),mn.Z(),mx.X(),mx.Y(),mx.Z()])
def xf(box, M):
    lo, hi = box[:3], box[3:]
    cs = np.array([[x,y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])])
    w = np.hstack([cs, np.ones((8,1))]) @ M.T
    return np.concatenate([w[:, :3].min(0), w[:, :3].max(0)])
def M4(t):
    m = np.eye(4)
    for i in range(3):
        for j in range(4): m[i,j] = t.Value(i+1,j+1)
    return m
doc = TDocStd_Document(TCollection_ExtendedString("X"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
r.ReadFile(sys.argv[1]); r.Transfer(doc)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
root = free.Value(1)
print("ROOT box", np.round(box(S.GetShape_s(root)),1))
cnt = [0]
def walk(lab, acc):
    if cnt[0] > 25: return
    if S.IsAssembly_s(lab):
        comps = TDF_LabelSequence(); S.GetComponents_s(lab, comps)
        for j in range(comps.Length()):
            c = comps.Value(j+1)
            loc = M4(S.GetLocation_s(c).Transformation())
            walk(c, acc @ loc)
        return
    ref = TDF_Label()
    if S.IsReference_s(lab): S.GetReferredShape_s(lab, ref)
    else: ref = lab
    own = M4(S.GetLocation_s(lab).Transformation())
    bGet = box(S.GetShape_s(lab))
    bRef = box(S.GetShape_s(ref))
    bAcc = xf(bRef, acc @ own)
    bOwn = xf(bRef, own)
    print("%-24s getShape=%s | ref=%s | acc*ref=%s | own*ref=%s" % (
        nm(ref)[:24], np.round(bGet,1), np.round(bRef,1), np.round(bAcc,1), np.round(bOwn,1)))
    print("   match get~acc*ref:", np.allclose(bGet[:3], bAcc[:3], atol=2), " get~own*ref:", np.allclose(bGet[:3], bOwn[:3], atol=2), " get~ref:", np.allclose(bGet, bRef, atol=2))
    cnt[0] += 1
walk(root, np.eye(4))
