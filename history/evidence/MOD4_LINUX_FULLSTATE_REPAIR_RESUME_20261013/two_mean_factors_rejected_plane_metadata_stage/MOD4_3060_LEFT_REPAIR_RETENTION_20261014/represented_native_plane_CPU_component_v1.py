"""CPU-only represented Plane reference; never imports Kit or derives a plane from hits.

This is a source-backed preparation component, not proof of the installed binary.
The input actor pose must come from the actual readonly PhysX getter.  The current
scope is a standalone USD Plane collider, with no RigidBodyAPI ancestor.  Its
actor gets the authored world pose, while the axis fixup is shape-local.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import numpy as np

SOURCE_COMMIT = "517a0073715120e114ee055b63b26c95e00d9039"
SOURCE_ROOT = Path(__file__).parent / "source_reference_1101"
SOURCE_FILES = (
    "Collision.cpp", "UsdInterface.cpp", "PhysX.cpp", "TypeCast.h",
    "NpShape.cpp", "PxTransform.h", "PxQuat.h", "GuInternal.cpp",
    "GuRaycastTests.cpp", "GuIntersectionRayPlane.h",
)
F = np.float32
TOLERANCE_M = 1e-6


def source_sha_manifest():
    return {name: hashlib.sha256((SOURCE_ROOT / name).read_bytes()).hexdigest()
            for name in SOURCE_FILES}


def finite_vector(value, count):
    a = np.asarray(value, dtype=np.float32)
    if a.shape != (count,) or not np.isfinite(a).all():
        raise ValueError("wrong shape or nonfinite metadata")
    return a


def normalize_quaternion(q):
    # PxQuatT::magnitudeSquared/getNormalized, explicit scalar float32 order.
    x, y, z, w = finite_vector(q, 4)
    squared = F(F(F(F(x*x) + F(y*y)) + F(z*z)) + F(w*w))
    if squared <= 0:
        raise ValueError("zero quaternion")
    magnitude = F(np.sqrt(squared))
    scale = F(F(1) / magnitude)
    return np.asarray([F(x*scale), F(y*scale), F(z*scale), F(w*scale)], dtype=np.float32)


def quaternion_multiply(a, b):
    # PxQuatT::operator*(const PxQuatT&), x/y/z/w constructor order.
    x, y, z, w = finite_vector(a, 4)
    X, Y, Z, W = finite_vector(b, 4)
    return np.asarray([
        F(F(F(F(w*X) + F(W*x)) + F(y*Z)) - F(Y*z)),
        F(F(F(F(w*Y) + F(W*y)) + F(z*X)) - F(Z*x)),
        F(F(F(F(w*Z) + F(W*z)) + F(x*Y)) - F(X*y)),
        F(F(F(F(w*W) - F(x*X)) - F(y*Y)) - F(z*Z)),
    ], dtype=np.float32)


def basis_vector_zero(q):
    # PxQuatT::getBasisVector0, which Gu::getPlane actually uses.
    x, y, z, w = finite_vector(q, 4)
    x2, w2 = F(x*F(2)), F(w*F(2))
    return np.asarray([
        F(F(F(w*w2) - F(1)) + F(x*x2)),
        F(F(z*w2) + F(y*x2)),
        F(F(-y*w2) + F(z*x2)),
    ], dtype=np.float32)


def dot3(a, b):
    a, b = finite_vector(a, 3), finite_vector(b, 3)
    return F(F(F(a[0]*b[0]) + F(a[1]*b[1])) + F(a[2]*b[2]))


def represented_plane_from_readonly_metadata(metadata):
    """No query-hit input, ideal-height fallback, mutation, cache flush, or draw.

    source_file_sha256 is the frozen reviewed public-source identity, not a claim
    that the installed DLL has the same compiled arithmetic. A separate future
    actual stage must establish binary/build and actual getter identities.
    """
    if metadata["source_commit"] != SOURCE_COMMIT:
        raise ValueError("wrong source commit")
    if metadata["source_file_sha256"] != source_sha_manifest():
        raise ValueError("wrong source bytes")
    plane = metadata["actual_USD_plane"]
    if plane["type"] != "Plane" or not plane["CollisionAPI"]:
        raise ValueError("wrong geometry or missing collision API")
    if plane["RigidBodyAPI_ancestor_paths"]:
        raise ValueError("only standalone static Plane scope reviewed")
    if plane["axis"] != metadata["approved_axis"] or plane["axis"] not in ("X", "Y", "Z"):
        raise ValueError("wrong or unsupported axis")
    actor = metadata["actual_actor_getter"]
    if actor["path"] != plane["path"] or actor["ret_val"] is not True:
        raise ValueError("actual standalone actor not identified")
    position = finite_vector(actor["position"], 3)
    rotation = finite_vector(actor["rotation_xyzw"], 4)
    usd_position = finite_vector(plane["world_position"], 3)
    usd_rotation = normalize_quaternion(plane["world_rotation_xyzw"])
    # Standalone source createShape puts the USD world pose on the static actor.
    # Current identity ground admits exact sign-equivalent quaternion. No new
    # positional/rotation tolerance is introduced here.
    if not np.array_equal(position, usd_position):
        raise ValueError("actor translation differs from independent USD world pose")
    if not (np.array_equal(rotation, usd_rotation) or np.array_equal(rotation, -usd_rotation)):
        raise ValueError("actor rotation differs from independent USD world pose")
    h = F(F(np.sqrt(F(2))) / F(2))
    if plane["axis"] == "X":
        fixup = np.asarray([0, 0, 0, 1], dtype=np.float32)
    elif plane["axis"] == "Y":
        fixup = np.asarray([h, h, 0, 0], dtype=np.float32)
    else:
        fixup = np.asarray([h, 0, h, 0], dtype=np.float32)
    # NpShape::setLocalPose normalizes after the Omni axis fixup is assigned.
    local_rotation = normalize_quaternion(fixup)
    world_rotation = quaternion_multiply(rotation, local_rotation)
    normal = basis_vector_zero(world_rotation)
    # Standalone local translation is explicitly reset to zero by source, so
    # actual shape world position is actor position. d is always computed.
    offset = F(-dot3(position, normal))
    return {
        "status": "CPU_source_reference_only_actual_binary_and_shape_pose_pending",
        "path": plane["path"], "axis": plane["axis"],
        "actor_position": position.tolist(), "actor_rotation_xyzw": rotation.tolist(),
        "shape_local_position_source": [0.0, 0.0, 0.0],
        "fixup_before_normalization_xyzw": fixup.tolist(),
        "normalized_shape_local_rotation_xyzw": local_rotation.tolist(),
        "shape_world_rotation_xyzw": world_rotation.tolist(),
        "represented_plane_normal": normal.tolist(),
        "represented_plane_offset_d": float(offset),
        "expected_from_query_hits": False,
        "actual_shape_local_pose_read": False,
    }


def compare_actual_hit_readonly(reference, hit):
    """Compare representation; preserve the original authored-height verdict.

    This comparison cannot promote a failed full case. reported normal is only a
    diagnostic crosscheck, never used to calculate either expected height or d.
    """
    n = np.asarray(reference["represented_plane_normal"], dtype=np.float64)
    d = float(reference["represented_plane_offset_d"])
    p = np.asarray(hit["position"], dtype=np.float64)
    if p.shape != (3,) or not np.isfinite(p).all() or abs(n[2]) <= 0:
        raise ValueError("invalid height query")
    height = -(n[0]*p[0] + n[1]*p[1] + d) / n[2]
    error = abs(float(p[2]) - float(height))
    reported_n = np.asarray(hit["normal"], dtype=np.float64)
    return dict(expected_represented_height=float(height), actual_hit_height=float(p[2]),
                represented_query_error_m=error,
                represented_query_within_original_1e6=bool(error <= TOLERANCE_M),
                normal_crosscheck_maxabs=float(np.max(np.abs(reported_n-n))),
                no_original_case_PASS_from_this_component=True)


def raycast_source_float32(reference, origin, direction):
    """Diagnostic source operation reconstruction; never a query fallback."""
    n = finite_vector(reference["represented_plane_normal"], 3)
    o, v = finite_vector(origin, 3), finite_vector(direction, 3)
    d = F(reference["represented_plane_offset_d"])
    denominator = dot3(v, n)
    if abs(float(denominator)) < 1e-7:
        raise ValueError("parallel ray")
    distance = F(-F(dot3(o, n)+d) / denominator)
    hit_position = np.asarray([F(o[i]+F(distance*v[i])) for i in range(3)], dtype=np.float32)
    return dict(distance=float(distance), position=hit_position.tolist())
