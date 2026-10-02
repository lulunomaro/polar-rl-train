import sys, json, os
import numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TopAbs import TopAbs_ShapeEnum as TE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
S = XCAFDoc_ShapeTool
doc = TDocStd_Document(TCollection_ExtendedString("X"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
r.ReadFile(sys.argv[1]); r.Transfer(doc)
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
free = TDF_LabelSequence(); tool.GetFreeShapes(free)
root = S.GetShape_s(free.Value(1))
BRepMesh_IncrementalMesh(root, 0.25, False, 0.3, True)
want = int(sys.argv[2]) if len(sys.argv)>2 else 4
e = TopExp_Explorer(root, TE.TopAbs_SOLID)
k = 0
while e.More():
    k += 1
    if k == want:
        so = e.Current()
        props = GProp_GProps(); BRepGProp.VolumeProperties_s(so, props)
        bb = Bnd_Box(); BRepBndLib.Add_s(so, bb, False)
        mn, mx = bb.CornerMin(), bb.CornerMax()
        print("solid", k, "vol=%.0f" % props.Mass(), "box", [round(mn.X(),1),round(mn.Y(),1),round(mn.Z(),1),round(mx.X(),1),round(mx.Y(),1),round(mx.Z(),1)])
        fe = TopExp_Explorer(so, TE.TopAbs_FACE)
        nf = 0; ntri = 0; nnone = 0
        loc = TopLoc_Location()
        while fe.More():
            f = TopoDS.Face_s(fe.Current())
            fb = Bnd_Box(); BRepBndLib.Add_s(f, fb, False)
            fmn, fmx = fb.CornerMin(), fb.CornerMax()
            tri = BRep_Tool.Triangulation_s(f, loc)
            t = 0 if tri is None else tri.NbTriangles()
            if tri is None: nnone += 1
            ntri += t; nf += 1
            if nf <= 12 or tri is None:
                print("   face %2d tris=%5d box=[%.1f %.1f %.1f %.1f %.1f %.1f]" % (nf, t, fmn.X(),fmn.Y(),fmn.Z(),fmx.X(),fmx.Y(),fmx.Z()))
            fe.Next()
        print("   faces=%d tris=%d none=%d" % (nf, ntri, nnone))
        break
    e.Next()
