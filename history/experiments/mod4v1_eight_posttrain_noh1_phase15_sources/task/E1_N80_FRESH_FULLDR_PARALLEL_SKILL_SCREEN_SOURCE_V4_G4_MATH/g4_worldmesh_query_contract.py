"""ExactoriginalG4mathfunctions only; unusedG3CADgenerator dependency excluded. FunctionAST unchanged."""
import numpy as np

def canonical_triangles(triangles):
    a = np.asarray(triangles, dtype=np.float32)
    order = np.lexsort((a[:, :, 2], a[:, :, 1], a[:, :, 0]), axis=1)
    a = a[np.arange(len(a))[:, None], order].reshape(-1, 9)
    return np.ascontiguousarray(a[np.lexsort(tuple(a[:, i] for i in range(8, -1, -1)))])

def downward_triangle_heights(triangles, starts):
    # Independent XY barycentric intersections, computed in float64.
    tri = np.asarray(triangles, dtype=np.float64)
    a = tri[:, 0]; b = tri[:, 1] - a; c = tri[:, 2] - a
    det = b[:, 0] * c[:, 1] - b[:, 1] * c[:, 0]
    assert np.all(np.abs(det) > 1e-12)
    out = []
    for point in np.asarray(starts, dtype=np.float64):
        d = point[:2] - a[:, :2]
        u = (d[:, 0] * c[:, 1] - d[:, 1] * c[:, 0]) / det
        v = (b[:, 0] * d[:, 1] - b[:, 1] * d[:, 0]) / det
        z = a[:, 2] + u * b[:, 2] + v * c[:, 2]
        hit = (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9)
        hit &= (z <= point[2]) & (z >= point[2] - 10.)
        assert hit.any(), 'Independent authored triangle ray miss'
        out.append(float(z[hit].max()))
    return np.asarray(out)
