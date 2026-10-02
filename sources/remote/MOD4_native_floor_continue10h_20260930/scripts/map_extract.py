"""Extract the RMUC2026 7v7 map from its STEP file: per-solid inventory (name, transform,
bbox) + a coarse mesh + a rasterised heightfield the RL terrain can be built from."""
import os, sys, json, time
from OCP.STEPControl import STEPControl_Reader
from OCP.Interface import Interface_Static
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_FACE, TopAbs_COMPOUND, TopAbs_SHAPE
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopoDS import TopoDS, TopoDS_Compound
from OCP.gp import gp_Pnt
import numpy as np
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS_Shape

SRC = r"C:/Users/lulunomaro/Downloads/RMUC2026_V2.0.0.stp"
OUT = r"D:/claude2/fangzhen/cad/out_map"
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
Interface_Static.SetCVal_s("read.step.product.mode", "0")   # keep the assembly structure
r = STEPControl_Reader()
print("reading...", flush=True)
st = r.ReadFile(SRC)
print("read status", st, "in %.1f s" % (time.time() - t0), flush=True)
ntr = r.TransferRoots()
print("transferred %d roots / %d shapes in %.1f s"
      % (r.NbRootsForTransfer(), r.NbShapes(), time.time() - t0), flush=True)
root = r.OneShape()
box = Bnd_Box(); BRepBndLib.Add_s(root, box, False)
lo, hi = box.CornerMin(), box.CornerMax()
print("MAP BBOX (mm) lo=(%.1f,%.1f,%.1f) hi=(%.1f,%.1f,%.1f) -> %.2f x %.2f x %.2f m"
      % (lo.X(), lo.Y(), lo.Z(), hi.X(), hi.Y(), hi.Z(),
         (hi.X() - lo.X()) / 1000, (hi.Y() - lo.Y()) / 1000, (hi.Z() - lo.Z()) / 1000), flush=True)
# per transferred shape (one per solid) -> the feature inventory
inv = []
for i in range(1, r.NbShapes() + 1):
    sh = r.Shape(i)
    b2 = Bnd_Box(); BRepBndLib.Add_s(sh, b2, False)
    a, c = b2.CornerMin(), b2.CornerMax()
    inv.append(dict(i=i, lo=[a.X(), a.Y(), a.Z()], hi=[c.X(), c.Y(), c.Z()]))
json.dump(inv, open(os.path.join(OUT, "shapes.json"), "w"), ensure_ascii=False)
print("wrote shapes.json with %d entries" % len(inv), flush=True)

# 1) every SOLID in the map with its bbox (mm)
n = 0
recs = []
exp = TopExp_Explorer(root, TopAbs_SOLID)
while exp.More():
    s = exp.Current(); n += 1
    box = Bnd_Box(); BRepBndLib.Add_s(s, box, False)
    lo, hi = box.CornerMin(), box.CornerMax()
    pr = GProp_GProps(); BRepGProp.VolumeProperties_s(s, pr)
    vol = pr.Mass()
    fill = vol / max(1.0, (hi.X() - lo.X()) * (hi.Y() - lo.Y()) * (hi.Z() - lo.Z()))
    recs.append(dict(i=n, lo=[lo.X(), lo.Y(), lo.Z()], hi=[hi.X(), hi.Y(), hi.Z()],
                     vol_mm3=vol, fill_ratio=float(fill)))
    exp.Next()
    if n % 50 == 0:
        print("  solids %d  %.1f s" % (n, time.time() - t0), flush=True)
print("solids:", n, "in %.1f s" % (time.time() - t0), flush=True)
json.dump(recs, open(os.path.join(OUT, "solids.json"), "w"), ensure_ascii=False)

# 2) coarse mesh of the whole map (for a heightfield + a picture)
try:
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.ShapeFix import ShapeFix_Shape
    import trimesh, numpy as np
    m = BRepMesh_IncrementalMesh(root, 8.0, False, 25.0, True)
    m.Perform(); print("meshed in %.1f s" % (time.time() - t0), flush=True)
    verts, faces = [], []
    fmap = TopTools_IndexedMapOfShape()
    from OCP.TopExp import TopExp
    TopExp.MapShapes_s(root, TopAbs_FACE, fmap)
    for fi in range(1, fmap.Extent() + 1):
        f = TopoDS.Face_s(fmap.FindKey(fi))
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is None:
            continue
        trsf = loc.Transformation()
        nv = tri.NbNodes()
        base = len(verts)
        for k in range(1, nv + 1):
            p = tri.Node(k).Transformed(trsf)
            verts.append((p.X(), p.Y(), p.Z()))
        for t in tri.Triangles():
            a, b, c = t.Value(1), t.Value(2), t.Value(3)
            faces.append((base + a - 1, base + b - 1, base + c - 1))
    V = np.asarray(verts, np.float64); F = np.asarray(faces, np.int64)
    print("mesh: %d verts %d faces" % (len(V), len(F)), flush=True)
    np.save(os.path.join(OUT, "map_verts.npy"), V)
    np.save(os.path.join(OUT, "map_faces.npy"), F)
    trimesh.Trimesh(vertices=V, faces=F).export(os.path.join(OUT, "map_coarse.stl"))
except Exception as e:
    print("meshing failed:", type(e).__name__, e, flush=True)
print("done in %.1f s" % (time.time() - t0), flush=True)
