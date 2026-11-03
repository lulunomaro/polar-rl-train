"""Private compiled-shape support; reads cached transforms, never forwards/steps.
Not sensor observations, a collision test, contact-margin support, or permission.
Compiled mesh vertices already include scale/centering/PCA: transform ONCE.
"""
from dataclasses import dataclass
import math
import numpy as np

TYPE_NAMES = {2: 'sphere', 3: 'capsule', 4: 'ellipsoid', 5: 'cylinder',
              6: 'box', 7: 'mesh_compiled_vertex_hull'}
PAD_M = 1e-8
ROT_BUDGET = 1e-8


def _v3(value, label):
    a = np.asarray(value, dtype=float)
    if a.shape != (3,) or not np.isfinite(a).all():
        raise ValueError(label + ' requires three finite scalars')
    return a


def shape_bounds(typ, size, rotation, position, vertices=None):
    """Raw float64 extrema of a finite compiled primitive/hull, no padding.
    Returns independent arrays. Mesh support equals support of its vertex hull;
    this is not evidence of mesh intersection, bearing, or solver contact.
    """
    typ = int(typ)
    if typ not in TYPE_NAMES:
        raise ValueError('Unbound finite collision type ' + str(typ))
    size = _v3(size, 'size')
    p = _v3(position, 'position')
    R = np.asarray(rotation, dtype=float)
    if R.shape != (3, 3) or not np.isfinite(R).all():
        raise ValueError('rotation requires a finite 3x3 matrix')
    if (np.max(np.abs(R.T @ R - np.eye(3))) > ROT_BUDGET
            or abs(float(np.linalg.det(R)) - 1.) > ROT_BUDGET):
        raise ValueError('non-rotation cached transform')
    if typ == 7:
        v = np.asarray(vertices, dtype=float)
        if v.ndim != 2 or v.shape[1] != 3 or len(v) < 4 or not np.isfinite(v).all():
            raise ValueError('invalid compiled mesh vertices')
        w = v @ R.T + p
        return w.min(axis=0), w.max(axis=0)
    needed = size[:1] if typ == 2 else size[:2] if typ in (3, 5) else size
    if np.any(needed <= 0):
        raise ValueError('nonpositive finite primitive size')
    if typ == 2:
        ext = np.full(3, size[0])
    elif typ == 3:
        ext = size[0] + size[1] * np.abs(R[:, 2])
    elif typ == 4:
        ext = np.linalg.norm(R * size[None, :], axis=1)
    elif typ == 5:
        ext = size[0] * np.hypot(R[:, 0], R[:, 1]) + size[1] * np.abs(R[:, 2])
    else:
        ext = np.abs(R) @ size
    return p - ext, p + ext


@dataclass(frozen=True)
class _Geom:
    gid: int
    name: str
    typ: int
    size: np.ndarray
    vertices: object
    old_radius: float
    contact_margin: float


