def mat_of_trsf(t):
    m = np.eye(4)
    for i in range(3):
        for j in range(4):
            m[i, j] = t.Value(i + 1, j + 1)
    return m


def unlocate(shape):
    shape.Location(TopLoc_Location())
    return shape


def tessellate(shape, M):
    """verts/tris of shape (its own sub-locations kept) transformed by 4x4 M."""
    verts = []
    tris = []
    loc = TopLoc_Location()
    for fa in sub_shapes(shape, TE.TopAbs_FACE):
        face = TopoDS.Face_s(fa)
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is None:
            continue
        L = M @ mat_of_trsf(loc.Transformation())
        n = tri.NbNodes()
        base = len(verts)
        for i in range(1, n + 1):
            p = tri.Node(i).Transformed(loc.Transformation())
            q = L @ np.array([p.X(), p.Y(), p.Z(), 1.0])
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


def transform_box(box, M):
    lo, hi = np.array(box[:3]), np.array(box[3:])
    cs = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    w = np.hstack([cs, np.ones((8, 1))]) @ M.T
    return [w[:, 0].min(), w[:, 1].min(), w[:, 2].min(), w[:, 0].max(), w[:, 1].max(), w[:, 2].max()]


def write_obj(path, V, F):
    with open(path, "w") as fh:
        fh.write("# mm, world frame\n")
        for p in V:
            fh.write("v %.4f %.4f %.4f\n" % (p[0], p[1], p[2]))
        for t in F:
            fh.write("f %d %d %d\n" % (t[0] + 1, t[1] + 1, t[2] + 1))


