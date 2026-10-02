"""STEP (SolidWorks assembly) -> per-solid world-frame meshes + manifest.json.

XCAF assembly walk with explicitly accumulated component transforms.  Output frame is
the STEP global frame, unit mm.  Every solid gets its own OBJ plus volume / COM / AABB.

Usage:
  python step_extract.py <in.STEP> <out_dir> [--defl 0.4] [--ang 0.3] [--min-vol 200]
"""
import argparse, json, os, time
import numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool, XCAFDoc_ColorTool
from OCP.TopAbs import TopAbs_ShapeEnum as TE, TopAbs_Orientation as OR
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

S = XCAFDoc_ShapeTool
t_start = time.time()


def label_name(lab):
    a = TDataStd_Name()
    try:
        if lab.FindAttribute(TDataStd_Name.GetID_s(), a):
            return a.Get().ToExtString()
    except Exception:
        pass
    return ""


def box_of(shape):
    bb = Bnd_Box()
    BRepBndLib.Add_s(shape, bb, False)
    mn, mx = bb.CornerMin(), bb.CornerMax()
    return [mn.X(), mn.Y(), mn.Z(), mx.X(), mx.Y(), mx.Z()]


def sub_shapes(shape, kind):
    out = []
    e = TopExp_Explorer(shape, kind)
    while e.More():
        out.append(e.Current())
        e.Next()
    return out


def mat_of_trsf(t):
    m = np.eye(4)
    for i in range(3):
        for j in range(4):
            m[i, j] = t.Value(i + 1, j + 1)
    return m


def label_loc_matrix(lab):
    try:
        return mat_of_trsf(S.GetLocation_s(lab).Transformation())
    except Exception:
        return np.eye(4)


def transform_box(box, M):
    lo, hi = np.array(box[:3]), np.array(box[3:])
    cs = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1])
                      for z in (lo[2], hi[2])])
    w = np.hstack([cs, np.ones((8, 1))]) @ M.T
    return [w[:, 0].min(), w[:, 1].min(), w[:, 2].min(),
            w[:, 0].max(), w[:, 1].max(), w[:, 2].max()]


def tessellate(shape, M):
    """Triangles of `shape` (sub-locations kept) pushed through 4x4 matrix M."""
    verts = []
    tris = []
    loc = TopLoc_Location()
    for fa in sub_shapes(shape, TE.TopAbs_FACE):
        face = TopoDS.Face_s(fa)
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is None:
            continue
        Lm = M @ mat_of_trsf(loc.Transformation())
        n = tri.NbNodes()
        base = len(verts)
        for i in range(1, n + 1):
            p = tri.Node(i)
            q = Lm @ np.array([p.X(), p.Y(), p.Z(), 1.0])
            verts.append((q[0], q[1], q[2]))
        rev = fa.Orientation() == OR.TopAbs_REVERSED
        m = tri.NbTriangles()
        for i in range(1, m + 1):
            t = tri.Triangle(i)
            a, b, c = t.Value(1), t.Value(2), t.Value(3)
            if rev:
                b, c = c, b
            tris.append((base + a - 1, base + b - 1, base + c - 1))
    V = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
    F = np.asarray(tris, dtype=np.int64).reshape(-1, 3)
    if len(V):
        uniq, inv = np.unique(np.round(V, 4), axis=0, return_inverse=True)
        if len(uniq) < len(V):
            F = inv[F.reshape(-1)].reshape(-1, 3)
            V = uniq
    return V, F