class CompiledCollisionSupport:
    """Model-bound immutable local cache; rebuild after GEOMETRY changes.
    Selection intentionally matches existing grade_rows exactly: all non-world
    geoms with either contact mask set OR participation in an explicit pair.
    In current scenes every non-world body belongs to the robot. This is NOT a
    general multi-robot selector; caller must not silently reuse in other scenes.
    """
    def __init__(self, model):
        explicit = np.isin(np.arange(model.ngeom),
                           np.r_[model.pair_geom1, model.pair_geom2])
        ids = np.flatnonzero((model.geom_bodyid > 0)
                            & ((model.geom_contype != 0)
                               | (model.geom_conaffinity != 0) | explicit))
        if not len(ids):
            raise ValueError('no selected non-world collision geometry')
        self.ngeom = int(model.ngeom)
        rows = []
        for i in ids:
            gid = int(i)
            typ = int(model.geom_type[gid])
            if typ not in TYPE_NAMES:
                raise ValueError('Unbound finite collision type ' + str(typ))
            size = _v3(model.geom_size[gid], 'model geom_size').copy()
            size.setflags(write=False)
            vertices = None
            if typ == 7:
                mid = int(model.geom_dataid[gid])
                if mid < 0:
                    raise ValueError('mesh geom without mesh id')
                adr, n = int(model.mesh_vertadr[mid]), int(model.mesh_vertnum[mid])
                vertices = np.asarray(model.mesh_vert[adr:adr+n], dtype=float).copy()
                vertices.setflags(write=False)
            # Validate supported local shape and radius before accepting cache.
            lo, hi = shape_bounds(typ, size, np.eye(3), np.zeros(3), vertices)
            radius = float(model.geom_rbound[gid])
            margin = float(model.geom_margin[gid])
            if not math.isfinite(radius) or radius <= 0 or not math.isfinite(margin):
                raise ValueError('non-finite radius or contact margin')
            if typ == 7:
                need = float(np.linalg.norm(vertices, axis=1).max())
            elif typ == 2:
                need = float(size[0])
            elif typ == 3:
                need = float(size[0] + size[1])
            elif typ == 4:
                need = float(size.max())
            elif typ == 5:
                need = float(np.linalg.norm(size[:2]))
            else:
                need = float(np.linalg.norm(size))
            if need > radius + PAD_M:
                raise ValueError('compiled shape exceeds original radius certificate')
            rows.append(_Geom(gid, str(model.geom(gid).name), typ, size, vertices,
                              radius + PAD_M, margin))
        self.geoms = tuple(rows)
        self.geom_ids = tuple(g.gid for g in rows)

    def bounds(self, data, *, stage_time_s):
        if not math.isfinite(stage_time_s) or stage_time_s < 0:
            raise ValueError('invalid caller-declared cached stage time')
        xp, xm = np.asarray(data.geom_xpos), np.asarray(data.geom_xmat)
        if xp.shape != (self.ngeom, 3) or xm.shape != (self.ngeom, 9):
            raise ValueError('data/model geometry dimensions differ')
        per, lows, highs = [], [], []
        sphere_lows, sphere_highs = [], []
        for g in self.geoms:
            p = _v3(xp[g.gid], 'cached geom position')
            lo, hi = shape_bounds(g.typ, g.size, xm[g.gid].reshape(3, 3), p, g.vertices)
            lows.append(lo); highs.append(hi)
            sphere_lows.append(p - g.old_radius)
            sphere_highs.append(p + g.old_radius)
            per.append({'geom_id': g.gid, 'geom_name': g.name,
                        'compiled_type': TYPE_NAMES[g.typ],
                        'min_xyz_m': lo.tolist(), 'max_xyz_m': hi.tolist(),
                        'geom_contact_margin_m_NOT_INCLUDED': g.contact_margin})
        low, high = np.asarray(lows), np.asarray(highs)
        lo, hi = low.min(axis=0), high.max(axis=0)
        arglo, arghi = low.argmin(axis=0), high.argmax(axis=0)
        return {'kind': 'PRIVATE_COMPILED_DIRECTIONAL_GEOMETRY_SUPPORT_V1',
                'stage_time_s': float(stage_time_s), 'collision_geoms': len(per),
                'selection': 'legacy_nonworld_mask_OR_explicit_pair',
                'raw_min_xyz_m': lo.tolist(), 'raw_max_xyz_m': hi.tolist(),
                'outward_padded_min_xyz_m': (lo-PAD_M).tolist(),
                'outward_padded_max_xyz_m': (hi+PAD_M).tolist(),
                'numeric_padding_m': PAD_M,
                'argmin_geoms_xyz': [per[int(i)]['geom_name'] for i in arglo],
                'argmin_geom_ids_xyz': [per[int(i)]['geom_id'] for i in arglo],
                'argmax_geoms_xyz': [per[int(i)]['geom_name'] for i in arghi],
                'argmax_geom_ids_xyz': [per[int(i)]['geom_id'] for i in arghi],
                'legacy_sphere_min_xyz_m': np.min(sphere_lows, axis=0).tolist(),
                'legacy_sphere_max_xyz_m': np.max(sphere_highs, axis=0).tolist(),
                'per_geom': per,
                'contact_margin_included': False,
                'not_formal_interval_or_contact_or_stability_proof': True,
                'controller_input': False, 'changes_old_acceptance': False}
