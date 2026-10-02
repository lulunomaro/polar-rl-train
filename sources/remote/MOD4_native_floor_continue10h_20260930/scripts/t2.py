import sys, os, time
t0 = time.time()
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Controller
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString, TCollection_AsciiString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_LabelSequence
from OCP.TColStd import TColStd_MapOfAsciiString, TColStd_IndexedDataMapOfStringString
from OCP.Message import Message_ProgressRange
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.Interface import Interface_Static
from OCP.RWMesh import RWMesh_NameFormat
from OCP.RWGltf import RWGltf_CafWriter, RWGltf_WriterTrsfFormat
try:
    STEPCAFControl_Controller.Init_s()
except Exception as e:
    print("ctrl init", e)
step, out = sys.argv[1], sys.argv[2]
defl = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
doc = TDocStd_Document(TCollection_ExtendedString("X"))
r = STEPCAFControl_Reader(); r.SetNameMode(True); r.SetColorMode(True)
print("read", r.ReadFile(step), "transfer", r.Transfer(doc), "%.1fs" % (time.time()-t0), flush=True)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
sh = tool.GetShape_s(free.Value(1))
BRepMesh_IncrementalMesh(sh, defl, False, 0.35, True)
print("meshed %.1fs" % (time.time()-t0), flush=True)
w = RWGltf_CafWriter(TCollection_AsciiString(out), True)
w.SetParallel(True)
w.SetTransformationFormat(RWGltf_WriterTrsfFormat.RWGltf_WriterTrsfFormat_Mat4)
w.SetNodeNameFormat(RWMesh_NameFormat.RWMesh_NameFormat_ProductAndInstance)
w.SetMeshNameFormat(RWMesh_NameFormat.RWMesh_NameFormat_ProductAndInstance)
print("write", w.Perform(doc, TDF_LabelSequence(), TColStd_MapOfAsciiString(), TColStd_IndexedDataMapOfStringString(), Message_ProgressRange()), "%.1fs" % (time.time()-t0), flush=True)
print("size", os.path.getsize(out) if os.path.exists(out) else "n/a")

