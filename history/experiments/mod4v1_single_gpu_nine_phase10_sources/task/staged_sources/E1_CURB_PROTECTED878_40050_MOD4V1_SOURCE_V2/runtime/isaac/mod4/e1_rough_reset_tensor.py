"""Full-pose placement math for an isolated, sampled-surface rough reset.

This is not a continuous collider penetration test or a training reset approval.
All 30 joints are written, including wheels, passive links, mimics and rollers.
"""
import numpy as np

def tangent_frame(normal, heading=0.):
    z = np.asarray(normal, dtype=np.float64)
    if z.shape != (3,) or not np.isfinite(z).all() or np.linalg.norm(z) < 1e-8 or z[2] <= 0:
        raise ValueError('Missing or downward terrain normal')
    z = z / np.linalg.norm(z)
    x = np.array([np.cos(heading), np.sin(heading), 0.])
    x -= z * np.dot(x, z)
    if np.linalg.norm(x) < 1e-8:
        raise ValueError('Degenerate tangent direction')
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    frame = np.column_stack((x, y, z))
    assert np.allclose(frame.T @ frame, np.eye(3), atol=1e-12)
    assert np.linalg.det(frame) > .999999
    return frame

def joint_permutation(bank_names, robot_names):
    if len(bank_names) != 30 or len(robot_names) != 30 or len(set(bank_names)) != 30 or set(bank_names) != set(robot_names):
        raise ValueError('Require the exact complete 30-joint plant')
    return np.array([list(bank_names).index(n) for n in robot_names], dtype=np.int64)

def sampled_vertical_placement(offsets, terrain_heights, hit, clearance=.002):
    offsets = np.asarray(offsets, dtype=np.float64)
    heights = np.asarray(terrain_heights, dtype=np.float64)
    hit = np.asarray(hit, dtype=bool)
    if offsets.ndim != 2 or offsets.shape[1] != 3 or heights.shape != offsets.shape[:1] or hit.shape != heights.shape:
        raise ValueError('Incomplete footprint geometry')
    if not np.isfinite(offsets).all() or not np.isfinite(heights).all() or not hit.all() or clearance < 0:
        raise ValueError('Missing/nonfinite terrain; no cached-floor fallback')
    z = np.max(heights + clearance - offsets[:, 2])
    return float(z), z + offsets[:, 2] - heights

def cpu_contract():
    tests = 0
    for slope in (-.15, 0., .15):
        frame = tangent_frame([-slope, 0., 1.])
        assert np.allclose(frame[:, 2], np.array([-slope, 0., 1.]) / np.linalg.norm([-slope, 0., 1.]))
        assert np.allclose(frame @ frame.T, np.eye(3))
        tests += 1
    names = ['j' + str(i) for i in range(30)]
    assert list(joint_permutation(names, names[::-1])) == list(range(29, -1, -1)); tests += 1
    points = np.array([[0., 0., -.25], [.2, 0., -.2], [-.2, .2, -.2]])
    z, gaps = sampled_vertical_placement(points, np.zeros(3), np.ones(3, bool))
    assert abs(z - .252) < 1e-12 and gaps.min() >= .002 - 1e-12; tests += 1
    z, gaps = sampled_vertical_placement(points, np.array([0., .12, .01]), np.ones(3, bool))
    assert abs(z - .322) < 1e-12 and gaps.min() >= .002 - 1e-12; tests += 1
    for call in (lambda: tangent_frame([0., 0., -1.]), lambda: tangent_frame([np.nan, 0., 1.]),
                 lambda: joint_permutation(names[:29], names), lambda: joint_permutation(names, names[:-1] + ['other']),
                 lambda: sampled_vertical_placement(points, np.zeros(3), [True, False, True]),
                 lambda: sampled_vertical_placement(points, [0., np.nan, 0.], [True] * 3)):
        try:
            call()
        except ValueError:
            tests += 1
        else:
            raise AssertionError('Expected missing/model/miss rejection')
    return dict(pass_=True, meaningful_contracts=tests, no_simulation=True, training_reset_approved=False)

if __name__ == '__main__':
    import json
    print(json.dumps(cpu_contract()))
