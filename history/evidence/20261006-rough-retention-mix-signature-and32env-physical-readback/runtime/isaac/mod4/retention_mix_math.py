"""Explicit finite geometry and environment groups for retention repair.

These groups separate old flat skills from the already declared gentle terrain.
They are a training exposure choice, not a skill completion threshold.
"""
import numpy as np
import torch

FLAT_SHIFT_X = 768.0
FLAT_HALF_EXTENT = 384.0
FLAT_ROUTE_LIMIT = 48.0
ROUGH_ROUTE_LIMIT = 2.0


def rough_mask(ids):
    return ids.remainder(4) == 3


def spawn_xy(origins, ids):
    xy = origins[ids, :2].clone()
    xy[:, 0] += (~rough_mask(ids)).to(xy.dtype) * FLAT_SHIFT_X
    return xy


def route_timeout(xy, anchor, ids):
    limit = torch.where(rough_mask(ids), ROUGH_ROUTE_LIMIT, FLAT_ROUTE_LIMIT)
    return (xy - anchor).abs().amax(-1) > limit


def flat_surface():
    # Declared finite Mesh, separated from the rough collider. No hidden Plane.
    vertices = np.array([
        [FLAT_SHIFT_X - FLAT_HALF_EXTENT, -FLAT_HALF_EXTENT, 0.],
        [FLAT_SHIFT_X + FLAT_HALF_EXTENT, -FLAT_HALF_EXTENT, 0.],
        [FLAT_SHIFT_X + FLAT_HALF_EXTENT, FLAT_HALF_EXTENT, 0.],
        [FLAT_SHIFT_X - FLAT_HALF_EXTENT, FLAT_HALF_EXTENT, 0.],
    ], dtype=np.float64)
    faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int64)
    return vertices, faces


def assert_surface_separation(rough_vertices):
    points = np.asarray(rough_vertices)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError('Invalid authored rough geometry')
    if float(points[:, 0].max()) >= FLAT_SHIFT_X - FLAT_HALF_EXTENT:
        raise ValueError('Declared rough and retained-flat surfaces overlap')