def write_obj(path, V, F):
    with open(path, "w") as fh:
        fh.write("# mm, world frame\n")
        for p in V:
            fh.write("v %.4f %.4f %.4f\n" % (p[0], p[1], p[2]))
        for t in F:
            fh.write("f %d %d %d\n" % (t[0] + 1, t[1] + 1, t[2] + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step")
    ap.add_argument("outdir")
    ap.add_argument("--defl", type=float, default=0.4)
    ap.add_argument("--ang", type=float, default=0.3)
    ap.add_argument("--min-vol", type=float, default=200.0, help="mm^3")
    ap.add_argument("--max-tris", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    os.makedirs(os.path.join(args.outdir, "meshes"), exist_ok=True)

    doc = TDocStd_Document(TCollection_ExtendedString("XCAFData"))
    rdr = STEPCAFControl_Reader()
    rdr.SetNameMode(True)
    if not rdr.ReadFile(args.step):
        print("READ FAILED")
        return 2
    rdr.Transfer(doc)
    print("[%.1fs] parsed %s" % (time.time() - t_start, os.path.basename(args.step)), flush=True)
    tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ctool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    free = TDF_LabelSequence()
    tool.GetFreeShapes(free)
    root_shape = S.GetShape_s(free.Value(1))
    BRepMesh_IncrementalMesh(root_shape, args.defl, False, args.ang, True)
    print("[%.1fs] tessellated (free=%d)" % (time.time() - t_start, free.Length()), flush=True)

    solids = []
    tree = []
    counter = [0]

    def color_of(lab):
        try:
            c = ctool.ColorOfShape_s(lab)
            if c is not None:
                return [round(c.Red(), 3), round(c.Green(), 3), round(c.Blue(), 3)]
        except Exception:
            pass
        return None

    def components_of(lab):
        comps = TDF_LabelSequence()
        try:
            S.GetComponents_s(lab, comps)
        except Exception:
            pass
        return comps

    def walk(lab, acc, path, depth):
        own = label_name(lab)
        ref = TDF_Label()
        try:
            isref = S.IsReference_s(lab)
        except Exception:
            isref = False
        if isref:
            try:
                S.GetReferredShape_s(lab, ref)
            except Exception:
                ref = TDF_Label()
        prod = label_name(ref) if (isref and not ref.IsNull()) else own
        disp = prod or own or ("label%d" % lab.Tag())
        p2 = path + [disp]
        M = acc if depth == 0 else acc @ label_loc_matrix(lab)
        asm_lab = None
        try:
            if S.IsAssembly_s(lab):
                asm_lab = lab
            elif not ref.IsNull() and S.IsAssembly_s(ref):
                asm_lab = ref
        except Exception:
            asm_lab = None
        if asm_lab is not None:
            comps = components_of(asm_lab)
            if comps.Length():
                tree.append(dict(depth=depth, name=disp, path="/".join(p2),
                                 n_children=comps.Length(),
                                 M=[[round(x, 6) for x in row] for row in M.tolist()]))
                for j in range(comps.Length()):
                    walk(comps.Value(j + 1), M, p2, depth + 1)
                return
        if not S.IsShape_s(lab):
            return
        base = ref if (isref and not ref.IsNull()) else lab
        shape = S.GetShape_s(base)
        if shape is None or shape.IsNull():
            return
        shape.Location(TopLoc_Location())
        sl = sub_shapes(shape, TE.TopAbs_SOLID) or sub_shapes(shape, TE.TopAbs_SHELL)
        for so in sl:
            props = GProp_GProps()
            try:
                BRepGProp.VolumeProperties_s(so, props)
                vol = props.Mass()
                com = props.CentreOfMass()
                mi = props.MatrixOfInertia()
                inertia0 = [[float(mi.Value(i, j)) for j in range(1, 4)] for i in range(1, 4)]
            except Exception:
                vol, com, inertia0 = 0.0, None, None
            if vol < args.min_vol:
                continue
            lb = box_of(so)
            wb = transform_box(lb, M)
            V, F = tessellate(so, M)
            if len(F) == 0:
                continue
            if args.max_tris and len(F) > args.max_tris:
                F = F[:args.max_tris]
            counter[0] += 1
            sid = "%05d" % counter[0]
            fn = "solid_%s.obj" % sid
            write_obj(os.path.join(args.outdir, "meshes", fn), V, F)
            cw = (M @ np.array([com.X(), com.Y(), com.Z(), 1.0])) if com else None
            solids.append(dict(
                id=sid, obj=fn, product=disp, inst_name=own, parent="/".join(path),
                path="/".join(p2), depth=depth, label_tag=lab.Tag(),
                volume_mm3=round(vol, 1),
                com_local=[round(com.X(), 3), round(com.Y(), 3), round(com.Z(), 3)] if com is not None else None,
                inertia_local=inertia0,
                com_world=[round(float(x), 2) for x in cw[:3]] if cw is not None else None,
                bbox_world=[round(x, 2) for x in wb],
                size=[round(wb[3] - wb[0], 2), round(wb[4] - wb[1], 2), round(wb[5] - wb[2], 2)],
                nverts=int(len(V)), ntris=int(len(F)),
                mesh_bbox=[round(float(V.min(0)[k]), 2) for k in range(3)] +
                          [round(float(V.max(0)[k]), 2) for k in range(3)],
                M=[[round(float(x), 6) for x in row] for row in M.tolist()],
                color=color_of(base),
            ))
            if args.limit and counter[0] >= args.limit:
                raise StopIteration()

    try:
        for i in range(free.Length()):
            walk(free.Value(i + 1), np.eye(4), [], 0)
    except StopIteration:
        print("stopped at limit", args.limit)
    lo = [min(s["bbox_world"][k] for s in solids) for k in range(3)]
    hi = [max(s["bbox_world"][k + 3] for s in solids) for k in range(3)]
    man = dict(source=os.path.abspath(args.step), unit="mm", frame="step_world",
               union_bbox=[round(x, 2) for x in lo + hi],
               deflection=args.defl, angular=args.ang, min_vol_mm3=args.min_vol,
               elapsed_s=round(time.time() - t_start, 1),
               n_solids=len(solids), n_tris=int(sum(s["ntris"] for s in solids)),
               tree=tree, solids=solids)
    with open(os.path.join(args.outdir, "manifest.json"), "w", encoding="utf8") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=1)
    print("[%.1fs] DONE solids=%d tris=%d union=%s" %
          (time.time() - t_start, len(solids), man["n_tris"], man["union_bbox"]), flush=True)


if __name__ == "__main__":
    main()
