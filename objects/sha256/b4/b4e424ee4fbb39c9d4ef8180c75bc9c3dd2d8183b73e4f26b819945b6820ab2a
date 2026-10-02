import sys, time
import numpy as np
t0 = time.time()
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_LabelSequence
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopAbs import TopAbs_ShapeEnum as TE, TopAbs_Orientation as OR
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
S = XCAFDoc_ShapeTool
doc = TDocStd_Document(TCollection_ExtendedString("X"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
r.ReadFile(sys.argv[1]); r.Transfer(doc)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
sh = tool.GetShape_s(free.Value(1))
BRepMesh_IncrementalMesh(sh, 0.5, False, 0.35, True)
print("parse+mesh %.2fs" % (time.time()-t0), flush=True)
faces = []
e = TopExp_Explorer(sh, TE.TopAbs_FACE)
while e.More():
    faces.append(TopoDS.Face_s(e.Current())); e.Next()
print("faces", len(faces), "%.2fs" % (time.time()-t0), flush=True)
totv = 0; tott = 0
loc = TopLoc_Location()
t1 = time.time()
for f in faces[:2000]:
    tri = BRep_Tool.Triangulation_s(f, loc)
    if tri is None:
        continue
    totv += tri.NbNodes(); tott += tri.NbTriangles()
print("count loop over 2000 faces: %.2fs verts=%d tris=%d" % (time.time()-t1, totv, tott), flush=True)
f0 = faces[0]
tri = BRep_Tool.Triangulation_s(f0, loc)
print("nbnodes", tri.NbNodes(), "nbtri", tri.NbTriangles())
try:
    a = tri.MapNodeArray(); print("MapNodeArray type", type(a))
    arr = np.frombuffer(a, dtype=np.float32) if hasattr(a,'__buffer__') else None
    print("frombuffer?", arr.shape if arr is not None else "no buffer")
except Exception as ex:
    print("mapnode err", ex)
try:
    import ctypes
    t1=time.time()
    pts = np.array([[tri.Node(i).X(), tri.Node(i).Y(), tri.Node(i).Z()] for i in range(1, tri.NbNodes()+1)])
    print("python loop nodes %d -> %.3fs" % (len(pts), time.time()-t1))
except Exception as ex:
    print("nodeloop err", ex)



