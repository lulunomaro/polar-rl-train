"""Ground queries for the actual static terrain collider, before MOD4 Rough integration.

The CPU oracle is deliberately independent of Isaac/Warp and is for small audits.
The runtime path builds a Warp mesh from the same authored world-space triangles.
No analytic height map, RMUC fallback, or infinite ground plane is introduced.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np


@dataclass
class TerrainTriangles:
    vertices: np.ndarray
    faces: np.ndarray
    collider_paths: tuple[str, ...]

    def __post_init__(self):
        self.vertices = np.asarray(self.vertices, dtype=np.float64)
        self.faces = np.asarray(self.faces, dtype=np.int64)
        if self.vertices.ndim != 2 or self.vertices.shape[1] != 3:
            raise ValueError("Expected world-space vertices [V,3]")
        if self.faces.ndim != 2 or self.faces.shape[1] != 3 or len(self.faces) == 0:
            raise ValueError("Expected nonempty triangular faces [F,3]")
        if not np.isfinite(self.vertices).all():
            raise ValueError("Nonfinite terrain vertices")
        if self.faces.min() < 0 or self.faces.max() >= len(self.vertices):
            raise ValueError("Terrain face index outside vertex array")

    def receipt(self):
        return {
            "collider_paths": list(self.collider_paths),
            "vertices": len(self.vertices),
            "triangles": len(self.faces),
            "bounds_w": [self.vertices.min(0).tolist(), self.vertices.max(0).tolist()],
            "triangles_sha256": hashlib.sha256(
                self.vertices.astype("<f8").tobytes() + self.faces.astype("<i8").tobytes()
            ).hexdigest(),
        }

    @classmethod
    def from_stage(cls, stage, prim_root="/World/ground"):
        """Read enabled static Mesh colliders and their final USD world transforms.

        Reject approximated or dynamic meshes: their authored triangles would not
        identify the collision surface. A cooked PhysX comparison is still required
        before production, since authored geometry is not the contact manifold.
        """
        from pxr import Usd, UsdGeom, UsdPhysics

        if UsdGeom.GetStageUpAxis(stage) != UsdGeom.Tokens.z:
            raise ValueError("Terrain stage must use Z up")
        if abs(UsdGeom.GetStageMetersPerUnit(stage) - 1.0) > 1e-9:
            raise ValueError("Terrain stage must use metres")
        root = stage.GetPrimAtPath(prim_root)
        if not root or not root.IsValid():
            raise ValueError(f"Actual terrain prim absent: {prim_root}")
        cache = UsdGeom.XformCache()
        points, triangles, paths = [], [], []
        offset = 0
        for prim in Usd.PrimRange(root):
            if not prim.IsA(UsdGeom.Mesh) or not prim.HasAPI(UsdPhysics.CollisionAPI):
                continue
            if not UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Get():
                continue
            parent = prim
            while parent and parent.IsValid():
                if parent.HasAPI(UsdPhysics.RigidBodyAPI):
                    raise ValueError(f"Terrain collider belongs to a rigid body: {prim.GetPath()}")
                parent = parent.GetParent()
            if prim.HasAPI(UsdPhysics.MeshCollisionAPI):
                approximation = UsdPhysics.MeshCollisionAPI(prim).GetApproximationAttr().Get()
                if approximation not in (None, "none"):
                    raise ValueError(f"Terrain mesh approximation is {approximation}")
            mesh = UsdGeom.Mesh(prim)
            if mesh.GetHoleIndicesAttr().Get():
                raise ValueError("Mesh hole faces need explicit support")
            vertices = np.asarray(mesh.GetPointsAttr().Get(), dtype=np.float64)
            counts = np.asarray(mesh.GetFaceVertexCountsAttr().Get(), dtype=np.int64)
            indices = np.asarray(mesh.GetFaceVertexIndicesAttr().Get(), dtype=np.int64)
            if counts.sum() != len(indices) or np.any(counts < 3):
                raise ValueError("Invalid terrain polygon topology")
            # TerrainGenerator authors triangles. Reject arbitrary n-gons instead
            # of assuming a fan triangulation matches PhysX cooking.
            if np.any(counts != 3):
                raise ValueError("Terrain collider must be explicitly triangulated")
            faces = indices.reshape(-1, 3).copy()
            if mesh.GetOrientationAttr().Get() == UsdGeom.Tokens.leftHanded:
                faces = faces[:, [0, 2, 1]]
            tf = np.asarray(cache.GetLocalToWorldTransform(prim), dtype=np.float64)
            world = np.column_stack((vertices, np.ones(len(vertices)))) @ tf
            if not np.allclose(world[:, 3], 1.0):
                raise ValueError("Projective transform cannot be a terrain collider")
            points.append(world[:, :3])
            triangles.append(faces + offset)
            paths.append(str(prim.GetPath()))
            offset += len(vertices)
        if not paths:
            raise ValueError(f"No enabled triangular collider under {prim_root}")
        return cls(np.concatenate(points), np.concatenate(triangles), tuple(paths))


class VerticalMeshOracle:
    """Small CPU audit of downward rays, including discontinuities and ray misses."""

    def __init__(self, terrain: TerrainTriangles):
        self.terrain = terrain
        self.triangles = terrain.vertices[terrain.faces]

    def cast(self, starts, max_distance=10.0):
        starts = np.asarray(starts, dtype=np.float64)
        if starts.shape[-1] != 3 or not np.isfinite(starts).all() or max_distance <= 0:
            raise ValueError("Invalid downward ray")
        out_shape = starts.shape[:-1]
        heights = np.full(starts.reshape(-1, 3).shape[0], np.nan)
        normals = np.full((len(heights), 3), np.nan)
        face_ids = np.full(len(heights), -1, dtype=np.int64)
        a = self.triangles[:, 0]
        b = self.triangles[:, 1] - a
        c = self.triangles[:, 2] - a
        det = b[:, 0] * c[:, 1] - b[:, 1] * c[:, 0]
        valid = abs(det) > 1e-12  # Vertical walls do not define a downward height.
        normal = np.cross(b, c)
        normal /= np.maximum(np.linalg.norm(normal, axis=1, keepdims=True), 1e-30)
        for i, point in enumerate(starts.reshape(-1, 3)):
            d = point[:2] - a[:, :2]
            u = np.zeros(len(a)); v = np.zeros(len(a))
            u[valid] = (d[valid, 0] * c[valid, 1] - d[valid, 1] * c[valid, 0]) / det[valid]
            v[valid] = (b[valid, 0] * d[valid, 1] - b[valid, 1] * d[valid, 0]) / det[valid]
            z = a[:, 2] + u * b[:, 2] + v * c[:, 2]
            hit = valid & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9)
            hit &= (z <= point[2] + 1e-9) & (z >= point[2] - max_distance)
            candidates = np.flatnonzero(hit)
            if len(candidates):
                j = candidates[np.argmax(z[candidates])]
                heights[i] = z[j]; normals[i] = normal[j]; face_ids[i] = j
        return {
            "height": heights.reshape(out_shape),
            "normal": normals.reshape(out_shape + (3,)),
            "hit": (face_ids >= 0).reshape(out_shape),
            "face_id": face_ids.reshape(out_shape),
        }


class AuthoredTerrainRaycast:
    """GPU query bound only to terrain triangles from the live USD stage.

    Construct after scene spawning; callers must terminate/reject misses explicitly.
    This module does not replace production ground-height or reset functions yet.
    """

    def __init__(self, stage, device, prim_root="/World/ground"):
        from isaaclab.utils.warp import convert_to_warp_mesh
        self.geometry = TerrainTriangles.from_stage(stage, prim_root)
        self.mesh = convert_to_warp_mesh(self.geometry.vertices, self.geometry.faces, str(device))

    def cast(self, starts, max_distance=10.0):
        import torch
        from isaaclab.utils.warp import raycast_mesh
        if starts.ndim != 3 or starts.shape[-1] != 3:
            raise ValueError("SDK requires [environment,ray,xyz] starts")
        directions = torch.zeros_like(starts); directions[..., 2] = -1
        hits, distances, normals, faces = raycast_mesh(
            starts.contiguous(), directions, self.mesh, max_dist=max_distance,
            return_distance=True, return_normal=True, return_face_id=True,
        )
        return {"height": hits[..., 2], "normal": normals,
                "distance": distances, "face_id": faces,
                "hit": (faces >= 0) & torch.isfinite(hits).all(-1)}


def clear_vertical_placement(points_root, root_xy, yaw, terrain: VerticalMeshOracle,
                             clearance=0.002):
    """Audit a complete FK collision point cloud before writing a reset pose.

    Returns minimum root Z with every supplied collision point above terrain.
    It does not compute FK or guarantee stability on an edge. A complete USD/MJCF
    point cloud and independent closure, clearance and support checks remain needed.
    """
    points = np.asarray(points_root, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) == 0:
        raise ValueError("Reset requires a nonempty complete collision point cloud")
    if clearance < 0 or not np.isfinite(yaw):
        raise ValueError("Invalid reset clearance/yaw")
    c, s = np.cos(yaw), np.sin(yaw)
    rot = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    world_offsets = points @ rot.T
    xy = world_offsets[:, :2] + np.asarray(root_xy)
    ceiling = float(terrain.terrain.vertices[:, 2].max()) + 1.0
    starts = np.column_stack((xy, np.full(len(xy), ceiling)))
    distance = ceiling - float(terrain.terrain.vertices[:, 2].min()) + 1.0
    query = terrain.cast(starts, max_distance=distance)
    if not query["hit"].all():
        raise ValueError("Reset footprint extends outside actual terrain")
    if np.any(query["normal"][:, 2] <= 0):
        raise ValueError("Reset hits back-facing/underside terrain")
    z = float(np.max(query["height"] + clearance - world_offsets[:, 2]))
    gaps = z + world_offsets[:, 2] - query["height"]
    return {"root_z": z, "minimum_point_clearance": float(gaps.min()),
            "maximum_point_clearance": float(gaps.max())}
