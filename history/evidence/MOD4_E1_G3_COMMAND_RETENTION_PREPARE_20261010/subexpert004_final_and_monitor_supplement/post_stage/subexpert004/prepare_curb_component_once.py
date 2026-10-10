"""New CPU-only curb preparation under approved revision004; never launches GPU."""
from pathlib import Path
import hashlib, json, sys, time, traceback
import numpy as np

D = Path(__file__).resolve().parent
R = D / 'reports'
G = D / 'next_curb_cpu'
sys.path.insert(0, str(G))
import curb20_component as c


def save(path, obj):
    assert not path.exists(), str(path)
    path.write_bytes(json.dumps(obj, ensure_ascii=False, indent=2).encode())


def ray(origin, direction, vertices, faces):
    """Independent Moller-Trumbore ray intersections with authored triangles."""
    hits = []
    for face in faces:
        a, b, z = vertices[face]
        e1, e2 = b - a, z - a
        p = np.cross(direction, e2)
        det = np.dot(e1, p)
        if abs(det) < 1e-12:
            continue
        s = origin - a
        u = np.dot(s, p) / det
        q = np.cross(s, e1)
        v = np.dot(direction, q) / det
        t = np.dot(e2, q) / det
        if u >= -1e-12 and v >= -1e-12 and u + v <= 1 + 1e-12 and t >= 0:
            hits.append(float(t))
    assert hits
    return origin + min(hits) * direction


def main():
    assert json.loads((R / 'REVISION_APPROVED.json').read_bytes())['approved']
    save(R / 'CURB20_CPU_PREPARE_STARTED.json', dict(epoch=time.time(),
        trial_id='E1-CURB20-DERIVED-CPU-GEOMETRY-01', CPU_only=True,
        no_GPU_PPO_queue_remote_signal_or_canonical_write=True))
    vertices, faces = c.mesh()
    assert np.isfinite(vertices).all()
    triangles = vertices[faces]
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    assert (np.linalg.norm(cross, axis=1) > 0).all()
    top = np.isclose(np.ptp(triangles[:, :, 2], axis=1), 0)
    assert (cross[top, 2] > 0).all()
    # Regular rays and exact joins are compared against the separate step oracle.
    samples = [(float(x), float(y)) for x in np.linspace(-4.4, 4.4, 21)
               for y in np.linspace(-4.3, 4.3, 11)]
    samples += [(c.EDGE_X_M, 0), (.075, 0), (c.EDGE_X_M - 1e-8, 0),
                (c.EDGE_X_M + 1e-8, 0)]
    errors = []
    for x, y in samples:
        hit = ray(np.array([x, y, 1.]), np.array([0., 0., -1.]), vertices, faces)
        errors.append(abs(float(hit[2]) - float(c.height(x, y))))
    assert max(errors) < 1e-10
    wall = ray(np.array([-1., 0., .010]), np.array([1., 0., 0.]), vertices, faces)
    assert abs(wall[0] - c.EDGE_X_M) < 1e-10 and wall[2] == .010
    mv, mf = c.mirrored_mesh()
    mirror_errors = []
    for x, y in samples:
        hit = ray(np.array([-x, y, 1.]), np.array([0., 0., -1.]), mv, mf)
        mirror_errors.append(abs(float(hit[2]) - float(c.height(x, y))))
    assert max(mirror_errors) < 1e-10
    geometry = dict(schema='derived_vertical_curb20_strip150_cpu_component_v1',
        derived_not_actual_RM_geometry=True, actual_RM002_heights_not_replaced=True,
        height_m=c.HEIGHT_M, strip_width_m=c.STRIP_WIDTH_M, tile_size_m=c.TILE_SIZE_M,
        edge_x_m=c.EDGE_X_M, lower_support_z_m=0., upper_platform_z_m=.020,
        strip_continuous_with_upper_platform=True, vertical_riser_unsmoothed=True,
        vertices=vertices.tolist(), triangles=faces.tolist(), mirrored_available=True,
        not_stair_flight=True, not_physical_traversal_pass=True)
    save(G / 'curb20_profile.json', geometry)
    save(R / 'CURB20_CPU_COMPONENT_REVIEW.json', dict(epoch=time.time(),
        trial_id='E1-CURB20-DERIVED-CPU-GEOMETRY-01', CPU_component_passed=True,
        independent_triangle_rays=len(samples), max_vertical_ray_error_m=max(errors),
        mirrored_ray_error_m=max(mirror_errors), actual_vertical_wall_hit=wall.tolist(),
        geometry=geometry, source=dict(path=str(G / 'curb20_component.py'),
        bytes=(G / 'curb20_component.py').stat().st_size,
        sha256=hashlib.sha256((G / 'curb20_component.py').read_bytes()).hexdigest()),
        undeployed=True, SDK_native_CUDA_fullsave_fullresume_PPO_pending=True,
        no_GPU_PPO_queue_signal_or_canonical_write=True, new_budget_seconds=0))
    print(json.dumps(dict(CPU_component_passed=True, independent_triangle_rays=len(samples),
        max_vertical_ray_error_m=max(errors), mirrored_ray_error_m=max(mirror_errors),
        undeployed=True, no_physical_pass_claim=True, new_budget_seconds=0)))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        save(R / 'CURB20_CPU_PREPARE_ERROR.json', dict(epoch=time.time(),
            trial_id='E1-CURB20-DERIVED-CPU-GEOMETRY-01', error=traceback.format_exc(),
            no_production_mutation=True, original_error_retained=True))
        raise
