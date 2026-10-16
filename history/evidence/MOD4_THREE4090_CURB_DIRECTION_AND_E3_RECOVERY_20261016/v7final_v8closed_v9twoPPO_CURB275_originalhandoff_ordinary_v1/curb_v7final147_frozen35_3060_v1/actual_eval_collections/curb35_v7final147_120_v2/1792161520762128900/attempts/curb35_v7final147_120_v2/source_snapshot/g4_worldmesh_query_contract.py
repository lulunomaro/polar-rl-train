"""Independent CPU triangle expectation bound to the actual float32 authored mesh.

No GPU hit/face/height is used to choose or calculate the expected surface.
Actual triangles must first match every procedural triangle byte for byte.
"""
import hashlib
import numpy as np
from g3_cad_wave_geometry import make_mesh


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


def expected_ground(actual_vertices, actual_faces, centers, actual_starts):
    mesh, _ = make_mesh((9., 9.))
    source = np.asarray(mesh.vertices, dtype=np.float64).copy()
    source[:, :2] -= 4.5
    source_faces = np.asarray(mesh.faces, dtype=np.int64)
    actual_tri = np.asarray(actual_vertices, dtype=np.float32)[actual_faces]
    centroids = actual_tri.astype(np.float64).mean(axis=1)
    expected = []; receipts = []; evidence = []
    for center, starts in zip(centers, actual_starts):
        # TerrainGenerator centers each cell and then the complete grid before USD
        # authors float32 points; Warp consumes those same float32 world vertices.
        predicted = source.copy(); predicted[:, :2] += center
        predicted = predicted.astype(np.float32)[source_faces]
        pick = np.all(np.abs(centroids[:, :2] - center) < 4.5, axis=1)
        selected = actual_tri[pick]
        lhs = canonical_triangles(selected); rhs = canonical_triangles(predicted)
        assert np.array_equal(lhs, rhs), 'Actual world triangles differ from procedural float32 cell identity'
        expected.append(downward_triangle_heights(predicted, starts))
        evidence.append(selected)
        receipts.append(dict(triangles=len(selected), actual_SHA=hashlib.sha256(lhs.tobytes()).hexdigest(),
                             expected_SHA=hashlib.sha256(rhs.tobytes()).hexdigest(), byteexact=True))
    return np.asarray(expected), receipts, np.stack(evidence)
